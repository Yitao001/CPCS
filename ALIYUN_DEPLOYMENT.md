# 大学生职业规划智能体 - 阿里云部署指南

## 目录
1. [阿里云服务器准备](#1-阿里云服务器准备)
2. [本地准备工作](#2-本地准备工作)
3. [上传代码到阿里云服务器](#3-上传代码到阿里云服务器)
4. [服务器环境配置](#4-服务器环境配置)
5. [导入 Excel 岗位数据](#5-导入-excel-岗位数据)
6. [启动服务](#6-启动服务)
7. [配置阿里云安全组](#7-配置阿里云安全组)
8. [访问验证](#8-访问验证)
9. [使用 Systemd 管理服务（推荐）](#9-使用-systemd-管理服务推荐)
10. [常见问题](#10-常见问题)

---

## 1. 阿里云服务器准备

### 1.1 购买服务器
- 登录阿里云：https://www.aliyun.com
- 选择产品 → 云服务器 ECS
- 推荐配置：
  - CPU：2 核及以上
  - 内存：4 GB 及以上
  - 操作系统：**Ubuntu 22.04 LTS**（推荐）
  - 带宽：1 Mbps 及以上

### 1.2 获取服务器信息
购买完成后，在阿里云控制台 → 云服务器 ECS → 实例与镜像 → 实例 中查看：
- **公网 IP**：例如 `123.45.67.89`
- **内网 IP**：例如 `172.16.0.1`
- **实例密码**：你设置的 root 密码

---

## 2. 本地准备工作

### 2.1 确保本地代码已提交到 Git
```bash
cd e:\yuanma\CPCS
git status
```

如果有未提交的更改：
```bash
git add .
git commit -m "准备部署到阿里云"
```

### 2.2 推送到 GitHub
```bash
git push -u origin master
```

---

## 3. 上传代码到阿里云服务器

### 3.1 使用 SSH 连接服务器
打开 PowerShell 或 CMD，执行：

```bash
ssh root@你的公网IP
```

例如：
```bash
ssh root@123.45.67.89
```

输入密码后，你就进入服务器了。

### 3.2 在服务器上安装 Git
```bash
apt update
apt install git -y
```

### 3.3 克隆项目代码
```bash
cd /opt
git clone https://github.com/Yitao001/CPCS.git career-planning-agent
cd career-planning-agent
```

### 3.4 （可选）如果是私有仓库
```bash
git clone https://你的用户名:你的token@github.com/Yitao001/CPCS.git career-planning-agent
```

---

## 4. 服务器环境配置

### 4.1 安装 Python 3 和 pip
```bash
apt install python3 python3-pip python3-venv -y
```

检查 Python 版本：
```bash
python3 --version
```
应该显示 3.8 或更高版本。

### 4.2 创建虚拟环境
```bash
cd /opt/career-planning-agent
python3 -m venv venv
source venv/bin/activate
```

激活成功后，提示符前面会有 `(venv)` 标志。

### 4.3 安装依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4.4 安装额外需要的包
```bash
pip install sentence-transformers pandas openpyxl xlrd -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4.5 配置环境变量
```bash
cp .env.example .env
nano .env
```

编辑 `.env` 文件，配置以下内容：

```env
# 模型配置
MODEL_PROVIDER=siliconflow
CHAT_MODEL_NAME=siliconflow/deepseek-ai/DeepSeek-V3
SILICONFLOW_API_KEY=sk-你的APIKey
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1

# 服务器配置
HOST=0.0.0.0
PORT=9000

# API Key（用于保护接口，可选）
API_KEY=your_secure_api_key_here

# CORS 配置
CORS_ORIGINS=*
```

按 `Ctrl + X`，然后按 `Y`，再按 `Enter` 保存退出。

---

## 5. 导入 Excel 岗位数据

### 5.1 上传 Excel 文件到服务器
在**本地**的 PowerShell 中执行（不要在 SSH 连接中执行）：

```bash
cd e:\yuanma\CPCS
scp data\job_data\岗位.xls root@你的公网IP:/opt/career-planning-agent/data/job_data/
```

例如：
```bash
scp data\job_data\岗位.xls root@123.45.67.89:/opt/career-planning-agent/data/job_data/
```

### 5.2 在服务器上导入数据
回到 SSH 连接，执行：

```bash
cd /opt/career-planning-agent
source venv/bin/activate
python import_excel.py data/job_data/岗位.xls --clear
```

导入成功后，会显示：
```
✅ 导入成功！
```

---

## 6. 启动服务

### 6.1 测试运行
```bash
cd /opt/career-planning-agent
source venv/bin/activate
python api.py
```

看到以下输出表示启动成功：
```
INFO:     Uvicorn running on http://0.0.0.0:9000
```

按 `Ctrl + C` 停止。

### 6.2 后台运行（临时方案）
```bash
nohup python api.py > app.log 2>&1 &
```

查看日志：
```bash
tail -f app.log
```

---

## 7. 配置阿里云安全组

### 7.1 打开阿里云控制台
1. 登录阿里云控制台
2. 进入：云服务器 ECS → 网络与安全 → 安全组
3. 找到你的实例对应的安全组，点击"配置规则"

### 7.2 添加入方向规则
点击"手动添加"，添加以下规则：

| 规则方向 | 授权策略 | 协议类型 | 端口范围 | 授权对象 | 描述 |
|---------|---------|---------|---------|---------|------|
| 入方向 | 允许 | TCP | 22/22 | 0.0.0.0/0 | SSH |
| 入方向 | 允许 | TCP | 9000/9000 | 0.0.0.0/0 | 应用服务 |

---

## 8. 访问验证

### 8.1 测试 API 健康检查
在浏览器或 Postman 中访问：
```
http://你的公网IP:9000/health
```

应该返回：
```json
{
  "status": "ok",
  "service": "career-planning-agent"
}
```

### 8.2 访问 API 文档
```
http://你的公网IP:9000/docs
```

### 8.3 访问前端页面
```
http://你的公网IP:9000/frontend/index.html
```

---

## 9. 使用 Systemd 管理服务（推荐）

### 9.1 创建 Systemd 服务文件
```bash
nano /etc/systemd/system/career-agent.service
```

复制以下内容：

```ini
[Unit]
Description=Career Planning Agent Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/career-planning-agent
Environment="PATH=/opt/career-planning-agent/venv/bin"
ExecStart=/opt/career-planning-agent/venv/bin/python api.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/career-agent.log
StandardError=append:/var/log/career-agent-error.log

[Install]
WantedBy=multi-user.target
```

按 `Ctrl + X`，`Y`，`Enter` 保存。

### 9.2 创建日志文件
```bash
touch /var/log/career-agent.log
touch /var/log/career-agent-error.log
```

### 9.3 启动服务
```bash
systemctl daemon-reload
systemctl start career-agent
systemctl enable career-agent
```

### 9.4 常用命令
```bash
# 查看状态
systemctl status career-agent

# 查看日志
journalctl -u career-agent -f

# 重启服务
systemctl restart career-agent

# 停止服务
systemctl stop career-agent
```

---

## 10. 常见问题

### Q1: SSH 连接超时
**解决方案**：
- 检查安全组是否开放 22 端口
- 检查本地网络
- 使用阿里云控制台的"远程连接"功能

### Q2: pip 安装很慢
**解决方案**：
- 使用清华镜像源（我们已经用了）
- 或者：`pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`

### Q3: 端口被占用
**解决方案**：
```bash
# 查看端口占用
netstat -tlnp | grep 9000

# 杀死进程
kill -9 <PID>
```

### Q4: 模型调用失败
**解决方案**：
- 检查 API Key 是否正确
- 检查 `.env` 文件中的配置
- 查看日志：`journalctl -u career-agent -f`

### Q5: 前端访问不到
**解决方案**：
- 检查安全组是否开放 9000 端口
- 检查服务是否运行：`systemctl status career-agent`
- 检查防火墙：`ufw status`

---

## 11. 下一步

- 配置域名（可选）
- 配置 HTTPS（使用 Let's Encrypt）
- 配置 Nginx 反向代理
- 设置定期备份

详细内容请参考 `DEPLOYMENT_GUIDE.md`。

---

**祝你部署顺利！** 🎉
