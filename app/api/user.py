"""用户接口蓝图：注册 / 登录 / 个人信息"""
from flask import Blueprint, request, g
from app import db
from app.models import User
from app.utils.response import success, fail
from app.utils.jwt_util import generate_token, login_required

user_bp = Blueprint("user", __name__)


@user_bp.route("/register", methods=["POST"])
def register():
    """用户注册"""
    data = request.get_json()
    if not data:
        return fail(400, "请求体不能为空")

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if len(username) < 3:
        return fail(400, "用户名至少3个字符")
    if len(password) < 6:
        return fail(400, "密码至少6个字符")
    if User.query.filter_by(username=username).first():
        return fail(400, "用户名已存在")

    user = User(username=username, nickname=data.get("nickname") or username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return success(user.to_dict(), msg="注册成功")


@user_bp.route("/login", methods=["POST"])
def login():
    """用户登录（返回 JWT token）"""
    data = request.get_json()
    if not data:
        return fail(400, "请求体不能为空")

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return fail(400, "用户名和密码不能为空")

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return fail(401, "用户名或密码错误")

    token = generate_token(user.id, user.username)
    return success({
        "token": token,
        "user": user.to_dict(),
    }, msg="登录成功")


@user_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    """获取当前登录用户的个人信息"""
    user = User.query.get(g.user_id)
    if not user:
        return fail(404, "用户不存在")
    return success(user.to_dict())


@user_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    """修改当前登录用户的个人信息"""
    user = User.query.get(g.user_id)
    if not user:
        return fail(404, "用户不存在")

    data = request.get_json()
    if not data:
        return fail(400, "请求体不能为空")

    if "nickname" in data:
        nickname = data["nickname"].strip()
        if not nickname:
            return fail(400, "昵称不能为空")
        user.nickname = nickname

    if "avatar" in data:
        user.avatar = data.get("avatar", "")

    if "bio" in data:
        user.bio = data.get("bio", "")

    if "password" in data:
        new_pwd = data["password"].strip()
        if len(new_pwd) < 6:
            return fail(400, "密码至少6个字符")
        user.set_password(new_pwd)

    db.session.commit()
    return success(user.to_dict(), msg="修改成功")
