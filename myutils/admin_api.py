from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Dict

from flask import Blueprint, abort, current_app, jsonify, render_template, request, session

from .crawler.core import STATUS_FILE
from .crawler.jobs import build_behavior_dataset, crawl_movie_comments, crawl_top_movies
from .evaluation import evaluate_recommenders
from .query import DB_PATH
from .rl.features import get_movie_feature_map
from .rl.local_ppo import (
    ensure_bootstrap_model,
    rollback_model_version,
    status_payload,
    train_pending_batch_if_ready,
)
from services.experiment_service import ExperimentService
from services.system_service import SystemService
from services.ui_audit_service import UIAuditService
from services.agent_service import AgentService
from services.cinema_service import CinemaService


admin_bp = Blueprint("admin_bp", __name__)
_JOB_STATE: Dict[str, Dict] = {}
_experiment_service = ExperimentService()
_system_service = SystemService()
_ui_audit_service = UIAuditService(Path(__file__).resolve().parents[1])
_agent_service = AgentService()
_cinema_service = CinemaService()


def is_admin_user() -> bool:
    email = (session.get("email") or "").lower()
    return bool(email) and email in current_app.config["ADMIN_EMAILS"]


def admin_required():
    if not session.get("email"):
        abort(401)
    if not is_admin_user():
        abort(403)


def _read_crawler_status() -> Dict:
    if not STATUS_FILE.exists():
        return {}
    return json.loads(STATUS_FILE.read_text(encoding="utf-8"))


def _system_counts() -> Dict:
    return _system_service.overview_counts(
        db_path=str(DB_PATH),
        movie_feature_cache_size=len(get_movie_feature_map()),
    )


def _overview_payload() -> Dict:
    return {
        "system": _system_counts(),
        "rl": status_payload(),
        "crawler": _read_crawler_status(),
        "jobs": _JOB_STATE,
        "evaluation": evaluate_recommenders(),
        "experiments": _experiment_service.build_trend_payload(limit=10),
        "ui_audit": _ui_audit_service.audit(current_app),
        "agent": _agent_service.get_status(),
    }


def _run_async_job(job_name: str, target, **kwargs) -> Dict:
    if _JOB_STATE.get(job_name, {}).get("status") == "running":
        return {"accepted": False, "message": "任务正在执行中"}

    _JOB_STATE[job_name] = {"status": "running", "params": kwargs}
    app_obj = current_app._get_current_object()

    def runner():
        try:
            result = target(**kwargs)
            _JOB_STATE[job_name] = {"status": "completed", "result": result}
        except Exception as exc:  # pragma: no cover - background task path
            app_obj.logger.exception("admin job failed: %s", job_name)
            _JOB_STATE[job_name] = {"status": "failed", "message": str(exc)}

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    return {"accepted": True, "message": "任务已启动", "job": job_name}


@admin_bp.route("/admin/dashboard")
def admin_dashboard():
    admin_required()
    return render_template("admin_dashboard.html")


@admin_bp.route("/admin/models")
def admin_models():
    admin_required()
    return render_template("admin_models.html")


@admin_bp.route("/admin/crawler")
def admin_crawler():
    admin_required()
    return render_template("admin_crawler.html")


@admin_bp.route("/admin/experiments")
def admin_experiments():
    admin_required()
    return render_template("admin_experiments.html")


@admin_bp.route("/api/v1/admin/overview")
def api_admin_overview():
    admin_required()
    return jsonify({"code": 200, "data": _overview_payload()})


@admin_bp.route("/api/v1/admin/evaluation")
def api_admin_evaluation():
    admin_required()
    return jsonify({"code": 200, "data": evaluate_recommenders()})


@admin_bp.route("/api/v1/admin/experiments")
def api_admin_experiments():
    admin_required()
    limit = request.args.get("limit", default=20, type=int)
    return jsonify({"code": 200, "data": _experiment_service.build_trend_payload(limit=limit)})


@admin_bp.route("/api/v1/admin/experiments/run", methods=["POST"])
def api_admin_experiments_run():
    admin_required()
    payload = request.get_json(silent=True) or {}
    top_k = int(payload.get("top_k", 5))
    note = str(payload.get("note", "")).strip()
    result = _experiment_service.build_snapshot(top_k=top_k, note=note)
    return jsonify({"code": 200, "data": result, "msg": "实验快照已生成"})


@admin_bp.route("/api/v1/admin/models")
def api_admin_models():
    admin_required()
    return jsonify({"code": 200, "data": status_payload()})


@admin_bp.route("/api/v1/admin/models/bootstrap", methods=["POST"])
def api_admin_model_bootstrap():
    admin_required()
    result = ensure_bootstrap_model()
    return jsonify({"code": 200, "data": result, "msg": "Bootstrap 完成"})


