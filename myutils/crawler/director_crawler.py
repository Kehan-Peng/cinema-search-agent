"""导演数据爬虫模块"""
from __future__ import annotations

import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

from ..query import querys, init_db
from .core import DoubanHttpClient


def parse_director_page(html: str, douban_id: str) -> Optional[Dict]:
    """解析导演详情页面"""
    soup = BeautifulSoup(html, "html.parser")

    # 导演姓名
    name_elem = soup.select_one("div#content h1")
    if not name_elem:
        return None

    name = name_elem.get_text(strip=True)
    name_en = None

    # 英文名（如果有）
    name_en_elem = soup.select_one("div#content h1 span.actor-name")
    if name_en_elem:
        name_en = name_en_elem.get_text(strip=True)

    # 头像
    avatar_url = None
    avatar_elem = soup.select_one("div#content img[rel='v:photo']")
    if avatar_elem:
        avatar_url = avatar_elem.get("src")

    # 个人信息
    info_elem = soup.select_one("div.bd div.info")
    gender = None
    birth_date = None
    birth_place = None

    if info_elem:
        info_text = info_elem.get_text()

        # 性别
        gender_match = re.search(r"性别[:：]\s*([男女])", info_text)
        if gender_match:
            gender = gender_match.group(1)

        # 出生日期
        birth_match = re.search(r"出生日期[:：]\s*(\d{4}-\d{2}-\d{2})", info_text)
        if birth_match:
            birth_date = birth_match.group(1)

        # 出生地
        place_match = re.search(r"出生地[:：]\s*([^\n]+)", info_text)
        if place_match:
            birth_place = place_match.group(1).strip()

    # 简介
    bio = None
    bio_elem = soup.select_one("div#intro div.bd span.all")
    if not bio_elem:
        bio_elem = soup.select_one("div#intro div.bd")
    if bio_elem:
        bio = bio_elem.get_text(strip=True)

    # 代表作品
    representative_works = []
    works_section = soup.select("div#best_movies div.list-wrapper li")
    for work in works_section[:5]:  # 取前5部代表作
        title_elem = work.select_one("a em")
        if title_elem:
            representative_works.append(title_elem.get_text(strip=True))

    return {
        "name": name,
        "name_en": name_en,
        "avatar_url": avatar_url,
        "gender": gender,
        "birth_date": birth_date,
        "birth_place": birth_place,
        "bio": bio,
        "representative_works": "/".join(representative_works) if representative_works else None,
        "douban_id": douban_id,
    }


def crawl_director_info(director_name: str, douban_id: Optional[str] = None) -> Optional[Dict]:
    """爬取导演信息

    Args:
        director_name: 导演姓名
        douban_id: 豆瓣导演ID（如果已知）

    Returns:
        导演信息字典，如果爬取失败返回None
    """
    client = DoubanHttpClient()

    # 如果没有提供douban_id，先搜索导演
    if not douban_id:
        search_url = f"https://www.douban.com/search?cat=1005&q={director_name}"
        search_html = client.get_html(search_url)
        soup = BeautifulSoup(search_html, "html.parser")

        # 查找第一个导演结果
        result = soup.select_one("div.result")
        if result:
            link = result.select_one("a")
            if link and link.get("href"):
                href = link.get("href")
                # 提取导演ID
                match = re.search(r"/celebrity/(\d+)/", href)
                if match:
                    douban_id = match.group(1)

    if not douban_id:
        print(f"未找到导演 {director_name} 的豆瓣ID")
        return None

    # 爬取导演详情页
    director_url = f"https://movie.douban.com/celebrity/{douban_id}/"
    html = client.get_html(director_url)

    return parse_director_page(html, douban_id)


def save_director_to_db(director_info: Dict) -> int:
    """保存导演信息到数据库

    Returns:
        导演ID
    """
    init_db()

    # 检查导演是否已存在
    existing = querys(
        "SELECT id FROM directors WHERE name = %s",
        [director_info["name"]],
        "select"
    )

    if existing:
        # 更新现有导演信息
        director_id = existing[0][0]
        querys(
            """
            UPDATE directors
            SET name_en = %s, avatar_url = %s, gender = %s,
                birth_date = %s, birth_place = %s, bio = %s,
                representative_works = %s, douban_id = %s
            WHERE id = %s
            """,
            [
                director_info.get("name_en"),
                director_info.get("avatar_url"),
                director_info.get("gender"),
                director_info.get("birth_date"),
                director_info.get("birth_place"),
                director_info.get("bio"),
                director_info.get("representative_works"),
                director_info.get("douban_id"),
                director_id,
            ]
        )
    else:
        # 插入新导演
        director_id = querys(
            """
            INSERT INTO directors (name, name_en, avatar_url, gender, birth_date,
                                   birth_place, bio, representative_works, douban_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                director_info["name"],
                director_info.get("name_en"),
                director_info.get("avatar_url"),
                director_info.get("gender"),
                director_info.get("birth_date"),
                director_info.get("birth_place"),
                director_info.get("bio"),
                director_info.get("representative_works"),
                director_info.get("douban_id"),
            ]
        )

    return director_id


def enrich_directors_from_movies() -> Dict:
    """从现有电影数据中提取导演并爬取详细信息"""
    init_db()

    # 获取所有电影的导演
    movies = querys("SELECT id, title, directors FROM movies WHERE directors IS NOT NULL", [], "select")

    director_names = set()
    for movie_id, title, directors in movies:
        if directors:
            for director in directors.split("/"):
                director = director.strip()
                if director and director != "未知导演":
                    director_names.add(director)

    print(f"发现 {len(director_names)} 位导演")

    enriched_count = 0
    failed_directors = []

    for director_name in director_names:
        try:
            print(f"正在爬取导演: {director_name}")
            director_info = crawl_director_info(director_name)

            if director_info:
                save_director_to_db(director_info)
                enriched_count += 1
                print(f"✓ 成功爬取导演 {director_name} 的信息")
            else:
                failed_directors.append(director_name)
                print(f"✗ 未能爬取导演 {director_name} 的信息")

        except Exception as e:
            failed_directors.append(director_name)
            print(f"✗ 爬取导演 {director_name} 时出错: {e}")

    # 建立电影-导演关联
    link_movies_to_directors()

    return {
        "total_directors": len(director_names),
        "enriched_count": enriched_count,
        "failed_count": len(failed_directors),
        "failed_directors": failed_directors,
    }


def link_movies_to_directors():
    """建立电影和导演的关联关系"""
    init_db()

    # 获取所有导演
    directors = querys("SELECT id, name FROM directors", [], "select")
    director_map = {name: director_id for director_id, name in directors}

    # 获取所有电影
    movies = querys("SELECT id, directors FROM movies WHERE directors IS NOT NULL", [], "select")

    linked_count = 0
    for movie_id, directors_str in movies:
        if not directors_str:
            continue

        for director_name in directors_str.split("/"):
            director_name = director_name.strip()
            director_id = director_map.get(director_name)

            if director_id:
                # 检查关联是否已存在
                existing = querys(
                    "SELECT 1 FROM movie_directors WHERE movie_id = %s AND director_id = %s",
                    [movie_id, director_id],
                    "select"
                )

                if not existing:
                    querys(
                        "INSERT INTO movie_directors (movie_id, director_id) VALUES (%s, %s)",
                        [movie_id, director_id]
                    )
                    linked_count += 1

    print(f"建立了 {linked_count} 个电影-导演关联")
    return linked_count
