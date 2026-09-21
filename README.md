cook_book/
├── .gitignore
├── requirements.txt
├── .env                # 环境变量，不提交git
├── config.py           # 配置：dev / prod
├── run.py              # 项目入口
├── app/
│   ├── __init__.py     # Flask工厂函数
│   ├── models.py       # 数据库模型
│   ├── utils/          # 工具：统一返回、日志、参数校验
│   │   ├── __init__.py
│   │   ├── response.py
│   │   └── logger.py
│   ├── api/            # 接口蓝图
│   │   ├── __init__.py
│   │   ├── recipe.py   # 菜谱接口
│   │   └── category.py # 菜谱分类接口
│   └── static/         # 上传图片存放目录
│       └── upload/
├── migrations/         # flask-migrate 数据库迁移文件
└── data/
    └── cook.db         # SQLite本地数据库

cook_miniprogram/       # 微信小程序前端（独立文件夹）
├── .gitignore
├── app.js
├── app.json
├── app.wxss
├── pages/
│   ├── index/          # 首页：随机推荐 + 菜谱列表
│   ├── add/            # 新增/编辑菜谱
│   ├── detail/         # 菜谱详情
│   ├── collect/        # 我的收藏
│   └── category/       # 分类筛选
├── components/         # 公共组件：菜谱卡片
└── utils/
    └── request.js      # 封装wx.request