import os
from dotenv import load_dotenv

# 项目根目录（config.py 所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 根据环境加载不同的 .env 文件
# 优先级：.env.production > .env
_env_file = os.path.join(BASE_DIR, ".env.production") if os.getenv("FLASK_ENV") == "prod" else os.path.join(BASE_DIR, ".env")
if os.path.exists(_env_file):
    load_dotenv(_env_file)
else:
    load_dotenv()  # 兜底：加载默认 .env


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-123456")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(BaseConfig):
    DEBUG = True
    # SQLite本地数据库，绝对路径避免相对路径问题
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/data/cook.db"


class ProdConfig(BaseConfig):
    DEBUG = False
    # 线上环境从环境变量读取数据库地址，不硬编码
    # 没配 DATABASE_URL 时回退到 SQLite（方便本地测试 --prod）
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or f"sqlite:///{BASE_DIR}/data/cook.db"


# 环境映射
config = {
    "dev": DevConfig,
    "prod": ProdConfig
}
