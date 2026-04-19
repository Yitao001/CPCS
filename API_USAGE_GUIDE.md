# 大学生职业规划智能体 - API 调用指南

## 快速开始

### 1. 服务地址
```
http://你的服务器IP:9000
```

### 2. 认证方式
所有请求必须在请求头中添加 API Key：
```
X-API-Key: CPCS_test_API_key
```

### 3. 查看 API 文档
在浏览器中打开以下地址可以看到完整的交互式 API 文档：
```
http://你的服务器IP:9000/docs
```

---

## 接口调用示例

### 接口 1：获取岗位列表
**接口：** `GET /jobs`

**请求参数：**
- `keyword` - 关键词搜索（可选）
- `industry` - 行业筛选（可选）
- `city` - 城市筛选（可选）
- `salary` - 薪资范围（可选）
- `stage` - 岗位阶段（可选）

**JavaScript 示例：**
```javascript
fetch('http://你的服务器IP:9000/jobs?keyword=Java', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
  }
})
.then(response => response.json())
.then(data => {
  console.log('岗位列表：', data);
  if (data.success) {
    console.log('找到 ' + data.data.length + ' 个岗位');
  }
})
.catch(error => {
  console.error('请求失败：', error);
});
```

**Python 示例：**
```python
import requests

url = 'http://你的服务器IP:9000/jobs'
params = {'keyword': 'Java'}
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
}

response = requests.get(url, params=params, headers=headers)
data = response.json()

if data['success']:
    print(f"找到 {len(data['data'])} 个岗位")
    for job in data['data']:
        print(f"- {job['job_name']} - {job['company_name']}")
```

---

### 接口 2：获取岗位详情
**接口：** `GET /jobs/{job_name}`

**JavaScript 示例：**
```javascript
const jobName = encodeURIComponent('Java后端开发工程师');
fetch(`http://你的服务器IP:9000/jobs/${jobName}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
  }
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('岗位详情：', data.data);
  }
});
```

**Python 示例：**
```python
import requests
import urllib.parse

job_name = 'Java后端开发工程师'
encoded_name = urllib.parse.quote(job_name)
url = f'http://你的服务器IP:9000/jobs/{encoded_name}'
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
}

response = requests.get(url, headers=headers)
data = response.json()

if data['success']:
    print('岗位详情：', data['data'])
```

---

### 接口 3：解析简历
**接口：** `POST /resume/parse`

**请求体：**
```json
{
  "resume_content": "张三，大三，计算机科学与技术专业，熟练掌握Java、Python、MySQL，有3个月的后端开发实习经验",
  "student_id": "student_001"
}
```

**JavaScript 示例：**
```javascript
fetch('http://你的服务器IP:9000/resume/parse', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
  },
  body: JSON.stringify({
    resume_content: '张三，大三，计算机科学与技术专业，熟练掌握Java、Python、MySQL，有3个月的后端开发实习经验',
    student_id: 'student_001'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('解析结果：', data.data);
  } else {
    console.error('解析失败：', data.message);
  }
});
```

**Python 示例：**
```python
import requests

url = 'http://你的服务器IP:9000/resume/parse'
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
}
data = {
    'resume_content': '张三，大三，计算机科学与技术专业，熟练掌握Java、Python、MySQL，有3个月的后端开发实习经验',
    'student_id': 'student_001'
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

if result['success']:
    print('解析成功：', result['data'])
else:
    print('解析失败：', result['message'])
```

---

### 接口 4：学生能力分析
**接口：** `POST /student/ability`

**请求体：**
```json
{
  "student_info": "大三，计算机科学与技术专业，熟练掌握Java、Python、MySQL，有3个月的后端开发实习经验，英语四级",
  "student_id": "student_001"
}
```

**JavaScript 示例：**
```javascript
fetch('http://你的服务器IP:9000/student/ability', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
  },
  body: JSON.stringify({
    student_info: '大三，计算机科学与技术专业，熟练掌握Java、Python、MySQL，有3个月的后端开发实习经验，英语四级',
    student_id: 'student_001'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('能力分析结果：', data.data);
  }
});
```

**Python 示例：**
```python
import requests

