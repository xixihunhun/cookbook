"""JWT 工具：生成 token / 验证 token / 登录装饰器"""
from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask import request, g, current_app

# token 有效期（秒），默认 7 天
TOKEN_EXPIRES = 7 * 24 * 60 * 60


def generate_token(user_id: int, username: str) -> str:
    """生成 JWT token"""
    payload = {
        "uid": user_id,
        "username": username,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRES),
    }
    secret = current_app.config["SECRET_KEY"]
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    """解码并验证 JWT token，失败返回 None"""
    try:
        secret = current_app.config["SECRET_KEY"]
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # token 已过期
    except jwt.InvalidTokenError:
        return None  # token 无效


def login_required(f):
    """登录验证装饰器：从 Authorization header 取 token 并验证"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            from app.utils.response import fail
            return fail(401, "请先登录")

        token = auth[7:]  # 去掉 "Bearer "
        payload = decode_token(token)
        if not payload:
            from app.utils.response import fail
            return fail(401, "登录已过期，请重新登录")

        # 把用户信息挂到 g 上，后续接口可以直接用 g.user_id / g.username
        g.user_id = payload["uid"]
        g.username = payload["username"]
        return f(*args, **kwargs)

    return wrapper
