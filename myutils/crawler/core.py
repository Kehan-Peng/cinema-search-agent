from __future__ import annotations

import csv
import json
import os
import random
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import requests


DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
]

BASE_DIR = Path(__file__).resolve().parents[2]
CRAWLER_DIR = BASE_DIR / "runtime" / "crawler"
CHECKPOINT_DIR = CRAWLER_DIR / "checkpoints"
STATUS_FILE = CRAWLER_DIR / "crawler_status.json"


@dataclass
class CrawlConfig:
    min_delay: float = 5.0
    max_delay: float = 10.0
    timeout: int = 30
    retries: int = 6
    user_agents: Optional[List[str]] = None
    proxy_file: Optional[Path] = None

    @classmethod
    def from_env(cls) -> "CrawlConfig":
        proxy_path = os.getenv("DOUBAN_PROXY_FILE")
        return cls(
            min_delay=float(os.getenv("DOUBAN_MIN_DELAY", "5.0")),
            max_delay=float(os.getenv("DOUBAN_MAX_DELAY", "10.0")),
            timeout=int(os.getenv("DOUBAN_TIMEOUT", "30")),
            retries=int(os.getenv("DOUBAN_RETRIES", "6")),
            user_agents=DEFAULT_USER_AGENTS,
            proxy_file=Path(proxy_path) if proxy_path else None,
        )


def _ensure_runtime_dirs() -> None:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_proxy_pool(proxy_file: Optional[Path]) -> List[str]:
    if not proxy_file or not proxy_file.exists():
        return []
    return [line.strip() for line in proxy_file.read_text(encoding="utf-8").splitlines() if line.strip()]


def _normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def clean_movie_record(record: Dict) -> Dict:
    cleaned = dict(record)
    cleaned["title"] = _normalize_whitespace(cleaned.get("title", ""))
    cleaned["genre"] = "/".join(
        sorted({item.strip() for item in str(cleaned.get("genre", "")).replace(",", "/").split("/") if item.strip()})
    )
    cleaned["summary"] = _normalize_whitespace(cleaned.get("summary", ""))
    cleaned["country"] = "/".join(
        item.strip() for item in str(cleaned.get("country", "")).replace(",", "/").split("/") if item.strip()
    )
    cleaned["directors"] = "/".join(
        item.strip() for item in str(cleaned.get("directors", "")).replace(",", "/").split("/") if item.strip()
    )
    cleaned["duration"] = int(cleaned.get("duration") or 0)
    cleaned["release_year"] = int(cleaned.get("release_year") or 0)
    cleaned["rating"] = float(cleaned.get("rating") or 0)
    cleaned["subject_id"] = str(cleaned.get("subject_id") or "")
    cleaned["comment_len"] = int(cleaned.get("comment_len") or 0)
    return cleaned


def dedupe_records(records: Sequence[Dict], key_fields: Sequence[str]) -> List[Dict]:
    merged = {}
    for item in records:
        key = tuple(str(item.get(field) or "") for field in key_fields)
        if not any(key):
            continue
        merged[key] = item
    return list(merged.values())