url = 'http://你的服务器IP:9000/student/ability'
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
}
data = {
    'student_info': '大三，计算机科学与技术专业，熟练掌握Java、Python、MySQL，有3个月的后端开发实习经验，英语四级',
    'student_id': 'student_001'
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

if result['success']:
    print('能力分析结果：', result['data'])
```

---

### 接口 5：生成职业报告
**接口：** `POST /report`

**请求体：**
```json
{
  "student_id": "student_001",
  "student_info": "大三，计算机科学与技术专业，熟练掌握Java、Python、MySQL，有3个月的后端开发实习经验，对大数据方向感兴趣",
  "job_name": "Java后端开发工程师"
}
```

**JavaScript 示例：**
```javascript
fetch('http://你的服务器IP:9000/report', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
  },
  body: JSON.stringify({
    student_id: 'student_001',
    student_info: '大三，计算机科学与技术专业，熟练掌握Java、Python、MySQL，有3个月的后端开发实习经验，对大数据方向感兴趣',
    job_name: 'Java后端开发工程师'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('职业报告：', data.data);
  } else {
    console.error('生成失败：', data.message);
  }
});
```

**Python 示例：**
```python
import requests

url = 'http://你的服务器IP:9000/report'
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
}
data = {
    'student_id': 'student_001',
    'student_info': '大三，计算机科学与技术专业，熟练掌握Java、Python、MySQL，有3个月的后端开发实习经验，对大数据方向感兴趣',
    'job_name': 'Java后端开发工程师'
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

if result['success']:
    print('职业报告：', result['data'])
else:
    print('生成失败：', result['message'])
```

---

### 接口 6：智能对话
**接口：** `POST /chat`

**请求体：**
```json
{
  "message": "你好，我是计算机专业大三学生，请给我一些职业规划建议"
}
```

**JavaScript 示例：**
```javascript
fetch('http://你的服务器IP:9000/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
  },
  body: JSON.stringify({
    message: '你好，我是计算机专业大三学生，请给我一些职业规划建议'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('AI 回复：', data.data);
  }
});
```

**Python 示例：**
```python
import requests

url = 'http://你的服务器IP:9000/chat'
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
}
data = {
    'message': '你好，我是计算机专业大三学生，请给我一些职业规划建议'
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

if result['success']:
    print('AI 回复：', result['data'])
```

---

### 接口 7：职业测评
**接口：** `POST /assessment`

**请求体：**
```json
{
  "student_info": "大三，计算机科学与技术专业，喜欢编程，对人工智能和大数据方向感兴趣，性格开朗，善于沟通",
  "student_name": "张三"
}
```

**JavaScript 示例：**
```javascript
fetch('http://你的服务器IP:9000/assessment', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
  },
  body: JSON.stringify({
    student_info: '大三，计算机科学与技术专业，喜欢编程，对人工智能和大数据方向感兴趣，性格开朗，善于沟通',
    student_name: '张三'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('测评结果：', data.data);
  }
});
```

**Python 示例：**
```python
import requests

url = 'http://你的服务器IP:9000/assessment'
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
}
data = {
    'student_info': '大三，计算机科学与技术专业，喜欢编程，对人工智能和大数据方向感兴趣，性格开朗，善于沟通',
    'student_name': '张三'
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

if result['success']:
    print('测评结果：', result['data'])
```

---

### 接口 8：职业发展报告（详细）
**接口：** `POST /career-report`

**请求体：**
```json
{
  "student_id": "student_001",
  "student_info": "大三，计算机科学与技术专业，熟练掌握Java、Python、MySQL，有3个月的后端开发实习经验，对大数据方向感兴趣",
  "job_name": "Java后端开发工程师"
}
```

**JavaScript 示例：**
```javascript
fetch('http://你的服务器IP:9000/career-report', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
  },
  body: JSON.stringify({
    student_id: 'student_001',
    student_info: '大三，计算机科学与技术专业，熟练掌握Java、Python、MySQL，有3个月的后端开发实习经验，对大数据方向感兴趣',
    job_name: 'Java后端开发工程师'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('职业发展报告：', data.data);
  }
});
```

**Python 示例：**
```python
import requests

