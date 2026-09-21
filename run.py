"""Flask 应用启动入口
开发环境：python3 run.py          （Flask 自带服务器，支持热重载）
生产环境：python3 run.py --prod    （Gunicorn / Waitress，自动适配系统）
"""
import os
import sys
from app import create_app, db
from app import models  # noqa: F401  # 导入模型以便 flask-migrate 识别

# 判断环境
is_prod = "--prod" in sys.argv
env = "prod" if is_prod else "dev"

app = create_app(env)

# 开发环境自动建表（生产环境用 flask-migrate）
if not is_prod:
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))

    if is_prod:
        # 生产环境：优先 Gunicorn（Linux/macOS），回退 Waitress（Windows）
        workers = int(os.getenv("WORKERS", 4))
        try:
            from gunicorn.app.base import BaseApplication

            class GunicornApp(BaseApplication):
                def __init__(self, flask_app, options=None):
                    self.flask_app = flask_app
                    self.options = options or {}
                    super().__init__()

                def load_config(self):
                    for k, v in self.options.items():
                        self.cfg.set(k.lower(), v)

                def load(self):
                    return self.flask_app

            GunicornApp(app, {
                "bind": f"{host}:{port}",
                "workers": workers,
                "accesslog": "-",
                "errorlog": "-",
            }).run()

        except ImportError:
            try:
                from waitress import serve
                print(f"[生产] Waitress 启动中 http://{host}:{port}")
                serve(app, host=host, port=port)
            except ImportError:
                print("⚠ 未安装 Gunicorn 或 Waitress，回退到 Flask 开发服务器")
                print("  安装：pip install gunicorn (macOS/Linux) 或 pip install waitress (Windows)")
                app.run(host=host, port=port)
    else:
        # 开发环境：Flask 自带服务器（支持热重载）
        print(f"[开发] Flask 启动中 http://{host}:{port}  (Ctrl+C 退出)")
        app.run(host=host, port=port, debug=True)
