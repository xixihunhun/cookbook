from flask import Blueprint, request
from app import db
from app.models import Recipe
from app.utils.response import success, fail
import random

recipe_bp = Blueprint("recipe", __name__)

# 1. 获取全部菜谱
@recipe_bp.route("/list", methods=["GET"])
def get_recipe_list():
    recipe_list = Recipe.query.all()
    return success([item.to_dict() for item in recipe_list])

# 2. 随机推荐一道菜
@recipe_bp.route("/random", methods=["GET"])
def get_random_recipe():
    recipe_list = Recipe.query.all()
    if not recipe_list:
        return fail(400, "暂无菜谱，请先添加菜谱")
    one = random.choice(recipe_list)
    return success(one.to_dict())

# 3. 新增菜谱
@recipe_bp.route("/add", methods=["POST"])
def add_recipe():
    data = request.get_json()
    # 参数校验
    if not data.get("title"):
        return fail(400, "菜名不能为空")
    if not data.get("material"):
        return fail(400, "食材不能为空")
    if not data.get("step"):
        return fail(400, "步骤不能为空")

    new_recipe = Recipe(
        title=data["title"],
        material=data["material"],
        step=data["step"],
        tip=data.get("tip", ""),
        cover_img=data.get("cover_img", ""),
        category_id=data.get("category_id"),
        cook_time=data.get("cook_time", "")
    )
    db.session.add(new_recipe)
    db.session.commit()
    return success(new_recipe.to_dict(), msg="菜谱新增成功")

# 4. 编辑菜谱
@recipe_bp.route("/edit/<int:rid>", methods=["PUT"])
def edit_recipe(rid):
    recipe = Recipe.query.get(rid)
    if not recipe:
        return fail(404, "菜谱不存在")
    data = request.get_json()

    recipe.title = data.get("title", recipe.title)
    recipe.material = data.get("material", recipe.material)
    recipe.step = data.get("step", recipe.step)
    recipe.tip = data.get("tip", recipe.tip)
    recipe.cover_img = data.get("cover_img", recipe.cover_img)
    recipe.category_id = data.get("category_id", recipe.category_id)
    recipe.cook_time = data.get("cook_time", recipe.cook_time)

    db.session.commit()
    return success(recipe.to_dict(), msg="修改成功")

# 5. 删除菜谱
@recipe_bp.route("/delete/<int:rid>", methods=["DELETE"])
def delete_recipe(rid):
    recipe = Recipe.query.get(rid)
    if not recipe:
        return fail(404, "菜谱不存在")
    db.session.delete(recipe)
    db.session.commit()
    return success(msg="删除成功")

# 6. 收藏 / 取消收藏
@recipe_bp.route("/collect/<int:rid>", methods=["POST"])
def collect_recipe(rid):
    recipe = Recipe.query.get(rid)
    if not recipe:
        return fail(404, "菜谱不存在")
    # 取反
    recipe.is_collect = not recipe.is_collect
    db.session.commit()
    return success(recipe.to_dict(), msg="操作成功")

# 7. 获取所有收藏菜谱
@recipe_bp.route("/collect/list", methods=["GET"])
def get_collect_list():
    collect_list = Recipe.query.filter_by(is_collect=True).all()
    return success([item.to_dict() for item in collect_list])