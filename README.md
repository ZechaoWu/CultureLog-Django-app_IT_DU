# CultureLog

个人媒体追踪与评论平台，支持图书和电影的管理与评分。

## 技术栈

- **后端**：Python / Django 6.0.2
- **数据库**：SQLite3（开发）
- **前端**：HTML5 + CSS3（Ocean Depths 主题）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env` 文件并修改 `SECRET_KEY`：

```bash
cp .env .env.local
```

`.env` 内容说明：

```
SECRET_KEY=your-secret-key-here        # 必须修改
DEBUG=True                              # 生产环境设为 False
ALLOWED_HOSTS=localhost,127.0.0.1      # 生产环境填写实际域名
```

### 3. 初始化数据库

```bash
python manage.py migrate
python manage.py createsuperuser       # 可选：创建管理员账号
```

### 4. 启动开发服务器

```bash
python manage.py runserver
# 或使用 PowerShell 脚本：
.\run_server.ps1
```

访问 http://127.0.0.1:8000

## 项目结构

```
CultureLogDjango/
├── config/
│   ├── settings.py     # 项目配置（通过 .env 读取敏感变量）
│   └── urls.py         # URL 路由
├── core/
│   ├── models.py       # Genre / MediaItem / Review
│   ├── views.py        # 所有视图函数
│   ├── forms.py        # 注册 / 评论 / 媒体条目表单
│   ├── admin.py        # Admin 界面配置
│   ├── tests.py        # 单元测试与集成测试
│   ├── templates/
│   │   └── core/       # 页面模板
│   └── static/
│       └── core/css/   # 样式文件
├── templates/
│   ├── 404.html        # 自定义 404 页
│   └── 500.html        # 自定义 500 页
├── .env                # 本地环境变量（不提交到 Git）
├── .gitignore
└── requirements.txt
```

## URL 路由

| 路径 | 说明 |
|------|------|
| `/` | 主页 |
| `/browse/` | 浏览（支持搜索、筛选、分页）|
| `/item/<id>/` | 媒体详情 + 评论 |
| `/add/` | 添加媒体（需登录）|
| `/item/<id>/delete/` | 删除媒体（需登录）|
| `/review/<id>/edit/` | 编辑评论（仅作者）|
| `/register/` | 注册 |
| `/login/` | 登录 |
| `/logout/` | 退出 |
| `/profile/` | 个人主页（需登录）|
| `/admin/` | Django 管理后台 |

## 运行测试

```bash
python manage.py test core
```

## 生产部署注意事项

1. 将 `DEBUG` 设为 `False`
2. 修改 `SECRET_KEY` 为随机字符串（`python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
3. 配置 `ALLOWED_HOSTS` 为实际域名
4. 考虑将数据库从 SQLite 迁移至 PostgreSQL
5. 配置静态文件服务（`python manage.py collectstatic`）
