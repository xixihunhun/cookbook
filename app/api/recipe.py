"""菜谱接口蓝图"""
from flask import Blueprint, request, g
from sqlalchemy import func
from app import db
from app.models import Recipe, Category
from app.utils.response import success, fail
from app.utils.jwt_util import login_required

recipe_bp = Blueprint("recipe", __name__)


# ============== 公开接口 ==============

@recipe_bp.route("/list", methods=["GET"])
def list_recipes():
    """菜谱列表（分页 + 分类筛选 + 关键词搜索）"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    category_id = request.args.get("category_id", type=int)
    keyword = request.args.get("keyword", "").strip()

    query = Recipe.query
    if category_id:
        query = query.filter(Recipe.category_id == category_id)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(Recipe.title.like(like))

    pagination = query.order_by(Recipe.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return success({
        "items": [r.to_dict() for r in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
    })


@recipe_bp.route("/<int:rid>", methods=["GET"])
def get_recipe(rid):
    """菜谱详情（浏览量 +1）"""
    recipe = Recipe.query.get(rid)
    if not recipe:
        return fail(404, "菜谱不存在")
    recipe.views = (recipe.views or 0) + 1
    db.session.commit()
    return success(recipe.to_dict())


@recipe_bp.route("/random", methods=["GET"])
def random_recipe():
    """随机推荐（可指定数量 count，默认 1，最多 10）"""
    count = request.args.get("count", 1, type=int)
    count = max(1, min(count, 10))

    recipes = Recipe.query.order_by(func.random()).limit(count).all()
    if not recipes:
        return fail(404, "暂无菜谱")

    if count == 1:
        return success(recipes[0].to_dict())
    return success([r.to_dict() for r in recipes])


# ============== 需登录接口 ==============

@recipe_bp.route("/add", methods=["POST"])
@login_required
def add_recipe():
    """新增菜谱"""
    data = request.get_json()
    if not data:
        return fail(400, "请求体不能为空")

    title = data.get("title", "").strip()
    material = data.get("material", "").strip()
    step = data.get("step", "").strip()

    if not title:
        return fail(400, "菜名不能为空")
    if not material:
        return fail(400, "食材不能为空")
    if not step:
        return fail(400, "步骤不能为空")

    recipe = Recipe(
        title=title,
        material=material,
        step=step,
        tip=data.get("tip", ""),
        cover_img=data.get("cover_img", ""),
        category_id=data.get("category_id"),
        cook_time=data.get("cook_time", ""),
        author_id=g.user_id,
    )
    db.session.add(recipe)
    db.session.commit()
    return success(recipe.to_dict(), msg="新增成功")


@recipe_bp.route("/edit/<int:rid>", methods=["PUT"])
@login_required
def edit_recipe(rid):
    """修改菜谱（仅作者可改）"""
    recipe = Recipe.query.get(rid)
    if not recipe:
        return fail(404, "菜谱不存在")
    if recipe.author_id != g.user_id:
        return fail(403, "无权修改他人的菜谱")

    data = request.get_json()
    if not data:
        return fail(400, "请求体不能为空")

    if "title" in data:
        recipe.title = data["title"].strip()
    if "material" in data:
        recipe.material = data["material"].strip()
    if "step" in data:
        recipe.step = data["step"].strip()
    if "tip" in data:
        recipe.tip = data.get("tip", "")
    if "cover_img" in data:
        recipe.cover_img = data.get("cover_img", "")
    if "category_id" in data:
        recipe.category_id = data.get("category_id")
    if "cook_time" in data:
        recipe.cook_time = data.get("cook_time", "")

    db.session.commit()
    return success(recipe.to_dict(), msg="修改成功")


@recipe_bp.route("/delete/<int:rid>", methods=["DELETE"])
@login_required
def delete_recipe(rid):
    """删除菜谱（仅作者可删）"""
    recipe = Recipe.query.get(rid)
    if not recipe:
        return fail(404, "菜谱不存在")
    if recipe.author_id != g.user_id:
        return fail(403, "无权删除他人的菜谱")

    db.session.delete(recipe)
    db.session.commit()
    return success(msg="删除成功")


@recipe_bp.route("/collect/<int:rid>", methods=["POST"])
@login_required
def toggle_collect(rid):
    """收藏 / 取消收藏（切换状态）"""
    recipe = Recipe.query.get(rid)
    if not recipe:
        return fail(404, "菜谱不存在")

    recipe.is_collect = not recipe.is_collect
    db.session.commit()
    msg = "已收藏" if recipe.is_collect else "已取消收藏"
    return success({"is_collect": recipe.is_collect}, msg=msg)


@recipe_bp.route("/collect/list", methods=["GET"])
@login_required
def list_collect():
    """收藏列表"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = Recipe.query.filter(Recipe.is_collect == True).order_by(  # noqa: E712
        Recipe.id.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return success({
        "items": [r.to_dict() for r in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
    })


@recipe_bp.route("/mine", methods=["GET"])
@login_required
def list_my_recipes():
    """我发布的菜谱"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = Recipe.query.filter(
        Recipe.author_id == g.user_id
    ).order_by(Recipe.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return success({
        "items": [r.to_dict() for r in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
    })