@admin_bp.route("/api/v1/admin/models/train", methods=["POST"])
def api_admin_model_train():
    admin_required()
    force = bool((request.get_json(silent=True) or {}).get("force", False))
    result = train_pending_batch_if_ready(force=force)
    return jsonify({"code": 200, "data": result, "msg": "训练已执行"})


@admin_bp.route("/api/v1/admin/models/<version_tag>/rollback", methods=["POST"])
def api_admin_model_rollback(version_tag: str):
    admin_required()
    result = rollback_model_version(version_tag)
    return jsonify({"code": 200 if result else 404, "ok": result, "version_tag": version_tag}), (200 if result else 404)


@admin_bp.route("/api/v1/admin/crawler/status")
def api_admin_crawler_status():
    admin_required()
    return jsonify({"code": 200, "data": {"crawler": _read_crawler_status(), "jobs": _JOB_STATE}})


@admin_bp.route("/api/v1/admin/crawler/run", methods=["POST"])
def api_admin_crawler_run():
    admin_required()
    payload = request.get_json(silent=True) or {}
    job = payload.get("job")
    if job == "movies":
        result = _run_async_job("movies", crawl_top_movies, pages=int(payload.get("pages", 8)))
    elif job == "comments":
        result = _run_async_job(
            "comments",
            crawl_movie_comments,
            pages_per_movie=int(payload.get("pages_per_movie", 3)),
            limit_movies=int(payload["limit_movies"]) if payload.get("limit_movies") else None,
        )
    elif job == "behaviors":
        result = _run_async_job(
            "behaviors",
            build_behavior_dataset,
            user_count=int(payload.get("user_count", 60)),
            min_behaviors=int(payload.get("min_behaviors", 8)),
            max_behaviors=int(payload.get("max_behaviors", 16)),
        )
    else:
        return jsonify({"code": 400, "msg": "不支持的任务类型"}), 400
    return jsonify({"code": 200, "data": result})

# Agent 系统 API
@admin_bp.route("/admin/agent")
def admin_agent():
    admin_required()
    return render_template("admin_agent.html")


@admin_bp.route("/api/v1/admin/agent/status")
def api_admin_agent_status():
    admin_required()
    return jsonify({"code": 200, "data": _agent_service.get_status()})


@admin_bp.route("/api/v1/admin/agent/health")
def api_admin_agent_health():
    admin_required()
    return jsonify({"code": 200, "data": _agent_service.monitor_system_health()})


@admin_bp.route("/api/v1/admin/agent/execute", methods=["POST"])
def api_admin_agent_execute():
    admin_required()
    payload = request.get_json(silent=True) or {}
    goal = payload.get("goal")
    if not goal:
        return jsonify({"code": 400, "msg": "缺少目标参数"}), 400
    
    result = _agent_service.execute_goal(goal)
    return jsonify({"code": 200, "data": result, "msg": "目标执行完成"})


@admin_bp.route("/api/v1/admin/agent/tools")
def api_admin_agent_tools():
    admin_required()
    return jsonify({"code": 200, "data": _agent_service.list_tools()})


@admin_bp.route("/api/v1/admin/agent/decisions")
def api_admin_agent_decisions():
    admin_required()
    limit = request.args.get("limit", default=10, type=int)
    return jsonify({"code": 200, "data": _agent_service.get_recent_decisions(limit)})


@admin_bp.route("/api/v1/admin/agent/stats")
def api_admin_agent_stats():
    admin_required()
    return jsonify({"code": 200, "data": _agent_service.get_action_stats()})


# 个人影院 API
@admin_bp.route("/cinema")
def cinema():
    if not session.get("email"):
        abort(401)
    return render_template("cinema.html")


@admin_bp.route("/director/<int:director_id>")
def director_detail(director_id: int):
    return render_template("director.html")


@admin_bp.route("/director/<string:name>")
def director_by_name(name: str):
    return render_template("director.html")


@admin_bp.route("/api/v1/cinema/watch-records")
def api_cinema_watch_records():
    if not session.get("email"):
        abort(401)

    user_email = session.get("email")
    year = request.args.get("year", type=int)

    records = _cinema_service.get_watch_records(user_email, year)
    return jsonify({"code": 200, "data": records})


@admin_bp.route("/api/v1/cinema/watch-records", methods=["POST"])
def api_cinema_add_watch_record():
    if not session.get("email"):
        abort(401)

    user_email = session.get("email")
    payload = request.get_json(silent=True) or {}

    movie_id = payload.get("movie_id")
    watch_date = payload.get("watch_date")
    rating = payload.get("rating")
    is_favorite = payload.get("is_favorite", False)

    if not movie_id or not watch_date:
        return jsonify({"code": 400, "msg": "缺少必要参数"}), 400

    record_id = _cinema_service.add_watch_record(
        user_email, movie_id, watch_date, rating, is_favorite
    )

    return jsonify({"code": 200, "data": {"id": record_id}, "msg": "添加成功"})


