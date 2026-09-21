from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from config import config

# 全局实例
db = SQLAlchemy()
migrate = Migrate()

def create_app(env="dev"):
    app = Flask(__name__)
    app.config.from_object(config[env])

    # 初始化插件
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # 注册蓝图（后面写菜谱接口用，先预留）
    from app.api.recipe import recipe_bp
    app.register_blueprint(recipe_bp, url_prefix="/api/recipe")

    # 基础路由
    @app.route("/")
    def index():
        return jsonify({"message": "欢迎来到 Cookbook API", "status": "ok"})

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"})

    return app

# =====新增这一行，加载模型，让migrate能识别到表！=====
from app import models    