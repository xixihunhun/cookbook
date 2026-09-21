"""分类接口蓝图"""
from flask import Blueprint, request
from app import db
from app.models import Category, Recipe
from app.utils.response import success, fail

category_bp = Blueprint("category", __name__)


@category_bp.route("/list", methods=["GET"])
def get_category_list():
    """获取全部分类"""
    categories = Category.query.order_by(Category.id.asc()).all()
    return success([c.to_dict() for c in categories])


@category_bp.route("/add", methods=["POST"])
def add_category():
    """新增分类"""
    data = request.get_json()
    if not data:
        return fail(400, "请求体不能为空")

    name = data.get("name", "").strip()
    if not name:
        return fail(400, "分类名不能为空")
    if Category.query.filter_by(name=name).first():
        return fail(400, "分类名已存在")

    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    return success(category.to_dict(), msg="分类新增成功")


@category_bp.route("/edit/<int:cid>", methods=["PUT"])
def edit_category(cid):
    """修改分类"""
    category = Category.query.get(cid)
    if not category:
        return fail(404, "分类不存在")

    data = request.get_json()
    if not data:
        return fail(400, "请求体不能为空")

    name = data.get("name", "").strip()
    if not name:
        return fail(400, "分类名不能为空")
    if name != category.name and Category.query.filter_by(name=name).first():
        return fail(400, "分类名已存在")

    category.name = name
    db.session.commit()
    return success(category.to_dict(), msg="修改成功")


@category_bp.route("/delete/<int:cid>", methods=["DELETE"])
def delete_category(cid):
    """删除分类"""
    category = Category.query.get(cid)
    if not category:
        return fail(404, "分类不存在")

    if Recipe.query.filter_by(category_id=cid).first():
        return fail(400, "该分类下还有菜谱，无法删除")

    db.session.delete(category)
    db.session.commit()
    return success(msg="删除成功")
