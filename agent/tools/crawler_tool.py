"""
爬虫工具

封装爬虫任务，支持爬取电影数据、评论数据、补充简介等功能。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .base_tool import BaseTool


class CrawlerTool(BaseTool):
    """爬虫工具"""

    @property
    def name(self) -> str:
        return "crawler_tool"

    @property
    def description(self) -> str:
        return "爬取豆瓣电影数据，支持爬取 Top250 电影、评论、补充简介、下载封面等功能"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_type": {
                    "type": "string",
                    "enum": ["movies", "summaries", "comments"],
                    "description": "任务类型：movies=爬取电影数据，summaries=补充简介，comments=爬取评论",
                },
                "pages": {
                    "type": "integer",
                    "description": "爬取页数（仅 movies 和 comments 任务需要）",
                    "minimum": 1,
                },
                "download_covers": {
                    "type": "boolean",
                    "description": "是否下载封面（仅 movies 任务需要）",
                    "default": True,
                },
                "limit_movies": {
                    "type": "integer",
                    "description": "限制处理的电影数量（仅 summaries 和 comments 任务需要）",
                },
                "use_api": {
                    "type": "boolean",
                    "description": "是否使用豆瓣 API（仅 summaries 任务需要）",
                    "default": True,
                },
            },
            "required": ["task_type"],
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_type": {"type": "string"},
                "total_items": {"type": "integer", "description": "处理的总条目数"},
                "success_count": {"type": "integer", "description": "成功数量"},
                "failed_count": {"type": "integer", "description": "失败数量"},
                "downloaded_covers": {"type": "integer", "description": "下载的封面数量"},
                "message": {"type": "string", "description": "执行消息"},
            },
        }

    def _execute(self, **kwargs) -> Any:
        """执行爬虫任务"""
        from myutils.crawler.jobs import crawl_top_movies, enrich_movie_summaries, crawl_comments

        task_type = kwargs["task_type"]

        if task_type == "movies":
            pages = kwargs.get("pages", 8)
            download_covers = kwargs.get("download_covers", True)

            result = crawl_top_movies(
                pages=pages,
                download_covers=download_covers,
                resume=True,
            )

            return {
                "task_type": "movies",
                "total_items": result.get("total_movies", 0),
                "success_count": result.get("total_movies", 0),
                "failed_count": 0,
                "downloaded_covers": result.get("downloaded_covers", 0),
                "message": f"成功爬取 {result.get('total_movies', 0)} 部电影",
            }

        elif task_type == "summaries":
            limit_movies = kwargs.get("limit_movies", 20)
            use_api = kwargs.get("use_api", True)

            result = enrich_movie_summaries(
                limit_movies=limit_movies,
                use_api=use_api,
                use_browser=not use_api,
            )

            return {
                "task_type": "summaries",
                "total_items": result.get("enriched_count", 0),
                "success_count": result.get("enriched_count", 0),
                "failed_count": result.get("failed_count", 0),
                "downloaded_covers": 0,
                "message": f"成功补充 {result.get('enriched_count', 0)} 部电影简介",
            }

        elif task_type == "comments":
            pages = kwargs.get("pages", 3)
            limit_movies = kwargs.get("limit_movies", 30)

            result = crawl_comments(
                pages_per_movie=pages,
                limit_movies=limit_movies,
            )

            return {
                "task_type": "comments",
                "total_items": result.get("total_comments", 0),
                "success_count": result.get("total_comments", 0),
                "failed_count": 0,
                "downloaded_covers": 0,
                "message": f"成功爬取 {result.get('total_comments', 0)} 条评论",
            }

        else:
            raise ValueError(f"不支持的任务类型: {task_type}")
