from app import db
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

# ============== 用户 ==============

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)       # 账号登录用（可选）
    password_hash = db.Column(db.String(256))                           # 账号密码（可选）
    nickname = db.Column(db.String(64))
    avatar = db.Column(db.String(512))                                  # 微信头像 URL
    openid = db.Column(db.String(128), unique=True, index=True)         # 微信 openid（唯一）
    unionid = db.Column(db.String(128))                                  # 微信 unionid
    session_key = db.Column(db.String(128))                             # 微信 session_key
    login_type = db.Column(db.String(16), default="wechat")             # wechat / account
    bio = db.Column(db.String(500))
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"))       # 所属家庭
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
        self.login_type = "account"

    def check_password(self, password: str) -> bool:
        return self.password_hash and check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname or "未命名",
            "avatar": self.avatar,
            "bio": self.bio,
            "login_type": self.login_type,
            "family_id": self.family_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============== 家庭（夫妻/情侣绑定） ==============

class Family(db.Model):
    __tablename__ = "family"

    id = db.Column(db.Integer, primary_key=True)
    invite_code = db.Column(db.String(16), unique=True, nullable=False, index=True)
    name = db.Column(db.String(50))                                      # 家庭昵称（如"老王一家"）
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))          # 创建者
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 成员列表
    members = db.relationship("FamilyMember", backref="family", lazy=True, cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "invite_code": self.invite_code,
            "name": self.name or "我们家",
            "creator_id": self.creator_id,
            "member_count": len(self.members),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class FamilyMember(db.Model):
    """家庭成员关系"""
    __tablename__ = "family_member"

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    role = db.Column(db.String(16), default="member")                    # creator / member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("family_id", "user_id", name="uq_family_user"),)

    user = db.relationship("User", backref="member_relations", lazy=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "family_id": self.family_id,
            "user_id": self.user_id,
            "role": self.role,
            "nickname": self.user.nickname if self.user else None,
            "avatar": self.user.avatar if self.user else None,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
        }


# ============== 菜谱分类 ==============

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    recipes = db.relationship("Recipe", backref="category", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }


# ============== 菜谱 ==============

class Recipe(db.Model):
    __tablename__ = "recipe"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    material = db.Column(db.Text, nullable=False)
    step = db.Column(db.Text, nullable=False)
    tip = db.Column(db.String(300))
    cover_img = db.Column(db.String(255))
    is_collect = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    cook_time = db.Column(db.String(50))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = db.relationship("User", backref="recipes", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "material": self.material,
            "step": self.step,
            "tip": self.tip,
            "cover_img": self.cover_img,
            "is_collect": self.is_collect,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "cook_time": self.cook_time,
            "author_id": self.author_id,
            "author_name": self.author.nickname if self.author else None,
            "views": self.views or 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# ============== 每日抽签投票 ==============

class DailyVote(db.Model):
    """每日抽签投票：一家人今天吃什么"""
    __tablename__ = "daily_vote"

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)
    vote_date = db.Column(db.Date, nullable=False, default=date.today)
    voter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    voted_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("family_id", "recipe_id", "vote_date", "voter_id", name="uq_daily_vote"),
    )

    recipe = db.relationship("Recipe", lazy=True)
    voter = db.relationship("User", lazy=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "family_id": self.family_id,
            "recipe_id": self.recipe_id,
            "recipe_title": self.recipe.title if self.recipe else None,
            "recipe_cover": self.recipe.cover_img if self.recipe else None,
            "vote_date": self.vote_date.isoformat() if self.vote_date else None,
            "voter_id": self.voter_id,
            "voter_nickname": self.voter.nickname if self.voter else None,
            "voted_at": self.voted_at.isoformat() if self.voted_at else None,
        }
