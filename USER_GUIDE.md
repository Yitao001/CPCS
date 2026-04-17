# 大学生职业规划智能体 - 使用指南

## 目录
1. [快速开始](#1-快速开始)
2. [环境配置](#2-环境配置)
3. [功能使用](#3-功能使用)
4. [API接口说明](#4-api接口说明)
5. [常见问题](#5-常见问题)

---

## 1. 快速开始

### 1.1 前提条件
- Python 3.8 或更高版本
- 至少 4GB 内存
- 有效的 API Key（推荐 SiliconFlow）

### 1.2 三步快速上手

```bash
# 第一步：进入项目目录
cd CareerPlanningAgent

# 第二步：安装依赖
pip install -r requirements.txt

# 第三步：运行演示
python demo_enhanced_features.py
```

---

## 2. 环境配置

### 2.1 配置文件说明

项目使用 `.env` 文件进行配置，请先复制示例文件：

```bash
cp .env.example .env
```

### 2.2 编辑 .env 文件

打开 `.env` 文件，配置以下内容：

#### 模型配置（必填）

**方式一：使用 SiliconFlow（推荐，免费额度多）**
```env
MODEL_PROVIDER=siliconflow
CHAT_MODEL_NAME=siliconflow/deepseek-ai/DeepSeek-V3
SILICONFLOW_API_KEY=sk-你的APIKey
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
```

**方式二：使用通义千问**
```env
MODEL_PROVIDER=tongyi
CHAT_MODEL_NAME=qwen-max
DASHSCOPE_API_KEY=你的APIKey
```

#### 服务配置
```env
HOST=0.0.0.0
PORT=9000
```

#### API 安全配置（可选）
```env
API_KEY=your_secure_api_key_here
CORS_ORIGINS=*
RATE_LIMIT_PER_MINUTE=60
```

### 2.3 获取 API Key

#### SiliconFlow
1. 访问 https://cloud.siliconflow.cn/
2. 注册/登录账号
3. 进入"API Key"管理页面
4. 创建新的 API Key
5. 复制到 `.env` 文件

#### 通义千问
1. 访问 https://dashscope.console.aliyun.com/
2. 注册/登录阿里云账号
3. 创建 API Key
4. 复制到 `.env` 文件

---

## 3. 功能使用

### 3.1 测试脚本使用

#### 基础测试
```bash
python test_simple.py
```
测试内容：
- 模型加载
- 系统提示词加载
- 岗位画像加载
- Agent 初始化

#### 增强功能演示
```bash
python demo_enhanced_features.py
```
展示增强后的核心功能：
- 智能人岗匹配
- 详细行动计划
- 精美报告导出

### 3.2 启动 API 服务

#### 方式一：直接运行
```bash
python api.py
```

#### 方式二：使用 Uvicorn
```bash
uvicorn api:app --host 0.0.0.0 --port 9000 --reload
```

服务启动后，访问以下地址：
- API 文档（Swagger UI）：http://localhost:9000/docs
- API 文档（ReDoc）：http://localhost:9000/redoc
- 健康检查：http://localhost:9000/health

### 3.3 使用 Swagger UI 测试

1. 打开浏览器访问 http://localhost:9000/docs
2. 点击任意接口展开
3. 点击 "Try it out"
4. 填写请求参数
5. 点击 "Execute" 执行
6. 查看返回结果

---

## 4. API 接口说明

### 4.1 岗位画像接口

#### 获取所有岗位列表
```http
GET /jobs
```

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "job_code": "DEV001",
      "job_name": "Java后端开发工程师",
      "category": "后端开发"
    }
  ]
}
```

#### 获取岗位画像
```http
GET /jobs/{job_identifier}
```

**参数：**
- `job_identifier`：岗位名称 或 岗位编码

**示例：**
```http
GET /jobs/Java后端开发工程师
GET /jobs/DEV001
```

#### 获取岗位关联图谱
```http
GET /jobs/{job_identifier}/relations
```

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "vertical_path": [
      "Java后端开发工程师",
      "高级Java后端开发工程师",
      "Java技术专家/架构师",
      "技术总监"
    ],
    "job_change_paths": [
      "大数据开发工程师",
      "全栈开发工程师",
      "技术项目经理"
    ]
  }
}
```

### 4.2 学生能力画像接口

#### 解析简历
```http
POST /parse-resume
Content-Type: application/json

{
  "resume_content": "张三，计算机科学与技术专业，大三学生。熟练掌握Java、Python、MySQL等技术，有3个月的实习经验。",
  "student_id": "2023001"
}
```

#### 获取学生能力画像
```http
GET /students/{student_id}/profile
```

### 4.3 人岗匹配接口

```http
POST /job-matching
Content-Type: application/json

{
  "student_id": "2023001",
  "job_name": "Java后端开发工程师"
}
```

### 4.4 职业发展报告接口

#### 生成职业发展报告
```http
POST /career-report
Content-Type: application/json

{
  "student_id": "2023001",
  "student_info": "大三，计算机专业，Java方向",
  "job_name": "Java后端开发工程师"
}
```

#### 导出职业发展报告
```http
POST /export-report
Content-Type: application/json

{
  "student_id": "2023001",
  "format": "markdown"
}
```

**格式选项：**
- `markdown`：Markdown 格式
- `html`：HTML 格式
- `json`：JSON 格式

### 4.5 其他接口

#### 职业测评
```http
POST /assessment
Content-Type: application/json

{
  "student_info": "大三，计算机专业，喜欢编程，对人工智能感兴趣",
  "student_name": "张三"
}
```

#### 课程推荐
```http
POST /course-recommendation
Content-Type: application/json

{
  "student_info": "大三，计算机专业，想做前端开发",
  "career_goal": "成为一名优秀的前端工程师"
}
```

#### 就业指导
```http
POST /job-guidance
Content-Type: application/json

{
  "student_info": "大四，计算机专业，准备找工作",
  "target_position": "Java后端开发工程师"
}
```

#### 智能对话
```http
POST /chat
Content-Type: application/json

{
  "message": "我是计算机专业的学生，不知道未来该做什么方向"
}
```

---

## 5. 常见问题

### 5.1 安装问题

**Q: pip install 失败怎么办？**
```
A: 尝试使用国内镜像源：
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**Q: 提示缺少某个模块？**
```
A: 确保在项目根目录运行，并且已安装所有依赖：
pip install -r requirements.txt
```

### 5.2 配置问题

**Q: API Key 怎么获取？**
```
A: 
- SiliconFlow：https://cloud.siliconflow.cn/
- 通义千问：https://dashscope.console.aliyun.com/
注册账号后创建 API Key 即可
```

**Q: 模型加载失败？**
```
A: 检查以下几点：
1. API Key 是否正确配置
2. 网络连接是否正常
3. 账户是否有余额/额度
4. .env 文件格式是否正确
```

### 5.3 运行问题

**Q: 端口被占用？**
```
A: 修改 .env 文件中的 PORT，或杀掉占用进程：
Windows: netstat -ano | findstr :9000
Linux: lsof -i :9000
```

**Q: 测试脚本报错？**
```
A: 
1. 确保在项目根目录下运行
2. 检查 Python 版本 >= 3.8
3. 查看错误日志，根据提示修复
4. 运行 test_simple.py 先做基础测试
```

### 5.4 使用问题

**Q: 如何使用增强功能？**
```
A: 
1. 运行 demo_enhanced_features.py 查看演示
2. 查看 agent/tools/enhanced_tools.py 了解实现
3. 集成到自己的代码中使用
```

**Q: 生成的报告在哪里？**
```
A: 
- Markdown: demo_career_report.md
- HTML: demo_career_report.html
都在项目根目录下
```

**Q: 如何扩展岗位画像？**
```
A: 编辑 data/job_data/job_portraits.json 文件，
按照现有格式添加新的岗位画像即可。
```

---

## 6. 更多帮助

- 项目开发指南：`PROJECT_GUIDE.md`
- 部署指南：`DEPLOYMENT_GUIDE.md`

祝您使用愉快！