def write_csv(path: Path, rows: Sequence[Dict], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def merge_csv_rows(path: Path, incoming_rows: Sequence[Dict], key_fields: Sequence[str], fieldnames: Sequence[str]) -> List[Dict]:
    existing = []
    if path.exists():
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            existing = list(csv.DictReader(csv_file))
    merged = dedupe_records(existing + list(incoming_rows), key_fields)
    write_csv(path, merged, fieldnames)
    return merged


def load_checkpoint(name: str) -> Dict:
    _ensure_runtime_dirs()
    checkpoint_path = CHECKPOINT_DIR / f"{name}.json"
    if not checkpoint_path.exists():
        return {}
    return json.loads(checkpoint_path.read_text(encoding="utf-8"))


def save_checkpoint(name: str, payload: Dict) -> None:
    _ensure_runtime_dirs()
    checkpoint_path = CHECKPOINT_DIR / f"{name}.json"
    checkpoint_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def update_crawler_status(job_name: str, payload: Dict) -> None:
    _ensure_runtime_dirs()
    status = {}
    if STATUS_FILE.exists():
        status = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    status[job_name] = {
        **payload,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    STATUS_FILE.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")


class DoubanHttpClient:
    def __init__(self, config: Optional[CrawlConfig] = None) -> None:
        self.config = config or CrawlConfig.from_env()
        self.session = requests.Session()
        self.proxy_pool = _load_proxy_pool(self.config.proxy_file)
        self.request_count = 0
        self.last_request_time = 0.0
        # 初始化cookies以模拟真实浏览器
        self._init_cookies()

    def _init_cookies(self) -> None:
        """初始化cookies以模拟真实浏览器会话"""
        # 设置基础cookies
        self.session.cookies.set('bid', self._generate_bid(), domain='.douban.com')
        self.session.cookies.set('ll', '"108288"', domain='.douban.com')

    def _generate_bid(self) -> str:
        """生成随机的bid cookie"""
        import string
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(11))

    def _headers(self, url: str) -> Dict[str, str]:
        """根据URL动态生成请求头"""
        user_agents = self.config.user_agents or DEFAULT_USER_AGENTS

        # 基础请求头
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "DNT": "1",
        }

        # 如果不是第一次请求，添加Referer
        if self.request_count > 0:
            headers["Referer"] = "https://movie.douban.com/top250"
        else:
            headers["Sec-Fetch-Site"] = "none"

        return headers

    def _proxies(self) -> Optional[Dict[str, str]]:
        if not self.proxy_pool:
            return None
        proxy = random.choice(self.proxy_pool)
        return {"http": proxy, "https": proxy}

    def _adaptive_delay(self) -> None:
        """自适应延迟策略"""
        self.request_count += 1

        # 基础延迟
        base_delay = random.uniform(self.config.min_delay, self.config.max_delay)

        # 每3个请求增加额外延迟
        if self.request_count % 3 == 0:
            base_delay += random.uniform(3.0, 6.0)

        # 每5个请求增加更长延迟
        if self.request_count % 5 == 0:
            base_delay += random.uniform(8.0, 12.0)

        time.sleep(base_delay)

    def get_html(self, url: str) -> str:
        last_error = None
        retry_delay = self.config.min_delay

        for attempt in range(max(self.config.retries, 1)):
            try:
                # 每次重试时重新初始化session和cookies
                if attempt > 0:
                    self.session = requests.Session()
                    self._init_cookies()
                    # 重试时增加更长的延迟
                    time.sleep(random.uniform(10.0, 20.0))

                response = self.session.get(
                    url,
                    headers=self._headers(url),
                    timeout=self.config.timeout,
                    proxies=self._proxies(),
                    allow_redirects=False,  # 禁止自动重定向以检测反爬虫
                )

                # 检查是否被重定向到验证页面
                if response.status_code in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location', '')
                    if "sec.douban.com" in location:
                        raise RuntimeError(f"触发豆瓣反爬虫验证，被重定向到: {location}")
                    # 如果是正常重定向，手动跟随
                    response = self.session.get(
                        location if location.startswith('http') else f"https://movie.douban.com{location}",
                        headers=self._headers(url),
                        timeout=self.config.timeout,
                        proxies=self._proxies(),
                        allow_redirects=False,
                    )

                response.raise_for_status()

                # 检查响应内容是否包含验证页面特征
                if "安全验证" in response.text or "请输入验证码" in response.text:
                    raise RuntimeError("响应内容包含验证码页面")

                self._adaptive_delay()
                return response.text

            except requests.exceptions.HTTPError as exc:
                last_error = exc
                status_code = exc.response.status_code if exc.response else 0

                # 针对不同错误码采用不同策略
                if status_code == 403:
                    retry_delay = random.uniform(15.0, 25.0)
                elif status_code == 429:
                    retry_delay = random.uniform(30.0, 45.0)
                else:
                    retry_delay = random.uniform(self.config.min_delay, self.config.max_delay) * (attempt + 2)

                print(f"请求失败 (状态码: {status_code})，{retry_delay:.1f}秒后重试 (尝试 {attempt + 1}/{self.config.retries})")
                time.sleep(retry_delay)

            except RuntimeError as exc:
                # 反爬虫验证错误
                last_error = exc
                retry_delay = random.uniform(20.0, 35.0)
                print(f"触发反爬虫机制: {exc}，{retry_delay:.1f}秒后重试 (尝试 {attempt + 1}/{self.config.retries})")
                time.sleep(retry_delay)

            except requests.RequestException as exc:
                last_error = exc
                retry_delay = random.uniform(self.config.min_delay, self.config.max_delay) * (attempt + 2)
                print(f"请求异常: {exc}，{retry_delay:.1f}秒后重试 (尝试 {attempt + 1}/{self.config.retries})")
                time.sleep(retry_delay)

        raise RuntimeError(f"请求失败: {url} ({last_error})")


