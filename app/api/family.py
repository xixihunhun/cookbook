"""家庭管理蓝图：创建 / 加入 / 退出 / 成员"""
import random
import string
from flask import Blueprint, request, g
from app import db
from app.models import User, Family, FamilyMember
from app.utils.response import success, fail
from app.utils.jwt_util import login_required

family_bp = Blueprint("family", __name__)


def _gen_invite_code() -> str:
    """生成 8 位邀请码（字母+数字，易读）"""
    chars = string.ascii_uppercase + string.digits
    while True:
        code = "".join(random.choices(chars, k=8))
        if not Family.query.filter_by(invite_code=code).first():
            return code


@family_bp.route("/create", methods=["POST"])
@login_required
def create_family():
    """创建家庭（同时加入自己）"""
    user = User.query.get(g.user_id)
    if not user:
        return fail(404, "用户不存在")

    # 已经有家庭了
    if user.family_id:
        return fail(400, "你已经在一个家庭中，请先退出")

    data = request.get_json() or {}
    name = (data.get("name") or "我们家").strip()

    family = Family(
        invite_code=_gen_invite_code(),
        name=name,
        creator_id=user.id,
    )
    db.session.add(family)
    db.session.flush()  # 拿到 family.id

    # 创建者自动加入
    member = FamilyMember(family_id=family.id, user_id=user.id, role="creator")
    db.session.add(member)

    # 绑定用户
    user.family_id = family.id

    db.session.commit()
    return success({
        "family": family.to_dict(),
        "member": member.to_dict(),
    }, msg="家庭创建成功")


@family_bp.route("/join", methods=["POST"])
@login_required
def join_family():
    """通过邀请码加入家庭"""
    user = User.query.get(g.user_id)
    if not user:
        return fail(404, "用户不存在")

    if user.family_id:
        return fail(400, "你已经在一个家庭中，请先退出")

    data = request.get_json() or {}
    code = (data.get("invite_code") or "").strip().upper()

    if not code:
        return fail(400, "邀请码不能为空")

    family = Family.query.filter_by(invite_code=code).first()
    if not family:
        return fail(404, "邀请码无效")

    # 已经在里面了
    if FamilyMember.query.filter_by(family_id=family.id, user_id=user.id).first():
        return fail(400, "你已经在这个家庭中了")

    # 超过 2 人（夫妻）
    if len(family.members) >= 2:
        return fail(400, "家庭已满（最多 2 人）")

    member = FamilyMember(family_id=family.id, user_id=user.id, role="member")
    user.family_id = family.id
    db.session.add(member)
    db.session.commit()

    return success({
        "family": family.to_dict(),
        "member": member.to_dict(),
    }, msg="加入成功")


@family_bp.route("/leave", methods=["POST"])
@login_required
def leave_family():
    """退出家庭"""
    user = User.query.get(g.user_id)
    if not user or not user.family_id:
        return fail(400, "你还没加入家庭")

    family = Family.query.get(user.family_id)
    if not family:
        user.family_id = None
        db.session.commit()
        return success(msg="退出成功")

    # 删除成员关系
    member = FamilyMember.query.filter_by(family_id=family.id, user_id=user.id).first()
    if member:
        db.session.delete(member)

    user.family_id = None

    # 如果没人了，删除家庭
    remaining = FamilyMember.query.filter_by(family_id=family.id).count()
    if remaining == 0:
        db.session.delete(family)

    db.session.commit()
    return success(msg="退出成功")


@family_bp.route("/mine", methods=["GET"])
@login_required
def get_my_family():
    """获取我所在的家庭 + 成员列表"""
    user = User.query.get(g.user_id)
    if not user or not user.family_id:
        return success({"family": None, "members": []})

    family = Family.query.get(user.family_id)
    if not family:
        return success({"family": None, "members": []})

    members = [m.to_dict() for m in family.members]
    return success({"family": family.to_dict(), "members": members})


@family_bp.route("/members", methods=["GET"])
@login_required
def list_members():
    """列出当前家庭的成员"""
    user = User.query.get(g.user_id)
    if not user or not user.family_id:
        return fail(400, "你还没加入家庭")

    family = Family.query.get(user.family_id)
    members = [m.to_dict() for m in family.members]
    return success(members)


@family_bp.route("/update", methods=["PUT"])
@login_required
def update_family():
    """修改家庭昵称"""
    user = User.query.get(g.user_id)
    if not user or not user.family_id:
        return fail(400, "你还没加入家庭")

    family = Family.query.get(user.family_id)
    # 只有创建者能改
    if family.creator_id != user.id:
        return fail(403, "只有创建者能修改家庭信息")

    data = request.get_json() or {}
    if "name" in data and data["name"].strip():
        family.name = data["name"].strip()

    db.session.commit()
    return success(family.to_dict(), msg="修改成功")
