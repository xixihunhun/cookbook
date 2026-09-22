from flask import Flask, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from config import config
import os

# 全局实例
db = SQLAlchemy()
migrate = Migrate()

def create_app(env="dev"):
    app = Flask(__name__, static_folder=None)

    # 前端构建产物目录
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

    # 初始化插件
    app.config.from_object(config[env])
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # 注册蓝图
    from app.api import recipe_bp, category_bp, user_bp, family_bp, vote_bp
    app.register_blueprint(recipe_bp, url_prefix="/api/recipe")
    app.register_blueprint(category_bp, url_prefix="/api/category")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(family_bp, url_prefix="/api/family")
    app.register_blueprint(vote_bp, url_prefix="/api/vote")

    # 健康检查
    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"})

    # SPA 前端路由
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve(path):
        # API 前缀不拦截
        if path.startswith("api/"):
            return jsonify({"msg": "not found"}), 404
        # 构建产物中存在的静态文件（如 assets/xxx.js）直接返回
        file_path = os.path.join(static_dir, path)
        if path and os.path.isfile(file_path):
            return send_from_directory(static_dir, path)
        # 其他情况都走 SPA fallback，返回 index.html
        # 开发阶段还没 build，index.html 不存在则返回提示
        if os.path.isfile(os.path.join(static_dir, "index.html")):
            return send_from_directory(static_dir, "index.html")
        return jsonify({
            "msg": "前端尚未构建，请先 cd web && npm run build",
            "api_docs": "/api/recipe/list"
        }), 200

    # 导入模型（在 create_app 内部，避免循环导入）
    from app import models  # noqa: F401

    return app
