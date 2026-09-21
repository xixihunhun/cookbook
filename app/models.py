from app import db

# 菜谱分类表
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