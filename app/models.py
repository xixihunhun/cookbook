from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# ============== 用户 ==============

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(64))
    avatar = db.Column(db.String(256))
    bio = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname or self.username,
            "avatar": self.avatar,
            "bio": self.bio,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============== 菜谱分类 ==============
class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    # 关联：一个分类下多个菜谱
    recipes = db.relationship("Recipe", backref="category", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

# 菜谱表
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
    cook_time = db.Column(db.String(50)) # 单位：分钟s

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
            "cook_time": self.cook_time # 记得在to_dict增加返回字段！
        }