@admin_bp.route("/api/v1/cinema/watch-records/<int:record_id>", methods=["PUT"])
def api_cinema_update_watch_record(record_id: int):
    if not session.get("email"):
        abort(401)

    payload = request.get_json(silent=True) or {}
    rating = payload.get("rating")
    is_favorite = payload.get("is_favorite")

    success = _cinema_service.update_watch_record(record_id, rating, is_favorite)

    if success:
        return jsonify({"code": 200, "msg": "更新成功"})
    else:
        return jsonify({"code": 404, "msg": "记录不存在"}), 404


@admin_bp.route("/api/v1/cinema/yearly-stats/<int:year>")
def api_cinema_yearly_stats(year: int):
    if not session.get("email"):
        abort(401)

    user_email = session.get("email")
    stats = _cinema_service.get_yearly_stats(user_email, year)

    return jsonify({"code": 200, "data": stats})


@admin_bp.route("/api/v1/cinema/watchlist")
def api_cinema_watchlist():
    if not session.get("email"):
        abort(401)

    user_email = session.get("email")
    watchlist = _cinema_service.get_watchlist(user_email)

    return jsonify({"code": 200, "data": watchlist})


@admin_bp.route("/api/v1/cinema/watchlist", methods=["POST"])
def api_cinema_add_to_watchlist():
    if not session.get("email"):
        abort(401)

    user_email = session.get("email")
    payload = request.get_json(silent=True) or {}
    movie_id = payload.get("movie_id")

    if not movie_id:
        return jsonify({"code": 400, "msg": "缺少电影ID"}), 400

    watchlist_id = _cinema_service.add_to_watchlist(user_email, movie_id)

    return jsonify({"code": 200, "data": {"id": watchlist_id}, "msg": "添加成功"})


@admin_bp.route("/api/v1/cinema/watchlist/<int:movie_id>", methods=["DELETE"])
def api_cinema_remove_from_watchlist(movie_id: int):
    if not session.get("email"):
        abort(401)

    user_email = session.get("email")
    success = _cinema_service.remove_from_watchlist(user_email, movie_id)

    if success:
        return jsonify({"code": 200, "msg": "移除成功"})
    else:
        return jsonify({"code": 404, "msg": "记录不存在"}), 404


@admin_bp.route("/api/v1/cinema/watch-notes/<int:movie_id>")
def api_cinema_get_watch_note(movie_id: int):
    if not session.get("email"):
        abort(401)

    user_email = session.get("email")
    note = _cinema_service.get_watch_note(user_email, movie_id)

    if note:
        return jsonify({"code": 200, "data": note})
    else:
        return jsonify({"code": 404, "msg": "笔记不存在"}), 404


@admin_bp.route("/api/v1/cinema/watch-notes/<int:movie_id>", methods=["POST", "PUT"])
def api_cinema_save_watch_note(movie_id: int):
    if not session.get("email"):
        abort(401)

    user_email = session.get("email")
    payload = request.get_json(silent=True) or {}

    note_id = _cinema_service.save_watch_note(
        user_email=user_email,
        movie_id=movie_id,
        note_title=payload.get("note_title"),
        theme=payload.get("theme"),
        plot=payload.get("plot"),
        other=payload.get("other"),
        images=payload.get("images")
    )

    return jsonify({"code": 200, "data": {"id": note_id}, "msg": "保存成功"})


@admin_bp.route("/api/v1/cinema/directors/<int:director_id>")
def api_cinema_director_info(director_id: int):
    director = _cinema_service.get_director_info(director_id)

    if director:
        return jsonify({"code": 200, "data": director})
    else:
        return jsonify({"code": 404, "msg": "导演不存在"}), 404


@admin_bp.route("/api/v1/cinema/directors/by-name/<string:name>")
def api_cinema_director_by_name(name: str):
    director = _cinema_service.get_director_by_name(name)

    if director:
        return jsonify({"code": 200, "data": director})
    else:
        return jsonify({"code": 404, "msg": "导演不存在"}), 404


@admin_bp.route("/api/v1/cinema/top250")
def api_cinema_top250():
    movies = _cinema_service.get_top250_movies()

    # 如果用户已登录，获取观看状态
    watch_status = {}
    if session.get("email"):
        movie_ids = [m["id"] for m in movies]
        watch_status = _cinema_service.get_user_watch_status(session.get("email"), movie_ids)

    return jsonify({"code": 200, "data": {"movies": movies, "watch_status": watch_status}})
