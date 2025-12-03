from flask import Blueprint, request, jsonify, g
from app.config import db
from app.models.community import Post, Vote, Report, Block
from app.routes.auth_utils import login_required
from flasgger import swag_from


community_bp = Blueprint("community", __name__, url_prefix="/api/community")


# 게시글 작성 (로그인 필요)
# POST /api/community/post
@community_bp.route("/post", methods=["POST"])
@swag_from("../docs/community_create_post.yml")
@login_required
def create_post():
    data = request.get_json() or {}

    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({"error": "title, content는 필수입니다."}), 400

    post = Post(
        title=title,
        content=content,
        user_id=g.current_user_id
    )
    db.session.add(post)
    db.session.commit()

    return jsonify({
        "message": "게시글 작성 완료",
        "post_id": post.id
    }), 201


# 게시글 목록 조회 (로그인 필요)
# GET /api/community/posts
@community_bp.route("/posts", methods=["GET"])
@swag_from("../docs/community_list_posts.yml")
@login_required
def list_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()

    results = []
    for p in posts:
        like_count = sum(1 for v in p.votes if v.value == 1)
        dislike_count = sum(1 for v in p.votes if v.value == -1)

        results.append({
            "id": p.id,
            "title": p.title,
            "content": p.content,
            "user_id": p.user_id,
            "created_at": p.created_at,
            "likes": like_count,
            "dislikes": dislike_count
        })

    return jsonify(results), 200


# 게시글 상세 조회
# GET /api/community/post/<id>
@community_bp.route("/post/<int:post_id>", methods=["GET"])
@swag_from("../docs/community_get_posts.yml")
@login_required
def get_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

    like_count = sum(1 for v in post.votes if v.value == 1)
    dislike_count = sum(1 for v in post.votes if v.value == -1)

    return jsonify({
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "user_id": post.user_id,
        "created_at": post.created_at,
        "likes": like_count,
        "dislikes": dislike_count
    }), 200


# 추천 / 비추천
# POST /api/community/post/<id>/vote
# body: { "value": 1 } or { "value": -1 }
@community_bp.route("/post/<int:post_id>/vote", methods=["POST"])
@swag_from("../docs/community_vote.yml")
@login_required
def vote_post(post_id):
    data = request.get_json() or {}
    value = data.get("value")

    if value not in [1, -1]:
        return jsonify({"error": "value는 1(추천) 또는 -1(비추천)이어야 합니다."}), 400

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

    # 같은 유저가 같은 글에 여러 번 투표하면 → 마지막 값으로 덮어쓰기
    vote = Vote.query.filter_by(post_id=post_id, user_id=g.current_user_id).first()
    if vote:
        vote.value = value
    else:
        vote = Vote(post_id=post_id, user_id=g.current_user_id, value=value)
        db.session.add(vote)

    db.session.commit()

    return jsonify({"message": "투표가 반영되었습니다."}), 200


# 신고하기
# POST /api/community/post/<id>/report
# body: { "reason": "..." }
from app.models.community import Report

@community_bp.route("/post/<int:post_id>/report", methods=["POST"])
@swag_from("../docs/community_report.yml")
@login_required
def report_post(post_id):
    data = request.get_json() or {}
    reason = data.get("reason", "")

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

    report = Report(
        post_id=post_id,
        user_id=g.current_user_id,
        reason=reason
    )
    db.session.add(report)
    db.session.commit()

    return jsonify({"message": "신고가 접수되었습니다."}), 201


# 사용자 차단
# POST /api/community/block
# body: { "blocked_user_id": 3 }
from app.models.community import Block

@community_bp.route("/block", methods=["POST"])
@swag_from("../docs/community_block.yml")
@login_required
def block_user():
    data = request.get_json() or {}
    blocked_user_id = data.get("blocked_user_id")

    if not blocked_user_id:
        return jsonify({"error": "blocked_user_id가 필요합니다."}), 400

    block = Block(
        user_id=g.current_user_id,
        blocked_user_id=blocked_user_id
    )
    db.session.add(block)
    db.session.commit()

    return jsonify({"message": "사용자를 차단했습니다."}), 201
