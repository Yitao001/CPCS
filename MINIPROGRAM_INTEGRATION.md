# 大学生职业规划智能体 - 小程序集成指南

## 目录
1. [整体架构](#1-整体架构)
2. [小程序调用 API](#2-小程序调用-api)
3. [API 封装示例](#3-api-封装示例)
4. [页面功能实现](#4-页面功能实现)
5. [跨域和安全配置](#5-跨域和安全配置)
6. [完整示例代码](#6-完整示例代码)

---

## 1. 整体架构

### 架构图

```
┌─────────────┐
│   微信小程序   │
│  (前端界面)   │
└──────┬──────┘
       │ HTTPS 请求
       ↓
┌─────────────────────┐
│  Nginx (反向代理)   │
│  (处理跨域、HTTPS)  │
└──────┬──────────────┘
       │
       ↓
┌─────────────────────────┐
│  职业规划智能体 API      │
│  (FastAPI + Python)     │
└─────────────────────────┘
```

### 数据流

1. 用户在小程序中输入信息
2. 小程序发送 HTTPS 请求到服务器
3. 智能体处理请求并返回结果
4. 小程序展示结果给用户

---

## 2. 小程序调用 API

### 2.1 基础请求方法

小程序使用 `wx.request` 发起网络请求：

```javascript
wx.request({
  url: 'https://your-domain.com/api/endpoint',
  method: 'POST',
  data: {
    key: 'value'
  },
  header: {
    'content-type': 'application/json',
    'X-API-Key': 'your-api-key'  // 如果配置了 API Key
  },
  success(res) {
    console.log('请求成功', res.data)
  },
  fail(err) {
    console.error('请求失败', err)
  }
})
```

### 2.2 服务器域名配置

**重要：** 小程序必须使用 HTTPS，并且需要在微信公众平台配置服务器域名。

#### 配置步骤

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入「开发」→「开发管理」→「开发设置」
3. 在「服务器域名」中配置：
   - request合法域名：`https://your-domain.com`
   - uploadFile合法域名（如果需要上传文件）
   - downloadFile合法域名（如果需要下载文件）

**注意：**
- 域名必须备案
- 必须使用 HTTPS
- 不能使用 IP 地址
- 不能使用端口号（除了 443）

---

## 3. API 封装示例

### 3.1 创建 API 配置文件

在小程序中创建 `config/api.js`：

```javascript
const BASE_URL = 'https://your-domain.com'

const API_CONFIG = {
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'content-type': 'application/json'
  }
}

module.exports = API_CONFIG
```

### 3.2 创建请求封装

在小程序中创建 `utils/request.js`：

```javascript
const config = require('../config/api.js')

function request(url, method = 'GET', data = {}) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: config.baseURL + url,
      method: method,
      data: data,
      header: config.headers,
      timeout: config.timeout,
      success(res) {
        if (res.statusCode === 200) {
          if (res.data.code === 200) {
            resolve(res.data.data)
          } else {
            wx.showToast({
              title: res.data.message || '请求失败',
              icon: 'none'
            })
            reject(res.data)
          }
        } else {
          wx.showToast({
            title: '网络错误',
            icon: 'none'
          })
          reject(res)
        }
      },
      fail(err) {
        wx.showToast({
          title: '网络连接失败',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

module.exports = {
  get: (url, data) => request(url, 'GET', data),
  post: (url, data) => request(url, 'POST', data)
}
```

### 3.3 创建业务 API 封装

在小程序中创建 `api/career.js`：

```javascript
const { get, post } = require('../utils/request.js')

module.exports = {
  // 获取岗位列表
  getJobList() {
    return get('/jobs')
  },

  // 获取岗位详情
  getJobDetail(jobIdentifier) {
    return get(`/jobs/${jobIdentifier}`)
  },

  // 获取岗位关联图谱
  getJobRelations(jobIdentifier) {
    return get(`/jobs/${jobIdentifier}/relations`)
  },

  // 解析简历
  parseResume(resumeContent, studentId) {
    return post('/parse-resume', {
      resume_content: resumeContent,
      student_id: studentId
    })
  },

  // 获取学生能力画像
  getStudentProfile(studentId) {
    return get(`/students/${studentId}/profile`)
  },

  // 人岗匹配
  jobMatching(studentId, jobName) {
    return post('/job-matching', {
      student_id: studentId,
      job_name: jobName
    })
  },

  // 生成职业发展报告
  generateCareerReport(studentId, studentInfo, jobName) {
    return post('/career-report', {
      student_id: studentId,
      student_info: studentInfo,
      job_name: jobName
    })
  },

  // 导出报告
  exportReport(studentId, format = 'markdown') {
    return post('/export-report', {
      student_id: studentId,
      format: format
    })
  },

  // 职业测评
  careerAssessment(studentInfo, studentName) {
    return post('/assessment', {
      student_info: studentInfo,
      student_name: studentName
    })
  },

  // 课程推荐
  courseRecommendation(studentInfo, careerGoal) {
    return post('/course-recommendation', {
      student_info: studentInfo,
      career_goal: careerGoal
    })
  },

  // 就业指导
  jobGuidance(studentInfo, targetPosition) {
    return post('/job-guidance', {
      student_info: studentInfo,
      target_position: targetPosition
    })
  },

  // 智能对话
  chat(message) {
    return post('/chat', {
      message: message
    })
  }
}
```

---

## 4. 页面功能实现

### 4.1 岗位列表页面

**pages/job-list/job-list.wxml**
```html
<view class="container">
  <view class="header">
    <text class="title">岗位列表</text>
  </view>
  
  <view class="job-list">
    <view 
      class="job-item" 
      wx:for="{{jobList}}" 
      wx:key="job_code"
      bindtap="goToDetail"
      data-job="{{item.job_name}}"
    >
      <view class="job-name">{{item.job_name}}</view>
      <view class="job-category">{{item.category}}</view>
    </view>
  </view>
</view>
```

**pages/job-list/job-list.js**
```javascript
const careerApi = require('../../api/career.js')

Page({
  data: {
    jobList: []
  },

  onLoad() {
    this.loadJobList()
  },

  async loadJobList() {
    wx.showLoading({ title: '加载中...' })
    try {
      const data = await careerApi.getJobList()
      this.setData({ jobList: data })
    } catch (err) {
      console.error(err)
    } finally {
      wx.hideLoading()
    }
  },

  goToDetail(e) {
    const jobName = e.currentTarget.dataset.job
    wx.navigateTo({
      url: `/pages/job-detail/job-detail?jobName=${encodeURIComponent(jobName)}`
    })
  }
})
```

### 4.2 岗位详情页面

**pages/job-detail/job-detail.js**
```javascript
const careerApi = require('../../api/career.js')

Page({
  data: {
    jobName: '',
    jobDetail: null,
    relations: null
  },

  onLoad(options) {
    const jobName = decodeURIComponent(options.jobName)
    this.setData({ jobName })
    this.loadJobDetail()
    this.loadJobRelations()
  },

  async loadJobDetail() {
    wx.showLoading({ title: '加载中...' })
    try {
      const data = await careerApi.getJobDetail(this.data.jobName)
      this.setData({ jobDetail: data })
    } catch (err) {
      console.error(err)
    } finally {
      wx.hideLoading()
    }
  },

  async loadJobRelations() {
    try {
      const data = await careerApi.getJobRelations(this.data.jobName)
      this.setData({ relations: data })
    } catch (err) {
      console.error(err)
    }
  }
})
```

### 4.3 人岗匹配页面

**pages/matching/matching.js**
```javascript
const careerApi = require('../../api/career.js')

Page({
  data: {
    studentId: '',
    jobName: '',
    jobList: [],
    matchingResult: null
  },

  onLoad() {
    this.loadJobList()
  },

  async loadJobList() {
    try {
      const data = await careerApi.getJobList()
      this.setData({ jobList: data })
    } catch (err) {
      console.error(err)
    }
  },

  onStudentIdInput(e) {
    this.setData({ studentId: e.detail.value })
  },

  onJobSelect(e) {
    const index = e.detail.value
    this.setData({ jobName: this.data.jobList[index].job_name })
  },

  async doMatching() {
    if (!this.data.studentId || !this.data.jobName) {
      wx.showToast({
        title: '请填写完整信息',
        icon: 'none'
      })
      return
    }

    wx.showLoading({ title: '匹配中...' })
    try {
      const data = await careerApi.jobMatching(
        this.data.studentId,
        this.data.jobName
      )
      this.setData({ matchingResult: data })
    } catch (err) {
      console.error(err)
    } finally {
      wx.hideLoading()
    }
  }
})
```

### 4.4 职业测评页面

**pages/assessment/assessment.js**
```javascript
const careerApi = require('../../api/career.js')

Page({
  data: {
    studentName: '',
    studentInfo: '',
    assessmentResult: null
  },

  onNameInput(e) {
    this.setData({ studentName: e.detail.value })
  },

  onInfoInput(e) {
    this.setData({ studentInfo: e.detail.value })
  },

  async doAssessment() {
    if (!this.data.studentName || !this.data.studentInfo) {
      wx.showToast({
        title: '请填写完整信息',
        icon: 'none'
      })
      return
    }

    wx.showLoading({ title: '分析中...' })
    try {
      const data = await careerApi.careerAssessment(
        this.data.studentInfo,
        this.data.studentName
      )
      this.setData({ assessmentResult: data })
    } catch (err) {
      console.error(err)
    } finally {
      wx.hideLoading()
    }
  }
})
```

---

## 5. 跨域和安全配置

### 5.1 服务器端 Nginx 配置

确保您的 Nginx 配置支持 CORS：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS 配置
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
        add_header Access-Control-Allow-Headers 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,X-API-Key';
        
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_request_buffering off;
    }
}
```

### 5.2 小程序端 app.json 配置

```json
{
  "pages": [
    "pages/index/index",
    "pages/job-list/job-list",
    "pages/job-detail/job-detail",
    "pages/matching/matching",
    "pages/assessment/assessment",
    "pages/report/report"
  ],
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#1890ff",
    "navigationBarTitleText": "职业规划智能体",
    "navigationBarTextStyle": "white"
  },
  "style": "v2",
  "sitemapLocation": "sitemap.json"
}
```

---

## 6. 完整示例代码

### 6.1 项目结构建议

```
小程序项目/
├── app.js
├── app.json
├── app.wxss
├── config/
│   └── api.js          # API 配置
├── utils/
│   └── request.js      # 请求封装
├── api/
│   └── career.js       # 业务 API
└── pages/
    ├── index/          # 首页
    ├── job-list/       # 岗位列表
    ├── job-detail/     # 岗位详情
    ├── matching/       # 人岗匹配
    ├── assessment/     # 职业测评
    └── report/         # 报告展示
```

### 6.2 首页示例

**pages/index/index.wxml**
```html
<view class="container">
  <view class="banner">
    <text class="banner-title">大学生职业规划智能体</text>
    <text class="banner-subtitle">基于 AI 的个性化职业规划助手</text>
  </view>

  <view class="menu-grid">
    <view class="menu-item" bindtap="navigateTo" data-url="/pages/job-list/job-list">
      <view class="menu-icon">💼</view>
      <view class="menu-text">岗位探索</view>
    </view>
    
    <view class="menu-item" bindtap="navigateTo" data-url="/pages/matching/matching">
      <view class="menu-icon">🎯</view>
      <view class="menu-text">人岗匹配</view>
    </view>
    
    <view class="menu-item" bindtap="navigateTo" data-url="/pages/assessment/assessment">
      <view class="menu-icon">📊</view>
      <view class="menu-text">职业测评</view>
    </view>
    
    <view class="menu-item" bindtap="navigateTo" data-url="/pages/report/report">
      <view class="menu-icon">📋</view>
      <view class="menu-text">我的报告</view>
    </view>
  </view>
</view>
```

**pages/index/index.js**
```javascript
Page({
  navigateTo(e) {
    const url = e.currentTarget.dataset.url
    wx.navigateTo({ url })
  }
})
```

**pages/index/index.wxss**
```css
.container {
  padding: 20rpx;
}

.banner {
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  padding: 60rpx 40rpx;
  border-radius: 20rpx;
  margin-bottom: 40rpx;
  color: white;
}

.banner-title {
  font-size: 40rpx;
  font-weight: bold;
  display: block;
  margin-bottom: 20rpx;
}

.banner-subtitle {
  font-size: 28rpx;
  opacity: 0.9;
}

.menu-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30rpx;
}

.menu-item {
  background: white;
  padding: 60rpx 40rpx;
  border-radius: 20rpx;
  text-align: center;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.menu-icon {
  font-size: 60rpx;
  margin-bottom: 20rpx;
}

.menu-text {
  font-size: 30rpx;
  color: #333;
}
```

---

## 7. 常见问题

### Q: 小程序请求失败怎么办？
```
A: 检查以下几点：
1. 服务器域名是否在微信公众平台配置
2. 是否使用 HTTPS
3. 域名是否备案
4. 查看网络请求日志
```

### Q: 如何处理用户登录？
```
A: 可以使用微信登录：
1. 调用 wx.login 获取 code
2. 将 code 发送到后端
3. 后端调用微信接口获取 openid
4. 保存用户信息
```

### Q: 如何上传简历文件？
```
A: 使用 wx.chooseMessageFile 选择文件，然后使用 wx.uploadFile 上传：
wx.chooseMessageFile({
  count: 1,
  type: 'file',
  success(res) {
    const tempFilePaths = res.tempFiles
    wx.uploadFile({
      url: 'https://your-domain.com/upload',
      filePath: tempFilePaths[0].path,
      name: 'file',
      success(res) {
        console.log(res.data)
      }
    })
  }
})
```

---

## 8. 总结

小程序集成的核心步骤：

1. ✅ 配置服务器域名（微信公众平台）
2. ✅ 封装 API 请求（request.js）
3. ✅ 创建业务 API（career.js）
4. ✅ 开发页面功能
5. ✅ 配置 HTTPS 和 CORS
6. ✅ 测试和调试

按照这个指南，您就可以轻松将职业规划智能体集成到小程序中了！🚀
