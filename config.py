import os
from dotenv import load_dotenv

# 项目根目录（config.py 所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 根据环境加载不同的 .env 文件
_env_file = os.path.join(BASE_DIR, ".env.production") if os.getenv("FLASK_ENV") == "prod" else os.path.join(BASE_DIR, ".env")
if os.path.exists(_env_file):
    load_dotenv(_env_file)
else:
    load_dotenv()


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-123456")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 微信小程序配置（所有环境通用）
    WX_APPID = os.getenv("WX_APPID", "")
    WX_SECRET = os.getenv("WX_SECRET", "")
    # 微信 code2session 接口
    WX_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


class DevConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/data/cook.db"


class ProdConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or f"sqlite:///{BASE_DIR}/data/cook.db"


config = {
    "dev": DevConfig,
    "prod": ProdConfig
}
