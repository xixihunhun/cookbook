"""API 蓝图统一导出"""
from app.api.recipe import recipe_bp
from app.api.category import category_bp
from app.api.user import user_bp

__all__ = ["recipe_bp", "category_bp", "user_bp"]
