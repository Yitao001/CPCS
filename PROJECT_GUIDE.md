# 大学生职业规划智能体 - 项目开发指南（小白版）

## 目录
1. [项目介绍](#1-项目介绍)
2. [环境准备](#2-环境准备)
3. [项目架构理解](#3-项目架构理解)
4. [从零开始开发](#4-从零开始开发)
5. [核心功能开发](#5-核心功能开发)
6. [常见问题解答](#6-常见问题解答)

---

## 1. 项目介绍

### 1.1 项目是什么？

这是一个**基于 AI 的大学生职业规划智能体**，可以帮助学生：

| 功能 | 说明 |
|------|------|
| 岗位画像查询 | 了解 12 个计算机类岗位的要求 |
| 能力画像分析 | 分析自己的技能和能力 |
| 人岗匹配 | 看看自己适合什么岗位 |
| 职业规划 | 生成职业发展路径和学习计划 |
| 报告导出 | 导出精美的职业发展报告 |

### 1.2 为什么要做这个项目？

- 很多大学生不知道自己未来做什么工作
- 不知道岗位需要什么技能
- 需要一个智能工具来辅助职业规划

### 1.3 技术栈（小白也能懂）

| 技术 | 作用 | 难度 |
|------|------|------|
| Python | 编程语言 | ⭐ |
| FastAPI | 快速搭建 API 接口 | ⭐⭐ |
| LangChain | 连接 AI 大模型 | ⭐⭐⭐ |
| JSON | 存储数据的格式 | ⭐ |

---

## 2. 环境准备

### 2.1 安装 Python

#### Windows
1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.8 或更高版本
3. 安装时**务必勾选** "Add Python to PATH"
4. 验证安装：
```bash
python --version
```

#### 验证是否成功
打开命令行（Windows 按 Win+R，输入 cmd），输入：
```bash
python --version
pip --version
```

如果显示版本号，说明安装成功！

### 2.2 获取项目代码

#### 方式一：从 Git 仓库克隆
```bash
git clone <你的仓库地址>
cd CareerPlanningAgent
```

#### 方式二：直接下载
1. 下载 ZIP 压缩包
2. 解压到某个文件夹
3. 进入解压后的目录

### 2.3 安装依赖包

在项目目录下运行：
```bash
pip install -r requirements.txt
```

如果下载很慢，可以使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2.4 配置 API Key

#### 第一步：复制配置文件
```bash
cp .env.example .env
```

#### 第二步：获取 API Key（以 SiliconFlow 为例）

1. 访问 https://cloud.siliconflow.cn/
2. 注册/登录账号
3. 进入 "API Key" 管理页面
4. 创建新的 API Key
5. 复制这个 Key（格式：sk-xxxxxxxxxx）

#### 第三步：编辑 .env 文件

用记事本或 VS Code 打开 `.env` 文件，修改以下内容：

```env
MODEL_PROVIDER=siliconflow
CHAT_MODEL_NAME=siliconflow/deepseek-ai/DeepSeek-V3
SILICONFLOW_API_KEY=sk-你的APIKey粘贴在这里
```

### 2.5 测试一下

运行测试脚本：
```bash
python test_simple.py
```

如果看到"[OK]"，说明环境配置成功！

---

## 3. 项目架构理解

### 3.1 整体结构（像公司一样理解）

```
CareerPlanningAgent/          # 公司总部
├── api.py                     # 前台接待（处理请求）
├── agent/                     # 核心业务部门
│   ├── react_agent.py        # 部门经理（协调工作）
│   └── tools/
│       ├── agent_tools.py    # 业务工具（职业测评、课程推荐）
│       ├── enhanced_tools.py # 高级工具（人岗匹配、报告导出）
│       └── middleware.py     # 监控（记录日志）
├── data/                      # 档案室（存储数据）
│   ├── data_manager.py       # 档案管理员
│   └── job_data/             # 岗位档案
│       └── job_portraits.json # 12个岗位的详细资料
├── model/                     # AI 顾问（大模型）
│   └── factory.py            # 顾问管理
├── prompts/                   # 提问模板（如何问 AI）
├── utils/                     # 后勤部门
│   ├── config_handler.py     # 配置管理
│   └── logger_handler.py     # 日志记录
├── config/                    # 公司规定
├── .env                       # 机密文件（API Key）
└── test_*.py                  # 测试员（检查功能）
```

### 3.2 工作流程（举个例子）

**场景：学生问"我适合什么岗位？"**

```
1. 学生访问 /api/assessment
   ↓
2. api.py（前台）接收请求
   ↓
3. react_agent.py（经理）处理
   ↓
4. agent_tools.py（工具）调用职业测评
   ↓
5. model/factory.py（AI 顾问）分析
   ↓
6. 返回结果给学生
```

### 3.3 核心文件说明

| 文件 | 作用 | 重要程度 |
|------|------|----------|
| `api.py` | API 接口入口 | ⭐⭐⭐⭐⭐ |
| `agent/react_agent.py` | 智能体核心 | ⭐⭐⭐⭐⭐ |
| `agent/tools/agent_tools.py` | 基础工具 | ⭐⭐⭐⭐ |
| `agent/tools/enhanced_tools.py` | 增强工具 | ⭐⭐⭐⭐ |
| `data/data_manager.py` | 数据管理 | ⭐⭐⭐⭐ |
| `data/job_data/job_portraits.json` | 岗位数据 | ⭐⭐⭐⭐⭐ |
| `model/factory.py` | 模型工厂 | ⭐⭐⭐⭐ |
| `utils/config_handler.py` | 配置管理 | ⭐⭐⭐ |
| `.env` | 环境配置 | ⭐⭐⭐⭐⭐ |

---

## 4. 从零开始开发

### 4.1 第一步：搭建项目骨架

#### 4.1.1 创建项目目录

```bash
mkdir CareerPlanningAgent
cd CareerPlanningAgent
```

#### 4.1.2 创建 requirements.txt

这个文件列出了项目需要的所有 Python 库：

```txt
fastapi>=0.100.0
uvicorn>=0.23.2
python-dotenv>=1.0.0
langchain>=0.1.0
langchain-openai>=0.0.5
pydantic>=2.0.0
python-multipart>=0.0.6
httpx>=0.24.0
cachetools>=5.3.0
```

#### 4.1.3 创建 .env.example

配置文件模板：

```env
MODEL_PROVIDER=siliconflow
CHAT_MODEL_NAME=siliconflow/deepseek-ai/DeepSeek-V3
SILICONFLOW_API_KEY=your_api_key_here
HOST=0.0.0.0
PORT=8000
```

### 4.2 第二步：创建模型工厂

在 `model/` 目录下创建 `factory.py`，用来加载不同的 AI 模型。

### 4.3 第三步：创建岗位数据

在 `data/job_data/` 目录下创建 `job_portraits.json`，存储岗位信息。

### 4.4 第四步：创建 API 服务

创建 `api.py`，使用 FastAPI 搭建接口。

### 4.5 第五步：测试运行

```bash
python api.py
```

访问 http://localhost:8000/docs 看看是否成功！

---

## 5. 核心功能开发

### 5.1 功能一：岗位画像管理

#### 需求
- 存储 10+ 个岗位的信息
- 每个岗位包含技能、证书、能力要求
- 支持查询岗位和发展路径

#### 数据结构（JSON 格式）

```json
{
  "job_code": "DEV001",
  "job_name": "Java后端开发工程师",
  "category": "后端开发",
  "professional_skills": ["Java", "Spring Boot", "MySQL"],
  "certificates": ["Java SE", "软考中级"],
  "abilities": {
    "innovation": 7,
    "learning": 8,
    "stress": 8,
    "communication": 6,
    "internship": 7
  },
  "vertical_path": [
    "Java后端开发工程师",
    "高级Java后端开发工程师",
    "Java技术专家/架构师",
    "技术总监"
  ],
  "job_change_paths": [
    "大数据开发工程师",
    "全栈开发工程师"
  ]
}
```

#### 实现步骤

1. 创建 `data/job_data/job_portraits.json`
2. 编写 `data/data_manager.py` 读取数据
3. 在 `api.py` 添加接口

### 5.2 功能二：人岗匹配（核心）

#### 需求
- 输入学生能力和目标岗位
- 计算匹配度
- 给出差距分析和改进建议

#### 算法思路

```
匹配度 = (技能匹配度 × 0.4) + (能力匹配度 × 0.3) + (经验匹配度 × 0.3)

技能匹配度：学生掌握的技能 / 岗位要求的技能 × 100%
能力匹配度：学生各项能力平均分 / 岗位要求平均分 × 100%
经验匹配度：根据实习经历评分
```

#### 实现代码（简化版）

```python
def calculate_matching(student, job):
    skill_match = len(set(student['skills']) & set(job['skills'])) / len(job['skills'])
    
    ability_student = sum(student['abilities'].values()) / len(student['abilities'])
    ability_job = sum(job['abilities'].values()) / len(job['abilities'])
    ability_match = min(ability_student / ability_job, 1.0)
    
    total_score = skill_match * 0.4 + ability_match * 0.3 + 0.3  # 假设经验满分
    
    return {
        'total_score': round(total_score * 100, 1),
        'skill_match': round(skill_match * 100, 1),
        'ability_match': round(ability_match * 100, 1),
        'gaps': find_gaps(student, job)
    }
```

### 5.3 功能三：报告导出

#### 需求
- 生成 Markdown 格式报告
- 生成 HTML 格式报告
- 支持下载

#### Markdown 报告模板

```markdown
# 职业发展报告

## 学生信息
- 姓名：张三
- 专业：计算机科学与技术
- 年级：大三

## 人岗匹配分析
- 匹配度：85.5分

## 行动计划
### 短期（3个月）
- 学习 Spring Boot
- 完成一个项目

### 中期（6个月）
- 寻找实习机会
- 考取 Java 证书
```

---

## 6. 常见问题解答

### 6.1 开发常见问题

**Q: 我看不懂代码怎么办？**
```
A: 
1. 先看这个文档理解整体架构
2. 从简单的文件开始看（如 test_simple.py）
3. 打印变量看看里面是什么
4. 加注释帮助理解
```

**Q: 如何添加新的岗位？**
```
A: 
1. 打开 data/job_data/job_portraits.json
2. 复制一个现有岗位的结构
3. 修改内容
4. 保存即可
```

**Q: 如何修改 API 端口？**
```
A: 编辑 .env 文件，修改 PORT=9000
```

**Q: 代码报错怎么办？**
```
A: 
1. 看错误信息的最后一行
2. 搜索错误关键词
3. 检查 .env 配置是否正确
4. 运行 test_simple.py 看看基础功能是否正常
```

### 6.2 小白学习路线

#### 第一周：环境和基础
- [ ] 安装 Python
- [ ] 运行项目
- [ ] 看懂项目结构
- [ ] 运行测试脚本

#### 第二周：理解代码
- [ ] 读懂 api.py
- [ ] 读懂 data_manager.py
- [ ] 理解岗位数据结构
- [ ] 尝试修改岗位数据

#### 第三周：修改功能
- [ ] 添加一个新岗位
- [ ] 修改匹配算法
- [ ] 修改报告模板
- [ ] 测试自己的修改

#### 第四周：扩展功能
- [ ] 添加新的 API 接口
- [ ] 集成新的 AI 模型
- [ ] 优化界面（如果有前端）
- [ ] 部署到服务器

---

## 7. 学习资源

### 7.1 Python 入门
- 廖雪峰 Python 教程：https://www.liaoxuefeng.com/wiki/1016959663602400
- Python 官方文档：https://docs.python.org/zh-cn/3/

### 7.2 FastAPI 入门
- FastAPI 官方文档：https://fastapi.tiangolo.com/zh/
- FastAPI 中文教程：https://fastapi.tiangolo.com/zh/tutorial/

### 7.3 LangChain 入门
- LangChain 官方文档：https://python.langchain.com/
- LangChain 中文教程：https://www.langchain.com.cn/

---

## 8. 总结

恭喜你！看完这份文档，你应该能够：

- [ ] 理解项目整体架构
- [ ] 配置开发环境
- [ ] 运行和测试项目
- [ ] 修改简单的功能
- [ ] 添加新的岗位数据

下一步：
1. 动手运行项目试试看
2. 阅读代码，加注释帮助理解
3. 尝试修改一些功能
4. 有问题随时查文档或问 AI

祝你开发顺利！🎉
