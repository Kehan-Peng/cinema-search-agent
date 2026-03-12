"""个人影院服务层"""
from __future__ import annotations

from typing import Dict, List, Optional
from datetime import datetime

from myutils.query import querys, init_db, get_movie_data


class CinemaService:
    """个人影院服务"""

    def get_watch_records(self, user_email: str, year: Optional[int] = None) -> List[Dict]:
        """获取观影记录

        Args:
            user_email: 用户邮箱
            year: 年份筛选（可选）
        """
        init_db()

        if year:
            sql = """
                SELECT wr.id, wr.watch_date, wr.rating, wr.is_favorite,
                       m.id as movie_id, m.title, m.cover_url, m.directors, m.types, m.rate
                FROM watch_records wr
                JOIN movies m ON wr.movie_id = m.id
                WHERE wr.user_email = %s AND strftime('%Y', wr.watch_date) = %s
                ORDER BY wr.watch_date DESC
            """
            records = querys(sql, [user_email, str(year)], "select")
        else:
            sql = """
                SELECT wr.id, wr.watch_date, wr.rating, wr.is_favorite,
                       m.id as movie_id, m.title, m.cover_url, m.directors, m.types, m.rate
                FROM watch_records wr
                JOIN movies m ON wr.movie_id = m.id
                WHERE wr.user_email = %s
                ORDER BY wr.watch_date DESC
            """
            records = querys(sql, [user_email], "select")

        return [
            {
                "id": r[0],
                "watch_date": r[1],
                "rating": r[2],
                "is_favorite": bool(r[3]),
                "movie": {
                    "id": r[4],
                    "title": r[5],
                    "cover_url": r[6],
                    "directors": r[7],
                    "types": r[8],
                    "rate": r[9],
                }
            }
            for r in records
        ]

    def get_yearly_stats(self, user_email: str, year: int) -> Dict:
        """获取年度观影统计

        Args:
            user_email: 用户邮箱
            year: 年份
        """
        init_db()

        # 观影数量
        count_sql = """
            SELECT COUNT(*) FROM watch_records
            WHERE user_email = %s AND strftime('%Y', watch_date) = %s
        """
        count = querys(count_sql, [user_email, str(year)], "select")[0][0]

        # 年度最爱（评分最高的前10部）
        favorites_sql = """
            SELECT wr.rating, m.id, m.title, m.cover_url, m.directors
            FROM watch_records wr
            JOIN movies m ON wr.movie_id = m.id
            WHERE wr.user_email = %s AND strftime('%Y', wr.watch_date) = %s
                  AND wr.rating IS NOT NULL
            ORDER BY wr.rating DESC, wr.watch_date DESC
            LIMIT 10
        """
        favorites = querys(favorites_sql, [user_email, str(year)], "select")

        return {
            "year": year,
            "watch_count": count,
            "favorites": [
                {
                    "rating": f[0],
                    "movie": {
                        "id": f[1],
                        "title": f[2],
                        "cover_url": f[3],
                        "directors": f[4],
                    }
                }
                for f in favorites
            ]
        }

    def add_watch_record(self, user_email: str, movie_id: int, watch_date: str,
                        rating: Optional[float] = None, is_favorite: bool = False) -> int:
        """添加观影记录"""
        init_db()

        record_id = querys(
            """
            INSERT INTO watch_records (user_email, movie_id, watch_date, rating, is_favorite)
            VALUES (%s, %s, %s, %s, %s)
            """,
            [user_email, movie_id, watch_date, rating, 1 if is_favorite else 0]
        )

        return record_id

    def update_watch_record(self, record_id: int, rating: Optional[float] = None,
                           is_favorite: Optional[bool] = None) -> bool:
        """更新观影记录"""
        init_db()

        updates = []
        params = []

        if rating is not None:
            updates.append("rating = %s")
            params.append(rating)

        if is_favorite is not None:
            updates.append("is_favorite = %s")
            params.append(1 if is_favorite else 0)

        if not updates:
            return False

        params.append(record_id)
        sql = f"UPDATE watch_records SET {', '.join(updates)} WHERE id = %s"

        affected = querys(sql, params)
        return affected > 0

    def get_watchlist(self, user_email: str) -> List[Dict]:
        """获取想看列表"""
        init_db()

        sql = """
            SELECT w.id, w.added_at,
                   m.id as movie_id, m.title, m.cover_url, m.directors, m.types, m.rate
            FROM watchlist w
            JOIN movies m ON w.movie_id = m.id
            WHERE w.user_email = %s
            ORDER BY w.added_at DESC
        """
        records = querys(sql, [user_email], "select")

        return [
            {
                "id": r[0],
                "added_at": r[1],
                "movie": {
                    "id": r[2],
                    "title": r[3],
                    "cover_url": r[4],
                    "directors": r[5],
                    "types": r[6],
                    "rate": r[7],
                }
            }
            for r in records
        ]

    def add_to_watchlist(self, user_email: str, movie_id: int) -> int:
        """添加到想看列表"""
        init_db()

        # 检查是否已存在
        existing = querys(
            "SELECT id FROM watchlist WHERE user_email = %s AND movie_id = %s",
            [user_email, movie_id],
            "select"
        )

        if existing:
            return existing[0][0]

        watchlist_id = querys(
            "INSERT INTO watchlist (user_email, movie_id) VALUES (%s, %s)",
            [user_email, movie_id]
        )

        return watchlist_id

    def remove_from_watchlist(self, user_email: str, movie_id: int) -> bool:
        """从想看列表移除"""
        init_db()

        affected = querys(
            "DELETE FROM watchlist WHERE user_email = %s AND movie_id = %s",
            [user_email, movie_id]
        )

        return affected > 0

    def get_watch_note(self, user_email: str, movie_id: int) -> Optional[Dict]:
        """获取观影笔记"""
        init_db()

        sql = """
            SELECT id, note_title, theme, plot, other, images, created_at, updated_at
            FROM watch_notes
            WHERE user_email = %s AND movie_id = %s
        """
        result = querys(sql, [user_email, movie_id], "select")

        if not result:
            return None

        r = result[0]
        return {
            "id": r[0],
            "note_title": r[1],
            "theme": r[2],
            "plot": r[3],
            "other": r[4],
            "images": r[5].split(",") if r[5] else [],
            "created_at": r[6],
            "updated_at": r[7],
        }

    def save_watch_note(self, user_email: str, movie_id: int, note_title: Optional[str] = None,
                       theme: Optional[str] = None, plot: Optional[str] = None,
                       other: Optional[str] = None, images: Optional[List[str]] = None) -> int:
        """保存观影笔记"""
        init_db()

        # 检查是否已存在
        existing = querys(
            "SELECT id FROM watch_notes WHERE user_email = %s AND movie_id = %s",
            [user_email, movie_id],
            "select"
        )

        images_str = ",".join(images) if images else None
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if existing:
            # 更新现有笔记
            note_id = existing[0][0]
            querys(
                """
                UPDATE watch_notes
                SET note_title = %s, theme = %s, plot = %s, other = %s, images = %s, updated_at = %s
                WHERE id = %s
                """,
                [note_title, theme, plot, other, images_str, now, note_id]
            )
        else:
            # 创建新笔记
            note_id = querys(
                """
                INSERT INTO watch_notes (user_email, movie_id, note_title, theme, plot, other, images)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                [user_email, movie_id, note_title, theme, plot, other, images_str]
            )

        return note_id

    def get_director_info(self, director_id: int) -> Optional[Dict]:
        """获取导演详情"""
        init_db()

        sql = """
            SELECT id, name, name_en, avatar_url, gender, birth_date, birth_place,
                   bio, representative_works, douban_id
            FROM directors
            WHERE id = %s
        """
        result = querys(sql, [director_id], "select")

        if not result:
            return None

        r = result[0]
        director = {
            "id": r[0],
            "name": r[1],
            "name_en": r[2],
            "avatar_url": r[3],
            "gender": r[4],
            "birth_date": r[5],
            "birth_place": r[6],
            "bio": r[7],
            "representative_works": r[8].split("/") if r[8] else [],
            "douban_id": r[9],
        }

        # 获取相关电影
        movies_sql = """
            SELECT m.id, m.title, m.cover_url, m.types, m.rate, m.release_year
            FROM movies m
            JOIN movie_directors md ON m.id = md.movie_id
            WHERE md.director_id = %s
            ORDER BY m.rate DESC, m.release_year DESC
        """
        movies = querys(movies_sql, [director_id], "select")

        director["movies"] = [
            {
                "id": m[0],
                "title": m[1],
                "cover_url": m[2],
                "types": m[3],
                "rate": m[4],
                "release_year": m[5],
            }
            for m in movies
        ]

        director["movie_count"] = len(movies)

        return director

    def get_director_by_name(self, name: str) -> Optional[Dict]:
        """根据姓名获取导演信息"""
        init_db()

        result = querys(
            "SELECT id FROM directors WHERE name = %s",
            [name],
            "select"
        )

        if not result:
            return None

        return self.get_director_info(result[0][0])

    def get_top250_movies(self) -> List[Dict]:
        """获取豆瓣Top 250电影列表"""
        init_db()

        sql = """
            SELECT id, title, rate, directors, types, release_year, cover_url
            FROM movies
            ORDER BY rate DESC, comment_len DESC
            LIMIT 250
        """
        movies = querys(sql, [], "select")

        return [
            {
                "rank": idx + 1,
                "id": m[0],
                "title": m[1],
                "rate": m[2],
                "directors": m[3],
                "types": m[4],
                "release_year": m[5],
                "cover_url": m[6],
            }
            for idx, m in enumerate(movies)
        ]

    def get_user_watch_status(self, user_email: str, movie_ids: List[int]) -> Dict[int, bool]:
        """批量获取用户观看状态"""
        init_db()

        if not movie_ids:
            return {}

        placeholders = ",".join(["%s"] * len(movie_ids))
        sql = f"""
            SELECT DISTINCT movie_id
            FROM watch_records
            WHERE user_email = %s AND movie_id IN ({placeholders})
        """

        watched = querys(sql, [user_email] + movie_ids, "select")
        watched_ids = {r[0] for r in watched}

        return {movie_id: movie_id in watched_ids for movie_id in movie_ids}
