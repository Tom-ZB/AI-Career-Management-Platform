# AI Career Management Platform

一个完整的、可实际运行的 AI Career Management Platform，用于个人职业管理、简历管理、求职申请管理以及 AI 辅助求职。

## 🚀 功能特性

- **个人职业档案管理**: 创建和管理你的职业档案
- **多版本简历管理**: 上传、创建和管理多个版本的 CV
- **职位机会管理**: 跟踪和管理你的工作机会
- **求职申请管理**: 跟踪你的求职申请状态
- **面试与跟进管理**: 安排面试和跟进记录
- **文档管理**: 上传和管理各类文档
- **数据分析仪表板**: 可视化你的求职进度和成功率
- **PDF/CSV 导出**: 导出数据和生成报告
- **AI 助手**:
  - CV 分析与改进建议
  - Cover Letter 自动生成
  - CV 与职位描述匹配分析
  - 自然语言查询（未来扩展）
  - AI 聊天助手（未来扩展）

## 🛠️ 技术栈

### Frontend
- **React** 18.3 + **TypeScript** 5.4
- **Vite** 5.2 - 快速的开发服务器
- **Tailwind CSS** 3.4 - 实用优先的 CSS 框架
- **shadcn/ui** - 现代化的 UI 组件库
- **TanStack Query** 5.30 - 强大的数据获取库
- **Zustand** 4.5 - 轻量级状态管理
- **React Router** 6.22 - 路由管理
- **React Hook Form** + **Zod** - 表单验证
- **Recharts** 2.12 - 数据可视化
- **Lucide React** - 图标库

### Backend
- **Python** 3.10+
- **FastAPI** 0.111 - 现代 Web 框架
- **SQLAlchemy** 2.0 - ORM
- **Alembic** 1.13 - 数据库迁移
- **Pydantic** 2.5 - 数据验证
- **LangChain** 0.1 - AI/LLM 集成
- **MySQL** - 关系型数据库
- **PyMuPDF** - PDF 解析
- **python-docx** - Word 文档解析
- **ReportLab** - PDF 生成

### AI
- **LangChain** 1.2 - LLM 编排框架
- **DeepSeek API** - LLM Provider（可配置）

## 📁 项目结构

```
AI Career Management Platform/
├── apps/
│   ├── frontend/           # React + TypeScript + Vite 前端应用
│   │   ├── src/
│   │   ├── public/
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── tailwind.config.js
│   │   └── tsconfig.json
│   │
│   └── backend/            # FastAPI + Python 后端应用
│       ├── backend/
│       │   ├── api/        # API 路由
│       │   ├── core/       # 核心配置
│       │   ├── crud/       # CRUD 操作
│       │   ├── models/     # SQLAlchemy 模型
│       │   ├── schemas/    # Pydantic schemas
│       │   ├── services/   # 业务逻辑
│       │   ├── utils/      # 工具函数
│       │   └── main.py     # FastAPI 应用入口
│       ├── alembic/        # 数据库迁移
│       ├── tests/          # 测试
│       └── requirements.txt
│
├── shared/                 # 共享类型和常量
├── docs/                   # 项目文档
├── package.json           # 根目录脚本
└── README.md
```

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- npm 或 yarn

### 安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd ai-career-management-platform
```

#### 2. 安装依赖
```bash
# 安装根目录依赖
npm install

# 安装前端依赖
cd apps/frontend
npm install

# 安装后端依赖
cd ../backend
pip install -r requirements.txt
```

#### 3. 配置环境变量
```bash
# 后端环境变量
cp apps/backend/.env.example apps/backend/.env
# 编辑 .env 文件，配置数据库和 API keys
```

#### 4. 数据库设置
```bash
# 创建 MySQL 数据库
mysql -u root -p -e "CREATE DATABASE ai_career_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行数据库迁移
cd apps/backend
alembic upgrade head
```

#### 5. 启动开发服务器
```bash
# 在项目根目录运行
npm run dev
```

- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 📝 环境变量配置

### Backend (.env)
```env
# 应用配置
APP_NAME="AI Career Management Platform"
DEBUG=True
SECRET_KEY=your-secret-key-here

# 数据库配置
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/ai_career_platform

# JWT 配置
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# DeepSeek API 配置
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat

# 文件存储配置
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./uploads
MAX_FILE_SIZE=10485760  # 10MB
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=AI Career Management Platform
```

## 🧪 测试

```bash
# 运行后端测试
cd apps/backend
pytest

# 运行前端测试
cd apps/frontend
npm test
```

## 📦 构建生产版本

```bash
# 构建前端
cd apps/frontend
npm run build

# 构建后端（可选，使用 Docker）
cd ..
docker-compose build
```

## 🚢 部署

### Docker 部署
```bash
docker-compose up -d
```

### 手动部署
参考 `docs/deployment.md` 获取详细部署指南。

## 📚 API 文档

启动后端后，访问以下地址查看 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 👥 作者

- 你的名字

## 🙏 致谢

感谢以下开源项目：
- FastAPI
- React
- Vite
- Tailwind CSS
- shadcn/ui
- LangChain

---

**注意**: 这是一个正在积极开发中的项目。功能可能会随时间变化。
