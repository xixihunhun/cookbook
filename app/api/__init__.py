"""API 蓝图统一导出"""
from app.api.recipe import recipe_bp
from app.api.category import category_bp
from app.api.user import user_bp
from app.api.family import family_bp
from app.api.vote import vote_bp

__all__ = ["recipe_bp", "category_bp", "user_bp", "family_bp", "vote_bp"]
