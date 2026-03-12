"""基于豆瓣公开 API 的爬虫客户端"""
from __future__ import annotations

import random
import time
from typing import Dict, Optional

import requests


class DoubanAPIClient:
    """使用豆瓣公开 API 获取电影信息"""

    def __init__(self, min_delay: float = 2.0, max_delay: float = 4.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.session = requests.Session()
        self.request_count = 0

    def _headers(self) -> Dict[str, str]:
        """生成请求头"""
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Referer": "https://movie.douban.com/",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    def _adaptive_delay(self) -> None:
        """自适应延迟"""
        self.request_count += 1
        delay = random.uniform(self.min_delay, self.max_delay)

        # 每5个请求增加额外延迟
        if self.request_count % 5 == 0:
            delay += random.uniform(2.0, 4.0)

        time.sleep(delay)

    def get_movie_detail(self, subject_id: str) -> Optional[Dict]:
        """
        获取电影详情

        Args:
            subject_id: 豆瓣电影ID

        Returns:
            电影详情字典，包含简介等信息
        """
        api_url = f"https://movie.douban.com/j/subject_abstract?subject_id={subject_id}"

        try:
            response = self.session.get(
                api_url,
                headers=self._headers(),
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("r") == 0 and "subject" in data:
                    self._adaptive_delay()
                    return data["subject"]

            return None

        except Exception as e:
            print(f"API 请求失败: {e}")
            return None

    def search_movie_id(self, title: str) -> Optional[str]:
        """
        通过电影标题搜索获取豆瓣ID

        Args:
            title: 电影标题

        Returns:
            豆瓣电影ID
        """
        search_url = f"https://movie.douban.com/j/subject_suggest?q={title}"

        try:
            response = self.session.get(
                search_url,
                headers=self._headers(),
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # 返回第一个匹配结果的ID
                    self._adaptive_delay()
                    return str(data[0].get("id", ""))

            return None

        except Exception as e:
            print(f"搜索电影ID失败: {e}")
            return None

    def get_movie_summary_from_page(self, subject_id: str) -> Optional[str]:
        """
        从豆瓣移动端API获取完整简介

        Args:
            subject_id: 豆瓣电影ID

        Returns:
            电影简介文本
        """
        # 使用移动端API，反爬虫限制较松
        mobile_api_url = f"https://m.douban.com/rexxar/api/v2/movie/{subject_id}"

        # 使用移动端User-Agent
        mobile_headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.20",
            "Referer": "https://m.douban.com/",
            "Accept": "application/json",
        }

        try:
            response = self.session.get(
                mobile_api_url,
                headers=mobile_headers,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                if "intro" in data and data["intro"]:
                    self._adaptive_delay()
                    return data["intro"]

            return None

        except Exception as e:
            print(f"移动端API请求失败: {e}")
            return None
