# 大学生职业规划智能体 - 部署指南

## 目录
1. [服务器要求](#1-服务器要求)
2. [传统部署（推荐）](#2-传统部署推荐)
3. [Docker 部署](#3-docker-部署)
4. [Nginx 反向代理](#4-nginx-反向代理)
5. [安全配置](#5-安全配置)
6. [故障排查](#6-故障排查)

---

## 1. 服务器要求

### 最低配置
- CPU：2 核
- 内存：4 GB
- 硬盘：20 GB
- 操作系统：Linux（Ubuntu 20.04+ / CentOS 7+）或 Windows Server

### 推荐配置
- CPU：4 核
- 内存：8 GB
- 硬盘：50 GB
- 操作系统：Ubuntu 22.04 LTS

---

## 2. 传统部署（推荐）

### 2.1 环境准备

#### 安装 Python 3.8+

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

**CentOS/RHEL:**
```bash
sudo yum install python3 python3-pip -y
```

### 2.2 上传项目文件

将项目文件上传到服务器：

```bash
mkdir -p /opt/career-planning-agent
cd /opt/career-planning-agent
```

然后通过以下方式上传：
- Git 克隆：`git clone <你的仓库地址> .`
- SFTP 上传：使用 FileZilla 等工具
- SCP 上传：`scp -r local_dir user@server:/opt/career-planning-agent`

### 2.3 创建虚拟环境

```bash
cd /opt/career-planning-agent
python3 -m venv venv
source venv/bin/activate
```

### 2.4 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2.5 配置环境变量

```bash
cp .env.example .env
nano .env
```

编辑 `.env` 文件，配置以下内容：

```env
MODEL_PROVIDER=siliconflow
CHAT_MODEL_NAME=siliconflow/deepseek-ai/DeepSeek-V3
SILICONFLOW_API_KEY=sk-你的APIKey
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
HOST=0.0.0.0
PORT=9000
API_KEY=your_secure_api_key_here
CORS_ORIGINS=*
```

### 2.6 测试运行

```bash
python test_simple.py
```

确保所有测试通过后，再启动服务。

### 2.7 使用 Gunicorn 部署（生产环境）

#### 安装 Gunicorn

```bash
pip install gunicorn
```

#### 创建 Gunicorn 配置文件

创建 `gunicorn_config.py`：

```python
import multiprocessing

bind = "0.0.0.0:9000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5
preload_app = True
daemon = True
pidfile = "/var/run/career_agent.pid"
accesslog = "/var/log/career_agent_access.log"
errorlog = "/var/log/career_agent_error.log"
loglevel = "info"
```

#### 创建日志目录

```bash
sudo mkdir -p /var/log/career-agent
sudo chown $USER:$USER /var/log/career-agent
sudo mkdir -p /var/run/career-agent
sudo chown $USER:$USER /var/run/career-agent
```

#### 启动服务

```bash
gunicorn -c gunicorn_config.py api:app
```

### 2.8 使用 Systemd 管理服务

#### 创建 Systemd 服务文件

```bash
sudo nano /etc/systemd/system/career-planning-agent.service
```

内容如下：

```ini
[Unit]
Description=Career Planning Agent Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/career-planning-agent
Environment="PATH=/opt/career-planning-agent/venv/bin"
ExecStart=/opt/career-planning-agent/venv/bin/gunicorn -c gunicorn_config.py api:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 启动并启用服务

```bash
sudo systemctl daemon-reload
sudo systemctl start career-planning-agent
sudo systemctl enable career-planning-agent
```

#### 查看服务状态

```bash
sudo systemctl status career-planning-agent
```

#### 查看日志

```bash
# 查看服务日志
sudo journalctl -u career-planning-agent -f

# 查看应用日志
tail -f /var/log/career_agent_access.log
tail -f /var/log/career_agent_error.log
```

---

## 3. Docker 部署

### 3.1 创建 Dockerfile

在项目根目录创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

RUN mkdir -p data/student_data data/reports

EXPOSE 9000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "9000"]
```

### 3.2 创建 .dockerignore

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
venv
.env
.git
.gitignore
test_*.py
demo_*.py
```

### 3.3 构建 Docker 镜像

```bash
docker build -t career-planning-agent:latest .
```

### 3.4 运行 Docker 容器

```bash
docker run -d \
  --name career-agent \
  -p 9000:9000 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/data/student_data:/app/data/student_data \
  -v $(pwd)/data/reports:/app/data/reports \
  --restart unless-stopped \
  career-planning-agent:latest
```

### 3.5 使用 Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  career-agent:
    build: .
    container_name: career-planning-agent
    ports:
      - "9000:9000"
    environment:
      - MODEL_PROVIDER=${MODEL_PROVIDER}
      - SILICONFLOW_API_KEY=${SILICONFLOW_API_KEY}
      - API_KEY=${API_KEY}
    volumes:
      - ./data/student_data:/app/data/student_data
      - ./data/reports:/app/data/reports
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

启动服务：

```bash
docker-compose up -d
```

---

## 4. Nginx 反向代理

### 4.1 安装 Nginx

```bash
sudo apt install nginx -y
```

### 4.2 创建 Nginx 配置文件

```bash
sudo nano /etc/nginx/sites-available/career-agent
```

内容如下：

```nginx
upstream career_backend {
    server 127.0.0.1:9000;
    keepalive 32;
}

server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://career_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_request_buffering off;
    }

    location /docs {
        proxy_pass http://career_backend;
        proxy_set_header Host $host;
    }

    location /redoc {
        proxy_pass http://career_backend;
        proxy_set_header Host $host;
    }

    access_log /var/log/nginx/career_agent_access.log;
    error_log /var/log/nginx/career_agent_error.log;
}
```

### 4.3 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/career-agent /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
```

### 4.4 测试并重启 Nginx

```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 4.5 配置 HTTPS（使用 Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 5. 安全配置

### 5.1 防火墙配置

**Ubuntu/Debian:**
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

**CentOS/RHEL:**
```bash
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 5.2 定期备份

创建备份脚本 `backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/career-agent"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份数据
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /opt/career-planning-agent/data

# 备份配置
cp /opt/career-planning-agent/.env $BACKUP_DIR/env_$DATE

# 保留最近 7 天的备份
find $BACKUP_DIR -type f -mtime +7 -delete
```

添加到 crontab：

```bash
crontab -e
```

添加每日备份：

```
0 2 * * * /opt/career-planning-agent/backup.sh
```

---

## 6. 故障排查

### 6.1 服务无法启动

```bash
# 检查端口占用
netstat -tlnp | grep 9000

# 检查配置文件
python -c "import dotenv; dotenv.load_dotenv(); print('Config loaded')"

# 手动运行查看错误
python api.py
```

### 6.2 模型调用失败

- 检查 API Key 是否正确
- 检查网络连接
- 查看应用日志

### 6.3 部署检查清单

- [ ] 服务器环境准备完成
- [ ] Python 版本符合要求
- [ ] 项目文件上传完成
- [ ] 虚拟环境创建完成
- [ ] 依赖安装完成
- [ ] 环境变量配置完成
- [ ] 测试运行通过
- [ ] 服务启动成功
- [ ] Nginx 配置完成
- [ ] HTTPS 配置完成（可选）
- [ ] 防火墙配置完成
- [ ] 备份脚本配置完成

---

## 7. 更多帮助

- 项目开发指南：`PROJECT_GUIDE.md`
- 使用指南：`USER_GUIDE.md`

祝您部署顺利！
