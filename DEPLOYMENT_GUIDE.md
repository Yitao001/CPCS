# 大学生职业规划智能体 - 部署与集成指南

## 目录

1. [快速开始](#1-快速开始)
2. [Windows 服务器部署](#2-windows-服务器部署详细步骤)
3. [Linux 服务器部署](#3-linux-服务器部署)
4. [API 接口说明](#4-api-接口说明)
5. [在你的程序中集成](#5-在你的程序中集成)
6. [常见问题排查](#6-常见问题排查)

---

## 1. 快速开始

### 1.1 获取项目

```bash
git clone https://github.com/Yitao001/CPCS.git
cd CPCS
```

### 1.2 本地运行

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 复制 .env.example 为 .env，然后编辑配置
cp .env.example .env

# 导入 Excel 数据到向量库
python import_excel.py data/job_data/岗位.xls --clear

# 启动服务
python api.py
```

### 1.3 访问服务

- **服务地址：** http://localhost:9000
- **API 文档：** http://localhost:9000/docs
- **前端页面：** http://localhost:9000/frontend/

---

## 2. Windows 服务器部署（详细步骤）

### 2.1 环境准备

#### 安装 Python 3.8+

1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.8 或更高版本
3. 安装时勾选 "Add Python to PATH"

#### 安装 Git

1. 访问 https://git-scm.com/download/win
2. 下载并安装 Git

### 2.2 克隆项目

```powershell
# 进入项目目录（根据你的实际情况调整）
cd C:\

# 克隆项目
git clone https://github.com/Yitao001/CPCS.git career-planning-agent
cd career-planning-agent
```

### 2.3 创建虚拟环境

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1
```

如果遇到执行策略问题，以管理员身份运行 PowerShell：
```powershell
Set-ExecutionPolicy RemoteSigned
```

### 2.4 安装依赖

```powershell
# 升级 pip
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

### 2.5 配置环境变量

```powershell
# 复制示例配置文件
Copy-Item .env.example .env

# 编辑 .env 文件，配置以下内容
notepad .env
```

配置示例：
```env
# 模型配置 - 使用阿里百炼（推荐）
MODEL_PROVIDER=dashscope
CHAT_MODEL_NAME=qwen-max
DASHSCOPE_API_KEY=你的API密钥

# 或者使用 SiliconFlow
# MODEL_PROVIDER=siliconflow
# CHAT_MODEL_NAME=siliconflow/deepseek-ai/DeepSeek-V3
# SILICONFLOW_API_KEY=你的API密钥

# 服务配置
HOST=0.0.0.0
PORT=9000

# API 密钥认证（重要！）
API_KEY=CPCS_test_API_key

# CORS 配置（允许所有来源访问）
CORS_ORIGINS=*
```

### 2.6 导入 Excel 数据

```powershell
# 导入岗位数据到向量库
python import_excel.py data/job_data/岗位.xls --clear
```

### 2.7 启动服务

```powershell
# 直接启动（开发环境）
python api.py
```

看到以下输出表示启动成功：
```
============================================================
大学生职业规划智能体 API服务启动中...
============================================================
服务地址: http://0.0.0.0:9000
API文档地址:
  - Swagger UI: http://localhost:9000/docs
  - ReDoc: http://localhost:9000/redoc
============================================================
```

### 2.8 配置阿里云安全组

1. 登录阿里云控制台
2. 进入 **ECS 实例** → **安全组**
3. 添加入站规则：
   - **端口范围：** 9000
   - **授权对象：** 0.0.0.0/0（或限制你的 IP）
   - **协议类型：** TCP

### 2.9 配置 Windows 防火墙

```powershell
# 以管理员身份运行 PowerShell

# 添加入站规则允许 9000 端口
New-NetFirewallRule -DisplayName "Allow Port 9000" -Direction Inbound -LocalPort 9000 -Protocol TCP -Action Allow

# 验证规则
Get-NetFirewallRule -DisplayName "*9000*"
```

### 2.10 验证服务

在浏览器中访问：
- `http://你的服务器公网IP:9000/docs`

如果看到 Swagger 文档页面，说明部署成功！

---

## 3. Linux 服务器部署

### 3.1 环境准备

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git -y

# CentOS/RHEL
sudo yum install python3 python3-pip git -y
```

### 3.2 克隆项目

```bash
cd /opt
sudo git clone https://github.com/Yitao001/CPCS.git career-planning-agent
cd career-planning-agent
sudo chown -R $USER:$USER .
```

### 3.3 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.4 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.5 配置环境变量

```bash
cp .env.example .env
nano .env
```

### 3.6 导入数据

```bash
python import_excel.py data/job_data/岗位.xls --clear
```

### 3.7 使用 Systemd 管理服务（推荐）

创建服务文件：
```bash
sudo nano /etc/systemd/system/career-agent.service
```

内容：
```ini
[Unit]
Description=Career Planning Agent Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/career-planning-agent
Environment="PATH=/opt/career-planning-agent/venv/bin"
ExecStart=/opt/career-planning-agent/venv/bin/python api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start career-agent
sudo systemctl enable career-agent
```

查看状态：
```bash
sudo systemctl status career-agent
```

---

## 4. API 接口说明

### 4.1 认证说明

所有 API 请求都需要在请求头中添加：
```
X-API-Key: CPCS_test_API_key
```

### 4.2 接口列表

#### 4.2.1 岗位相关

**获取岗位列表**
```
GET /jobs?keyword=&industry=&city=&salary=&stage=
```

参数：
- `keyword`：关键词搜索
- `industry`：行业筛选
- `city`：城市筛选
- `salary`：薪资范围
- `stage`：岗位阶段

返回：
```json
{
  "success": true,
  "data": [...],
  "message": "获取成功"
}
```

**获取岗位详情**
```
GET /jobs/{job_name}
```

#### 4.2.2 简历解析

**解析简历**
```
POST /resume/parse
```

请求体：
```json
{
  "resume_content": "张三，大三，计算机专业，熟练掌握Java、Python...",
  "student_id": "student_001"
}
```

#### 4.2.3 学生能力分析

**能力分析**
```
POST /student/ability
```

请求体：
```json
{
  "student_info": "大三，计算机科学与技术专业，熟练掌握Java、Python...",
  "student_id": "student_001"
}
```

#### 4.2.4 职业报告

**生成职业报告**
```
POST /report
```

请求体：
```json
{
  "student_id": "student_001",
  "student_info": "大三，计算机专业，Java方向，有3个月实习经验...",
  "job_name": "Java后端开发工程师"
}
```

**润色报告**
```
POST /report/polish
```

**导出报告**
```
GET /report/export?student_id=&format=
```

#### 4.2.5 用户相关

**获取用户信息**
```
GET /user/info?user_id=
```

**获取历史报告**
```
GET /history/reports?user_id=
```

#### 4.2.6 社区相关

**获取官方文章**
```
GET /community/articles
```

#### 4.2.7 智能对话

**发送聊天消息**
```
POST /chat
```

请求体：
```json
{
  "message": "你好，我是计算机专业大三学生，请给我一些职业规划建议"
}
```

**职业测评**
```
POST /assessment
```

请求体：
```json
{
  "student_info": "大三，计算机科学与技术专业，喜欢编程...",
  "student_name": "张三"
}
```

**职业发展报告**
```
POST /career-report
```

---

## 5. 在你的程序中集成

### 5.1 JavaScript/前端集成示例

#### 5.1.1 基础 API 封装

```javascript
// api.js - API 封装
const API_BASE = 'http://你的服务器IP:9000';
const API_KEY = 'CPCS_test_API_key';

async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${url}`, {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
        ...options.headers
      },
      ...options
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API 请求失败:', error);
    throw error;
  }
}

// 岗位相关
export const JobAPI = {
  // 获取岗位列表
  getJobs: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/jobs?${query}`);
  },
  
  // 获取岗位详情
  getJobDetail: (jobName) => {
    return apiRequest(`/jobs/${encodeURIComponent(jobName)}`);
  }
};

// 简历解析
export const ResumeAPI = {
  parse: (resumeContent, studentId) => {
    return apiRequest('/resume/parse', {
      method: 'POST',
      body: JSON.stringify({ resume_content: resumeContent, student_id: studentId })
    });
  }
};

// 学生能力分析
export const StudentAPI = {
  analyzeAbility: (studentInfo, studentId) => {
    return apiRequest('/student/ability', {
      method: 'POST',
      body: JSON.stringify({ student_info: studentInfo, student_id: studentId })
    });
  }
};

// 职业报告
export const ReportAPI = {
  generate: (studentId, studentInfo, jobName) => {
    return apiRequest('/report', {
      method: 'POST',
      body: JSON.stringify({ student_id: studentId, student_info: studentInfo, job_name: jobName })
    });
  },
  
  polish: (reportId, content) => {
    return apiRequest('/report/polish', {
      method: 'POST',
      body: JSON.stringify({ report_id: reportId, content: content })
    });
  },
  
  export: (studentId, format = 'html') => {
    return apiRequest(`/report/export?student_id=${studentId}&format=${format}`);
  }
};

// 智能对话
export const ChatAPI = {
  sendMessage: (message) => {
    return apiRequest('/chat', {
      method: 'POST',
      body: JSON.stringify({ message: message })
    });
  },
  
  assessment: (studentInfo, studentName) => {
    return apiRequest('/assessment', {
      method: 'POST',
      body: JSON.stringify({ student_info: studentInfo, student_name: studentName })
    });
  },
  
  careerReport: (studentId, studentInfo, jobName) => {
    return apiRequest('/career-report', {
      method: 'POST',
      body: JSON.stringify({ student_id: studentId, student_info: studentInfo, job_name: jobName })
    });
  }
};
```

#### 5.1.2 在页面中使用

```html
<!DOCTYPE html>
<html>
<head>
  <title>职业规划 - 我的应用</title>
</head>
<body>
  <h1>职业规划系统</h1>
  
  <!-- 岗位搜索 -->
  <div>
    <h2>岗位搜索</h2>
    <input type="text" id="keyword" placeholder="输入关键词">
    <button onclick="searchJobs()">搜索</button>
    <div id="jobsList"></div>
  </div>
  
  <!-- 简历解析 -->
  <div>
    <h2>简历解析</h2>
    <textarea id="resumeContent" placeholder="粘贴你的简历内容..."></textarea>
    <input type="text" id="studentId" placeholder="学生ID">
    <button onclick="parseResume()">解析简历</button>
    <div id="parseResult"></div>
  </div>
  
  <!-- 智能对话 -->
  <div>
    <h2>智能对话</h2>
    <div id="chatHistory"></div>
    <input type="text" id="chatInput" placeholder="输入消息...">
    <button onclick="sendChat()">发送</button>
  </div>

  <script type="module">
    import { JobAPI, ResumeAPI, ChatAPI } from './api.js';
    
    // 搜索岗位
    window.searchJobs = async () => {
      const keyword = document.getElementById('keyword').value;
      const result = await JobAPI.getJobs({ keyword });
      
      if (result.success) {
        const jobsList = document.getElementById('jobsList');
        jobsList.innerHTML = result.data.map(job => 
          `<div>${job.job_name} - ${job.company_name}</div>`
        ).join('');
      }
    };
    
    // 解析简历
    window.parseResume = async () => {
      const content = document.getElementById('resumeContent').value;
      const studentId = document.getElementById('studentId').value;
      const result = await ResumeAPI.parse(content, studentId);
      
      document.getElementById('parseResult').innerText = JSON.stringify(result, null, 2);
    };
    
    // 发送聊天
    window.sendChat = async () => {
      const message = document.getElementById('chatInput').value;
      const result = await ChatAPI.sendMessage(message);
      
      if (result.success) {
        const history = document.getElementById('chatHistory');
        history.innerHTML += `<div><strong>我:</strong> ${message}</div>`;
        history.innerHTML += `<div><strong>AI:</strong> ${result.data}</div>`;
        document.getElementById('chatInput').value = '';
      }
    };
  </script>
</body>
</html>
```

### 5.2 Python/后端集成示例

```python
# career_agent_client.py
import requests
import json

class CareerAgentClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        }
    
    def _request(self, method, url, data=None):
        try:
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
    
    # 岗位相关
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
        import urllib.parse
        encoded_name = urllib.parse.quote(job_name)
        return self._request('GET', f"/jobs/{encoded_name}")
    
    # 简历解析
    def parse_resume(self, resume_content, student_id):
        return self._request('POST', '/resume/parse', {
            'resume_content': resume_content,
            'student_id': student_id
        })
    
    # 学生能力分析
    def analyze_ability(self, student_info, student_id):
        return self._request('POST', '/student/ability', {
            'student_info': student_info,
            'student_id': student_id
        })
    
    # 生成职业报告
    def generate_report(self, student_id, student_info, job_name):
        return self._request('POST', '/report', {
            'student_id': student_id,
            'student_info': student_info,
            'job_name': job_name
        })
    
    # 智能对话
    def chat(self, message):
        return self._request('POST', '/chat', {
            'message': message
        })
    
    # 职业测评
    def assessment(self, student_info, student_name):
        return self._request('POST', '/assessment', {
            'student_info': student_info,
            'student_name': student_name
        })


# 使用示例
if __name__ == '__main__':
    # 初始化客户端
    client = CareerAgentClient(
        base_url='http://你的服务器IP:9000',
        api_key='CPCS_test_API_key'
    )
    
    # 1. 获取岗位列表
    print("=== 获取岗位列表 ===")
    result = client.get_jobs(keyword='Java')
    if result['success']:
        print(f"找到 {len(result['data'])} 个岗位")
        for job in result['data'][:3]:
            print(f"- {job['job_name']}")
    
    # 2. 解析简历
    print("\n=== 解析简历 ===")
    result = client.parse_resume(
        resume_content='张三，大三，计算机科学与技术专业，熟练掌握Java、Python、MySQL，有3个月的后端开发实习经验',
        student_id='student_001'
    )
    if result['success']:
        print('解析成功')
        print(result['data'])
    
    # 3. 智能对话
    print("\n=== 智能对话 ===")
    result = client.chat('你好，我是计算机专业大三学生，请给我一些职业规划建议')
    if result['success']:
        print('AI 回复:', result['data'])
    
    # 4. 生成职业报告
    print("\n=== 生成职业报告 ===")
    result = client.generate_report(
        student_id='student_001',
        student_info='大三，计算机专业，Java方向，有3个月实习经验',
        job_name='Java后端开发工程师'
    )
    if result['success']:
        print('报告生成成功')
```

### 5.3 微信小程序集成示例

```javascript
// app.js
const API_BASE = 'http://你的服务器IP:9000';
const API_KEY = 'CPCS_test_API_key';

// API 封装
function request(url, data, method = 'GET') {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE}${url}`,
      method: method,
      header: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      data: data,
      success: (res) => {
        resolve(res.data);
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
}

// 页面使用示例
Page({
  data: {
    jobs: []
  },
  
  onLoad() {
    this.loadJobs();
  },
  
  // 加载岗位列表
  async loadJobs() {
    const result = await request('/jobs');
    if (result.success) {
      this.setData({ jobs: result.data });
    }
  },
  
  // 搜索岗位
  async searchJobs(e) {
    const keyword = e.detail.value;
    const result = await request(`/jobs?keyword=${keyword}`);
    if (result.success) {
      this.setData({ jobs: result.data });
    }
  },
  
  // 发送聊天
  async sendChat(e) {
    const message = e.detail.value;
    const result = await request('/chat', { message: message }, 'POST');
    if (result.success) {
      // 处理回复
    }
  }
});
```

### 5.4 其他语言集成

#### Java
```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class CareerAgentClient {
    private static final String BASE_URL = "http://你的服务器IP:9000";
    private static final String API_KEY = "CPCS_test_API_key";
    
    private HttpClient client = HttpClient.newHttpClient();
    
    public String getJobs() throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/jobs"))
            .header("Content-Type", "application/json")
            .header("X-API-Key", API_KEY)
            .GET()
            .build();
        
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }
}
```

#### Go
```go
package main

import (
    "bytes"
    "encoding/json"
    "io/ioutil"
    "net/http"
)

const (
    baseURL = "http://你的服务器IP:9000"
    apiKey  = "CPCS_test_API_key"
)

func main() {
    // 获取岗位列表
    req, _ := http.NewRequest("GET", baseURL+"/jobs", nil)
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("X-API-Key", apiKey)
    
    client := &http.Client{}
    resp, _ := client.Do(req)
    defer resp.Body.Close()
    
    body, _ := ioutil.ReadAll(resp.Body)
    println(string(body))
}
```

---

## 6. 常见问题排查

### 6.1 服务无法启动

**检查端口占用：**
```powershell
# Windows
netstat -ano | findstr :9000

# Linux
netstat -tlnp | grep 9000
```

如果端口被占用，结束进程或修改 .env 中的 PORT。

**手动运行查看错误：**
```bash
python api.py
```

### 6.2 无法访问服务

1. 检查阿里云安全组是否开放 9000 端口
2. 检查服务器防火墙是否允许 9000 端口
3. 确认服务监听在 0.0.0.0 而不是 127.0.0.1
4. 使用服务器公网 IP 访问，不要用 localhost

### 6.3 模型调用失败

1. 检查 API Key 是否正确配置
2. 检查网络连接是否正常
3. 查看服务日志输出
4. 确认模型提供商和模型名称配置正确

### 6.4 API 调用返回 401

检查是否在请求头中正确添加了 `X-API-Key`。

### 6.5 数据导入失败

1. 确认 Excel 文件路径正确
2. 检查文件格式是否正确
3. 查看导入日志输出

### 6.6 跨域问题（CORS）

确保 .env 中配置：
```env
CORS_ORIGINS=*
```

或者配置具体的允许域名：
```env
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
```

---

## 7. 更新与维护

### 7.1 更新代码

```bash
# 停止旧服务（Windows）
netstat -ano | findstr :9000
# 找到 PID 后执行
taskkill /F /PID <PID>

# 拉取最新代码
git pull origin main

# 重新导入数据（如果有更新）
python import_excel.py data/job_data/岗位.xls --clear

# 重新启动服务
python api.py
```

### 7.2 备份数据

定期备份以下目录：
- `data/student_data/` - 学生数据
- `data/reports/` - 报告数据

---

## 8. 技术支持

如遇到问题，请检查：
1. 服务日志输出
2. API 文档（/docs）
3. 常见问题排查章节

---

祝您使用愉快！如有问题，欢迎反馈。
