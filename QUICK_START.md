# 大学生职业规划智能体 - 快速开始

## 📦 交付物

| 项目 | 内容 |
|------|------|
| **API 地址 | http://47.111.160.196:9000 |
| **API 文档** | http://47.111.160.196:9000/docs |
| **前端演示** | http://47.111.160.196:9000/frontend/index.html |
| **接口文档** | API_GUIDE.md |

---

## 🚀 5 分钟快速上手

### 1. 测试健康检查
```bash
curl http://47.111.160.196:9000/health
```

### 2. 获取岗位列表
```bash
curl http://47.111.160.196:9000/jobs
```

### 3. 智能对话
```bash
curl -X POST http://47.111.160.196:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'
```

---

## 📚 核心功能

| 功能 | 接口 | 说明 |
|------|------|------|
| 就业能力分析 | `POST /parse-resume` | 解析简历生成学生画像 |
| 就业岗位要求 | `GET /jobs`, `POST /jobs/search` | 岗位探索和搜索 |
| 职业生涯发展报告 | `POST /career-report` | 生成完整的职业发展报告 |
| 智能对话 | `POST /chat` | 自然语言交互 |

---

## 💻 代码示例

### JavaScript
```javascript
async function chat(message) {
  const res = await fetch('http://47.111.160.196:9000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  return (await res.json()).data.response;
}
```

### Python
```python
import requests

def chat(message):
    url = 'http://47.111.160.196:9000/chat'
    data = {'message': message}
    return requests.post(url, json=data).json()['data']['response']
```

---

## 📖 详细文档

- API 接口文档：API_GUIDE.md
- 部署指南：ALIYUN_DEPLOYMENT.md
- 使用指南：USER_GUIDE.md