url = 'http://你的服务器IP:9000/career-report'
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'CPCS_test_API_key'
}
data = {
    'student_id': 'student_001',
    'student_info': '大三，计算机科学与技术专业，熟练掌握Java、Python、MySQL，有3个月的后端开发实习经验，对大数据方向感兴趣',
    'job_name': 'Java后端开发工程师'
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

if result['success']:
    print('职业发展报告：', result['data'])
```

---

### 接口 9：润色报告
**接口：** `POST /report/polish`

**请求体：**
```json
{
  "report_id": "student_001_20240419",
  "content": "需要润色的报告内容..."
}
```

---

### 接口 10：导出报告
**接口：** `GET /report/export?student_id=xxx&format=html`

**请求参数：**
- `student_id` - 学生ID
- `format` - 导出格式：`html` 或 `markdown`

---

### 接口 11：获取用户信息
**接口：** `GET /user/info?user_id=xxx`

---

### 接口 12：获取历史报告
**接口：** `GET /history/reports?user_id=xxx`

---

### 接口 13：获取官方文章
**接口：** `GET /community/articles`

---

## 完整封装示例

### JavaScript 完整封装
```javascript
// career-api.js
class CareerAPI {
  constructor(baseUrl, apiKey) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  async request(method, url, data = null) {
    const options = {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey
      }
    };

    if (data && method !== 'GET') {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(`${this.baseUrl}${url}`, options);
      return await response.json();
    } catch (error) {
      return {
        success: false,
        data: null,
        message: error.message
      };
    }
  }

  async getJobs(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request('GET', `/jobs?${query}`);
  }

  async getJobDetail(jobName) {
    const encodedName = encodeURIComponent(jobName);
    return this.request('GET', `/jobs/${encodedName}`);
  }

  async parseResume(resumeContent, studentId) {
    return this.request('POST', '/resume/parse', {
      resume_content: resumeContent,
      student_id: studentId
    });
  }

  async analyzeAbility(studentInfo, studentId) {
    return this.request('POST', '/student/ability', {
      student_info: studentInfo,
      student_id: studentId
    });
  }

  async generateReport(studentId, studentInfo, jobName) {
    return this.request('POST', '/report', {
      student_id: studentId,
      student_info: studentInfo,
      job_name: jobName
    });
  }

  async chat(message) {
    return this.request('POST', '/chat', { message: message });
  }

  async assessment(studentInfo, studentName) {
    return this.request('POST', '/assessment', {
      student_info: studentInfo,
      student_name: studentName
    });
  }

  async careerReport(studentId, studentInfo, jobName) {
    return this.request('POST', '/career-report', {
      student_id: studentId,
      student_info: studentInfo,
      job_name: jobName
    });
  }
}

// 使用示例
const api = new CareerAPI('http://你的服务器IP:9000', 'CPCS_test_API_key');

// 调用示例
async function testAPI() {
  // 获取岗位列表
  const jobs = await api.getJobs({ keyword: 'Java' });
  console.log('岗位列表：', jobs);

  // 解析简历
  const resumeResult = await api.parseResume(
    '张三，大三，计算机专业，熟练掌握Java',
    'student_001'
  );
  console.log('简历解析：', resumeResult);

  // 智能对话
  const chatResult = await api.chat('你好，请介绍一下自己');
  console.log('对话结果：', chatResult);
}

