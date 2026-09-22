"""用户接口蓝图：微信登录 / 账号注册登录 / 个人信息"""
import requests as http_requests
from flask import Blueprint, request, g, current_app
from app import db
from app.models import User
from app.utils.response import success, fail
from app.utils.jwt_util import generate_token, login_required

user_bp = Blueprint("user", __name__)


# ============== 微信登录 ==============

@user_bp.route("/wx-login", methods=["POST"])
def wx_login():
    """
    微信小程序登录
    前端流程：wx.login() 拿 code → 调此接口 → 后端 code2session → 返回 token
    前端可选传 nickname / avatar（来自 getUserProfile）
    """
    data = request.get_json() or {}
    code = data.get("code", "").strip()
    nickname = data.get("nickname", "").strip()
    avatar = data.get("avatar", "").strip()

    # 判断是否走真实微信 code2session
    appid = current_app.config["WX_APPID"]
    secret = current_app.config["WX_SECRET"]
    has_wx_config = bool(appid and secret)

    if not code or not has_wx_config:
        # 模拟登录（H5/开发环境没微信 code，或没配 AppID/Secret）
        openid = f"dev_{code or 'anonymous'}"
        session_key = ""
        unionid = ""
    else:
        # 真实微信 code2session
        url = current_app.config["WX_CODE2SESSION_URL"]
        params = {
            "appid": appid,
            "secret": secret,
            "js_code": code,
            "grant_type": "authorization_code",
        }
        try:
            resp = http_requests.get(url, params=params, timeout=10)
            wx_data = resp.json()
        except Exception as e:
            return fail(500, f"微信接口调用失败: {e}")

        if "openid" not in wx_data:
            return fail(400, f"微信登录失败: {wx_data.get('errmsg', '未知错误')}")

        openid = wx_data["openid"]
        session_key = wx_data.get("session_key", "")
        unionid = wx_data.get("unionid", "")

    # 查用户
    user = User.query.filter_by(openid=openid).first()

    if user:
        # 老用户：更新最新的 session_key / 昵称头像
        user.session_key = session_key
        user.login_type = "wechat"
        if nickname:
            user.nickname = nickname
        if avatar:
            user.avatar = avatar
    else:
        # 新用户：创建
        user = User(
            openid=openid,
            unionid=unionid,
            session_key=session_key,
            username=f"wx_{openid[:8]}",     # 自动生成用户名
            nickname=nickname or f"食客{openid[-4:]}",
            avatar=avatar,
            login_type="wechat",
        )
        db.session.add(user)

    db.session.commit()
    token = generate_token(user.id, user.username or user.openid)
    return success({
        "token": token,
        "user": user.to_dict(),
        "is_new": user.created_at == user.updated_at,  # 简单判断是否新注册
    }, msg="登录成功")


# ============== 账号注册（可选，开发用）==============

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
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

    token = generate_token(user.id, user.username)
    return success({
        "token": token,
        "user": user.to_dict(),
    }, msg="注册成功")


# ============== 账号登录（可选，开发用）==============

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
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


# ============== 个人信息 ==============

@user_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    user = User.query.get(g.user_id)
    if not user:
        return fail(404, "用户不存在")
    return success(user.to_dict())


@user_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    user = User.query.get(g.user_id)
    if not user:
        return fail(404, "用户不存在")

    data = request.get_json() or {}

    if "nickname" in data and data["nickname"].strip():
        user.nickname = data["nickname"].strip()

    if "avatar" in data:
        user.avatar = data.get("avatar", "")

    if "bio" in data:
        user.bio = data.get("bio", "")

    db.session.commit()
    return success(user.to_dict(), msg="修改成功")
