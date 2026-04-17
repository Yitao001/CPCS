# 大学生职业规划智能体 - API 接口文档

## 目录
1. [基础信息](#1-基础信息)
2. [认证方式](#2-认证方式)
3. [接口列表](#3-接口列表)
4. [接口详情](#4-接口详情)
5. [调用示例](#5-调用示例)
6. [常见问题](#6-常见问题)

---

## 1. 基础信息

| 项目 | 说明 |
|------|------|
| **API 地址** | `http://47.111.160.196:9000` |
| **协议** | HTTP |
| **数据格式** | JSON |
| **字符编码** | UTF-8 |

---

## 2. 认证方式

当前无需认证（可在 `.env` 中配置 `API_KEY` 启用认证。

---

## 3. 接口列表

| 接口 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/jobs` | GET | 获取岗位列表 |
| `/jobs/{id` | GET | 获取岗位详情 |
| `/jobs/search` | POST | 搜索岗位（RAG 检索） |
| `/parse-resume` | POST | 解析简历生成学生画像 |
| `/job-matching` | POST | 人岗匹配分析 |
| `/career-report` | POST | 生成职业发展报告 |
| `/export-report` | POST | 导出职业发展报告 |
| `/chat` | POST | 智能对话 |

---

## 4. 接口详情

### 4.1 健康检查

**接口**：`GET /health`

**请求示例**：
```
GET http://47.111.160.196:9000/health
```

**响应示例**：
```json
{
  "status": "ok",
  "service": "career-planning-agent",
  "llm_connected": true
}
```

---

### 4.2 获取岗位列表

**接口**：`GET /jobs`

**请求示例**：
```
GET http://47.111.160.196:9000/jobs?limit=50
```

**响应示例**：
```json
{
  "status": "success",
  "data": [
    {
      "id": "1",
      "job_name": "Java开发工程师",
      "company_name": "某某公司",
      "salary_range": "15-25K",
      "address": "北京"
    }
  ]
}
```

---

### 4.3 搜索岗位（RAG 检索）

**接口**：`POST /jobs/search`

**请求参数**：
```json
{
  "query": "Java开发",
  "top_k": 5
}
```

**请求示例**：
```bash
curl -X POST http://47.111.160.196:9000/jobs/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Java开发",
    "top_k": 5
  }'
```

**响应示例**：
```json
{
  "status": "success",
  "data": [
    {
      "job_name": "Java开发工程师",
      "company_name": "深圳市指南测控技术有限公司",
      "salary_range": "3000-5000元",
      "similarity": 0.92
    }
  ]
}
```

---

### 4.4 解析简历生成学生画像

**接口**：`POST /parse-resume`

**请求参数**：
```json
{
  "name": "张三",
  "age": 22,
  "education": "本科",
  "school": "某某大学",
  "major": "计算机科学与技术",
  "skills": ["Java", "Python", "MySQL", "Spring Boot", "MySQL", "MongoDB"],
  "certificates": ["计算机二级", "英语六级"],
  "internships": [
    {
      "company": "ABC公司",
      "position": "Java开发实习生",
      "duration": "3个月"
    }
  ],
  "projects": [
    {
      "name": "学生管理系统",
      "description": "基于Spring Boot开发的学生信息管理系统"
    }
  ]
}
```

**请求示例**：
```bash
curl -X POST http://47.111.160.196:9000/parse-resume \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "age": 22,
    "education": "本科",
    "school": "某某大学",
    "major": "计算机科学与技术",
    "skills": ["Java", "Python"],
    "certificates": ["计算机二级"]
  }'
```

**响应示例**：
```json
{
  "status": "success",
  "data": {
    "student_id": "xxx",
    "name": "张三",
    "completeness_score": 85,
    "competitiveness_score": 78
  }
}
```

---

### 4.5 人岗匹配分析

**接口**：`POST /job-matching`

**请求参数**：
```json
{
  "student_profile": {
    "name": "张三",
    "skills": ["Java", "Python"],
    "professional_skills": {
      "programming_languages": ["Java",
      "frameworks": ["Spring Boot"]
    },
    "abilities": {
      "innovation_ability": 8,
      "learning_ability": 7
    }
  },
  "job_name": "Java开发工程师"
}
```

**响应示例**：
```json
{
  "status": "success",
  "data": {
    "total_score": 78,
    "skill_matching": 82,
    "quality_matching": 75
  }
}
```

---

### 4.6 生成职业发展报告

**接口**：`POST /career-report`

**请求参数**：
```json
{
  "student_info": {
    "name": "张三",
    "age": 22,
    "education": "本科",
    "school": "某某大学",
    "major": "计算机科学与技术",
    "skills": ["Java", "Python"],
    "target_job": "Java开发工程师"
  }
}
```

**响应示例**：
```json
{
  "status": "success",
  "data": {
    "report_id": "xxx",
    "title": "张三同学Java开发岗位职业发展报告",
    "content": "..."
  }
}
```

---

### 4.7 智能对话

**接口**：`POST /chat`

**请求参数**：
```json
{
  "message": "我想了解一下Java开发岗位的要求"
}
```

**响应示例**：
```json
{
  "status": "success",
  "data": {
    "response": "Java开发岗位需要掌握Java语言、Spring框架、数据库等技能..."
  }
}
```

---

## 5. 调用示例

### 5.1 JavaScript (Fetch)
```javascript
async function chat(message) {
  const response = await fetch('http://47.111.160.196:9000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message })
  });
  const data = await response.json();
  return data.data.response;
}
```

### 5.2 Python (Requests)
```python
import requests

def chat(message):
    url = 'http://47.111.160.196:9000/chat'
    data = {'message': message}
    response = requests.post(url, json=data)
    return response.json()['data']['response']
```

### 5.3 Java (OkHttp)
```java
OkHttpClient client = new OkHttpClient();
MediaType JSON = MediaType.get("application/json; charset=utf-8");

String json = "{\"message\":\"你好\"}";
RequestBody body = RequestBody.create(json, JSON);
Request request = new Request.Builder()
  .url("http://47.111.160.196:9000/chat")
  .post(body)
  .build();

try (Response response = client.newCall(request).execute()) {
  System.out.println(response.body().string());
}
```

---

## 6. 常见问题

### Q1: 接口返回 500 错误
**A: 检查服务是否正常运行，查看服务器日志。

### Q2: 跨域问题
**A: 确保 `.env` 中 `CORS_ORIGINS=*`

### Q3: 如何获取 API 文档
**A: 访问 http://47.111.160.196:9000/docs

---

## 7. 更多信息

- **API 文档 (Swagger): http://47.111.160.196:9000/docs
- **前端演示: http://47.111.160.196:9000/frontend/index.html

