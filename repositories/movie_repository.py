from __future__ import annotations

from typing import Dict, List, Optional

from myutils.query import get_movie_comments, get_movie_data, get_top_movies, search_movies
from myutils.recommender.semantic_embeddings import semantic_search


class MovieRepository:
    def get_top_movies(self, limit: int = 10) -> List[Dict]:
        return get_top_movies(limit)

    def get_movie(self, movie_id: int) -> Optional[Dict]:
        return get_movie_data(movie_id)

    def search(self, keyword: str) -> List[Dict]:
        return search_movies(keyword)

    def semantic_search(self, query: str, top_n: int = 10, model_name: str = "word2vec") -> List[Dict]:
        """语义搜索"""
        return semantic_search(query, top_n, model_name)

    def get_comments(self, movie_id: int) -> List[Dict]:
        return get_movie_comments(movie_id)
