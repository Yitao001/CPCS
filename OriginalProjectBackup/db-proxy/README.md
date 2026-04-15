# 数据库代理服务 - 使用教程

## 目录
1. [快速开始](#1-快速开始)
2. [配置说明](#2-配置说明)
3. [代理服务测试](#3-代理服务测试)
4. [常见问题](#4-常见问题)

> **注意**：这是旧版 HTTP 代理方式，推荐使用新的 [WebSocket 中继模式](../db-proxy-client/README.md)！

---

## 1. 快速开始

### 1.1 什么是数据库代理服务？
数据库代理服务是一个运行在您本地电脑上的服务，它允许智能体安全地访问您的本地数据库，而无需将数据上传到云端。

### 1.2 环境要求
- Python 3.8+
- Windows / Linux / Mac
- MySQL 数据库

### 1.3 安装步骤

#### Windows 用户
1. 解压本文件夹
2. 双击运行 `start.bat`
3. 首次运行会自动创建 `.env` 文件
4. 用记事本打开 `.env`，修改配置
5. 再次双击 `start.bat`

#### Mac / Linux 用户
```bash
# 1. 进入文件夹
cd db-proxy

# 2. 复制配置文件
cp .env.example .env

# 3. 编辑配置
vim .env

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行代理服务
python main.py
```

---

## 2. 配置说明

编辑 `.env` 文件：

```env
# ==========================================
# 代理API Key（由智能体服务提供方提供）
# ==========================================
PROXY_API_KEY=test_proxy_key_123

# ==========================================
# 您的数据库配置
# ==========================================
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=student_talk_db

# ==========================================
# 表结构配置
# ==========================================
TABLE_NAME=chat_records
STUDENT_ID_FIELD=student_id
CONTENT_FIELD=content
CREATED_TIME_FIELD=created_time
QUERY_LIMIT=100
```

### 配置项详解

| 配置项 | 说明 | 示例 |
|--------|------|------|
| PROXY_API_KEY | 代理服务的 API Key（由服务提供方提供） | your_secure_key |
| MYSQL_HOST | 数据库地址 | localhost |
| MYSQL_PORT | 数据库端口 | 3306 |
| MYSQL_USER | 数据库用户名 | root |
| MYSQL_PASSWORD | 数据库密码 | your_password |
| MYSQL_DATABASE | 数据库名称 | student_talk_db |
| TABLE_NAME | 谈话记录表名 | chat_records |
| STUDENT_ID_FIELD | 学生ID字段名 | student_id |
| CONTENT_FIELD | 谈话内容字段名 | content |
| CREATED_TIME_FIELD | 创建时间字段名 | created_time |
| QUERY_LIMIT | 单次查询最大条数 | 100 |

---

## 3. 代理服务测试

### 3.1 启动服务
运行后，看到以下信息表示启动成功：

```
============================================================
数据库代理服务启动中...
============================================================
数据库配置: localhost:3306/student_talk_db
API文档: http://localhost:8001/docs
============================================================
```

### 3.2 访问 API 文档
在浏览器中打开：
```
http://localhost:8001/docs
```

### 3.3 测试步骤

#### 第1步：认证
1. 点击右上角的 **Authorize**
2. 输入您的 `PROXY_API_KEY`
3. 点击 **Authorize** 完成认证

#### 第2步：测试健康检查
找到 `GET /health` 接口，点击 **Try it out**，然后 **Execute**。

预期响应：
```json
{
  "status": "ok",
  "database": "ok"
}
```

#### 第3步：测试获取对话历史
找到 `POST /chat-history` 接口，点击 **Try it out**，输入：

```json
{
  "student_id": "test_student_001",
  "limit": 10
}
```

点击 **Execute**，应该会返回该学生的历史谈话记录。

### 3.4 使用 curl 测试

```bash
# 测试健康检查
curl -X GET "http://localhost:8001/health" \
  -H "X-Proxy-API-Key: your_proxy_api_key"

# 测试获取对话历史
curl -X POST "http://localhost:8001/chat-history" \
  -H "Content-Type: application/json" \
  -H "X-Proxy-API-Key: your_proxy_api_key" \
  -d '{"student_id": "test_student_001", "limit": 10}'
```

---

## 4. 常见问题

### Q1: 代理服务启动失败？
**A:** 检查以下几点：
1. Python 是否安装：`python --version`
2. 数据库服务是否启动
3. 端口 8001 是否被占用

### Q2: 数据库连接失败？
**A:** 检查：
1. MySQL 服务是否启动
2. 用户名密码是否正确
3. 数据库名称是否正确
4. 用户是否有访问权限

### Q3: 智能体无法访问我的代理？
**A:** 
- 如果智能体和代理在同一台电脑上，使用 `http://localhost:8001`
- 如果智能体在云端，您需要配置内网穿透（如 ngrok）或使用新的 [WebSocket 中继模式](../db-proxy-client/README.md)

### Q4: 推荐使用哪种方式？
**A:** **强烈推荐使用新的 WebSocket 中继模式！**
- 无需公网 IP
- 无需配置端口映射
- 更安全
- 使用更简单

请查看 [db-proxy-client 文件夹的 README](../db-proxy-client/README.md) 了解更多。

---

## 5. 数据库表结构要求

### 方案A：使用现有数据库
确保您的表包含以下字段：
- `student_id`：学生唯一标识
- `content`：谈话内容
- `created_time`：创建时间（DATETIME类型）

### 方案B：创建新数据库
我们提供了示例表结构，在 `example_schema.sql` 文件中：

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS student_talk_db CHARACTER SET utf8mb4;

-- 使用数据库
USE student_talk_db;

-- 创建表
CREATE TABLE IF NOT EXISTS chat_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id)
);

-- 插入测试数据
INSERT INTO chat_records (student_id, content, created_time) VALUES
('S2023001', '今天学习了数学，感觉有点难，特别是几何部分。', '2026-04-01 09:00:00'),
('S2023001', '老师布置了新的作业，我会认真完成的。', '2026-04-02 14:30:00');
```

---

## 6. 从 HTTP 代理迁移到 WebSocket 中继

**强烈建议升级到 WebSocket 中继模式！**

迁移步骤：
1. 查看 [db-proxy-client/README.md](../db-proxy-client/README.md)
2. 使用新的客户端程序
3. 配置中继服务地址
4. 享受更简单、更安全的使用体验

---

## 7. 技术支持

如果您遇到任何问题，请联系我们的技术支持团队。

---

**祝您使用愉快！**
