"""无 debug 启动 Flask（绕过 reloader 的沙箱问题）"""
from app import create_app, db
app = create_app("dev")
with app.app_context():
    db.create_all()
print("[Flask] http://0.0.0.0:5000  debug=False")
app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False, threaded=True)