def download_cover_image(cover_url: str, save_path: Path, session: Optional[requests.Session] = None) -> bool:
    """下载电影封面图片

    Args:
        cover_url: 封面图片URL
        save_path: 保存路径
        session: 可选的requests会话

    Returns:
        是否下载成功
    """
    if not cover_url:
        return False

    try:
        if session is None:
            session = requests.Session()

        headers = {
            "User-Agent": random.choice(DEFAULT_USER_AGENTS),
            "Referer": "https://movie.douban.com/",
        }

        response = session.get(cover_url, headers=headers, timeout=15, stream=True)
        response.raise_for_status()

        # 确保目录存在
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with save_path.open('wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return True
    except Exception as e:
        print(f"下载封面失败 {cover_url}: {e}")
        return False


def parse_top250_page(html: str) -> List[Dict]:
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:  # pragma: no cover - optional dependency at runtime
        raise RuntimeError("缺少 beautifulsoup4 依赖，请先执行 pip install -r requirements.txt") from exc
    soup = BeautifulSoup(html, "html.parser")
    movies = []
    for item in soup.select("div.item"):
        title_node = item.select_one("span.title")
        rating_node = item.select_one("span.rating_num")
        detail_link = item.select_one("div.hd a")
        info_node = item.select_one("div.bd p")
        summary_node = item.select_one("span.inq")
        cover_img = item.select_one("div.pic img")

        info_lines = [
            _normalize_whitespace(line)
            for line in (info_node.get_text("\n", strip=True).split("\n") if info_node else [])
            if _normalize_whitespace(line)
        ]
        info_text = " ".join(info_lines)
        subject_id_match = re.search(r"/subject/(\d+)/", detail_link["href"]) if detail_link else None
        year_match = re.search(r"\b(19|20)\d{2}\b", info_text)
        duration_match = re.search(r"(\d+)\s*分钟", info_text)

        metadata = [item.strip() for item in re.split(r"/", info_text) if item.strip()]
        directors = []
        countries = []
        genres = []
        if metadata:
            directors_match = re.search(r"导演:\s*([^主演]+?)(?:主演:|$)", info_text)
            if directors_match:
                directors = [seg.strip() for seg in re.split(r"\s+", directors_match.group(1)) if seg.strip()]
            countries = [token for token in metadata if re.fullmatch(r"[\u4e00-\u9fa5A-Za-z· ]{2,20}", token)]
            genres = [token for token in metadata if token in info_text and len(token) <= 12]

        # 提取封面URL
        cover_url = ""
        if cover_img and cover_img.get("src"):
            cover_url = cover_img["src"]

        movies.append(
            clean_movie_record(
                {
                    "subject_id": subject_id_match.group(1) if subject_id_match else "",
                    "title": title_node.get_text(strip=True) if title_node else "",
                    "rating": rating_node.get_text(strip=True) if rating_node else 0,
                    "genre": "/".join(genres[:4]),
                    "release_year": year_match.group(0) if year_match else 0,
                    "duration": duration_match.group(1) if duration_match else 0,
                    "summary": summary_node.get_text(strip=True) if summary_node else "",
                    "country": "/".join(countries[:3]),
                    "directors": "/".join(directors[:3]),
                    "detail_url": detail_link["href"] if detail_link else "",
                    "cover_url": cover_url,
                }
            )
        )
    return dedupe_records(movies, ["subject_id", "title"])


def parse_movie_detail_page(html: str, subject_id: str) -> Optional[str]:
    """解析电影详情页，提取完整剧情简介"""
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise RuntimeError("缺少 beautifulsoup4 依赖，请先执行 pip install -r requirements.txt") from exc

    soup = BeautifulSoup(html, "html.parser")

    # 尝试多个可能的简介位置
    summary_text = ""

    # 方法1: 查找 span.all.hidden 中的完整简介
    summary_node = soup.select_one("span.all.hidden")
    if summary_node:
        summary_text = _normalize_whitespace(summary_node.get_text(strip=True))

    # 方法2: 如果没有展开的简介，查找默认显示的简介
    if not summary_text:
        summary_node = soup.select_one("span[property='v:summary']")
        if summary_node:
            summary_text = _normalize_whitespace(summary_node.get_text(strip=True))

    # 方法3: 查找 div#link-report 下的简介
    if not summary_text:
        link_report = soup.select_one("div#link-report")
        if link_report:
            # 移除"展开全部"等链接文本
            for a_tag in link_report.select("a"):
                a_tag.decompose()
            summary_text = _normalize_whitespace(link_report.get_text(strip=True))

    return summary_text if summary_text else None


def parse_comment_page(html: str, subject_id: str, movie_title: str) -> List[Dict]:
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:  # pragma: no cover - optional dependency at runtime
        raise RuntimeError("缺少 beautifulsoup4 依赖，请先执行 pip install -r requirements.txt") from exc
    soup = BeautifulSoup(html, "html.parser")
    comments = []
    for item in soup.select("div.comment-item"):
        short_node = item.select_one("span.short")
        user_node = item.select_one("span.comment-info a")
        vote_node = item.select_one("span.votes")
        rating_node = item.select_one("span.comment-info span.rating")
        time_node = item.select_one("span.comment-time")
        if not short_node:
            continue
        rating_value = 0
        if rating_node and rating_node.get("class"):
            for class_name in rating_node.get("class", []):
                match = re.search(r"allstar(\d+)0", class_name)
                if match:
                    rating_value = int(match.group(1)) / 2
                    break
        comments.append(
            {
                "subject_id": subject_id,
                "movie_title": movie_title,
                "comment_user": _normalize_whitespace(user_node.get_text(strip=True) if user_node else "匿名用户"),
                "comment_text": _normalize_whitespace(short_node.get_text(strip=True)),
                "comment_votes": int(vote_node.get_text(strip=True) or 0) if vote_node else 0,
                "comment_rating": rating_value,
                "comment_time": time_node.get("title", "") if time_node else "",
            }
        )
    return dedupe_records(comments, ["subject_id", "comment_user", "comment_text"])
