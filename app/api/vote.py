"""每日抽签投票蓝图：推荐菜谱池 / 投票 / 揭晓"""
from datetime import date, timedelta
from flask import Blueprint, request, g
from sqlalchemy import func, or_
from app import db
from app.models import User, Family, Recipe, DailyVote
from app.utils.response import success, fail
from app.utils.jwt_util import login_required

vote_bp = Blueprint("vote", __name__)


@vote_bp.route("/recommend", methods=["GET"])
@login_required
def recommend_pool():
    """
    今日推荐菜谱池（抽签候选）
    - 优先推荐家庭成员收藏的菜
    - 不够的话随机补充
    - 每次返回 8 个候选
    """
    user = User.query.get(g.user_id)
    if not user or not user.family_id:
        return fail(400, "请先加入家庭")

    count = int(request.args.get("count", 8))
    count = max(4, min(count, 12))  # 4~12 之间

    # 1. 家庭成员收藏的菜
    favorite_recipes = (
        Recipe.query.filter_by(is_collect=True)
        .order_by(func.random())
        .limit(count)
        .all()
    )

    pool = list(favorite_recipes)
    favorite_ids = {r.id for r in pool}

    # 2. 不够的话随机补充
    if len(pool) < count:
        remaining = Recipe.query.filter(~Recipe.id.in_(favorite_ids)).order_by(func.random()).limit(count - len(pool)).all()
        pool.extend(remaining)

    return success([r.to_dict() for r in pool])


@vote_bp.route("/cast", methods=["POST"])
@login_required
def cast_vote():
    """
    投票：给某个菜谱投一票
    规则：每人每天只能投一票，可以改投（取消之前的）
    """
    user = User.query.get(g.user_id)
    if not user or not user.family_id:
        return fail(400, "请先加入家庭")

    data = request.get_json() or {}
    recipe_id = data.get("recipe_id")
    if not recipe_id:
        return fail(400, "请选择菜谱")

    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return fail(404, "菜谱不存在")

    today = date.today()

    # 查今天是否投过
    existing = DailyVote.query.filter_by(
        family_id=user.family_id,
        voter_id=user.id,
        vote_date=today,
    ).first()

    if existing:
        # 改投：更新 recipe_id
        existing.recipe_id = recipe_id
        db.session.commit()
        return success(existing.to_dict(), msg="改投成功")
    else:
        # 新投票
        vote = DailyVote(
            family_id=user.family_id,
            recipe_id=recipe_id,
            voter_id=user.id,
            vote_date=today,
        )
        db.session.add(vote)
        db.session.commit()
        return success(vote.to_dict(), msg="投票成功")


@vote_bp.route("/today", methods=["GET"])
@login_required
def get_today_result():
    """
    今日投票结果：
    - 每个人投了什么
    - 统计得票
    - 返回"今日推荐"（得票最多的）
    """
    user = User.query.get(g.user_id)
    if not user or not user.family_id:
        return fail(400, "请先加入家庭")

    today = date.today()

    # 今日所有投票
    votes = DailyVote.query.filter_by(
        family_id=user.family_id,
        vote_date=today,
    ).all()

    # 每个人投了什么
    my_vote = next((v for v in votes if v.voter_id == user.id), None)
    vote_details = [v.to_dict() for v in votes]

    # 统计得票
    from collections import Counter
    counter = Counter(v.recipe_id for v in votes)

    # 构建菜谱信息
    recipe_ids = list(counter.keys())
    recipes = Recipe.query.filter(Recipe.id.in_(recipe_ids)).all() if recipe_ids else []
    recipe_map = {r.id: r for r in recipes}

    vote_summary = []
    for recipe_id, votes_count in counter.most_common():
        recipe = recipe_map.get(recipe_id)
        if recipe:
            vote_summary.append({
                "recipe": recipe.to_dict(),
                "votes": votes_count,
            })

    # 今日冠军
    winner = vote_summary[0] if vote_summary else None

    return success({
        "vote_date": today.isoformat(),
        "total_votes": len(votes),
        "vote_details": vote_details,
        "my_vote": my_vote.to_dict() if my_vote else None,
        "vote_summary": vote_summary,
        "winner": winner,
    })


@vote_bp.route("/history", methods=["GET"])
@login_required
def get_history():
    """历史投票结果（最近 N 天）"""
    user = User.query.get(g.user_id)
    if not user or not user.family_id:
        return fail(400, "请先加入家庭")

    days = int(request.args.get("days", 7))
    days = max(1, min(days, 30))

    since = date.today() - timedelta(days=days - 1)

    votes = DailyVote.query.filter(
        DailyVote.family_id == user.family_id,
        DailyVote.vote_date >= since,
    ).order_by(DailyVote.vote_date.desc()).all()

    # 按日期分组
    from collections import defaultdict
    by_date = defaultdict(list)
    for v in votes:
        by_date[v.vote_date].append(v.to_dict())

    history = []
    for d in sorted(by_date.keys(), reverse=True):
        day_votes = by_date[d]
        # 当天冠军
        counter = Counter(v["recipe_id"] for v in day_votes)
        winner_id = counter.most_common(1)[0][0] if counter else None
        winner_recipe = Recipe.query.get(winner_id).to_dict() if winner_id else None
        history.append({
            "date": d.isoformat(),
            "votes": day_votes,
            "winner": winner_recipe,
        })

    return success(history)


@vote_bp.route("/cancel", methods=["POST"])
@login_required
def cancel_vote():
    """取消今日投票"""
    user = User.query.get(g.user_id)
    if not user or not user.family_id:
        return fail(400, "请先加入家庭")

    today = date.today()
    vote = DailyVote.query.filter_by(
        family_id=user.family_id,
        voter_id=user.id,
        vote_date=today,
    ).first()

    if not vote:
        return fail(400, "今天还没投票")

    db.session.delete(vote)
    db.session.commit()
    return success(msg="已取消投票")