testAPI();
```

### Python 完整封装
```python
import requests
import urllib.parse

class CareerAPIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        }
    
    def _request(self, method, url, data=None):
        try:
            if method == 'GET':
                response = requests.get(
                    f"{self.base_url}{url}",
                    headers=self.headers
                )
            else:
                response = requests.request(
                    method,
                    f"{self.base_url}{url}",
                    headers=self.headers,
                    json=data
                )
            return response.json()
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'message': str(e)
            }
    
    def get_jobs(self, keyword=None, industry=None, city=None):
        params = {}
        if keyword:
            params['keyword'] = keyword
        if industry:
            params['industry'] = industry
        if city:
            params['city'] = city
        
        query = '&'.join([f"{k}={v}" for k, v in params.items()])
        return self._request('GET', f"/jobs?{query}")
    
    def get_job_detail(self, job_name):
        encoded_name = urllib.parse.quote(job_name)
        return self._request('GET', f"/jobs/{encoded_name}")
    
    def parse_resume(self, resume_content, student_id):
        return self._request('POST', '/resume/parse', {
            'resume_content': resume_content,
            'student_id': student_id
        })
    
    def analyze_ability(self, student_info, student_id):
        return self._request('POST', '/student/ability', {
            'student_info': student_info,
            'student_id': student_id
        })
    
    def generate_report(self, student_id, student_info, job_name):
        return self._request('POST', '/report', {
            'student_id': student_id,
            'student_info': student_info,
            'job_name': job_name
        })
    
    def chat(self, message):
        return self._request('POST', '/chat', {
            'message': message
        })
    
    def assessment(self, student_info, student_name):
        return self._request('POST', '/assessment', {
            'student_info': student_info,
            'student_name': student_name
        })
    
    def career_report(self, student_id, student_info, job_name):
        return self._request('POST', '/career-report', {
            'student_id': student_id,
            'student_info': student_info,
            'job_name': job_name
        })

# 使用示例
if __name__ == '__main__':
    client = CareerAPIClient('http://你的服务器IP:9000', 'CPCS_test_API_key')
    
    # 1. 获取岗位列表
    print("=== 获取岗位列表 ===")
    jobs_result = client.get_jobs(keyword='Java')
    if jobs_result['success']:
        print(f"找到 {len(jobs_result['data'])} 个岗位")
    
    # 2. 解析简历
    print("\n=== 解析简历 ===")
    resume_result = client.parse_resume(
        '张三，大三，计算机专业，熟练掌握Java',
        'student_001'
    )
    if resume_result['success']:
        print('解析成功')
    
    # 3. 智能对话
    print("\n=== 智能对话 ===")
    chat_result = client.chat('你好，请给我一些职业建议')
    if chat_result['success']:
        print('AI 回复：', chat_result['data'])
```

---

## 统一响应格式

所有接口都返回统一的 JSON 格式：
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| data | any | 返回的数据 |
| message | string | 提示信息 |

---

## 常见问题

### 1. 401 Unauthorized
**问题：** 返回 401 未授权错误

**解决：** 检查是否在请求头中正确添加了 `X-API-Key`

---

### 2. CORS 跨域问题
**问题：** 浏览器提示跨域错误

**解决：** 确保服务器已配置 `CORS_ORIGINS=*`

---

### 3. 请求超时
**问题：** 响应时间较长

**说明：** AI 处理需要时间，建议设置 30-60 秒的超时时间

---

### 4. 查看交互式文档
在浏览器打开 `http://你的服务器IP:9000/docs` 可以：
- 直接测试所有接口
- 查看完整的请求和响应格式
- 自动生成各种语言的调用代码

---

## 联系支持

如有问题，请检查：
1. 服务是否正常运行
2. API Key 是否正确
3. 网络连接是否正常
4. 查看 API 文档 `/docs`

---

祝您使用愉快！
