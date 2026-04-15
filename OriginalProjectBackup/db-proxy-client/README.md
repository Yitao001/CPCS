# 数据库代理客户端 - 使用教程

## 目录
1. [快速开始](#1-快速开始)
2. [配置说明](#2-配置说明)
3. [中继服务测试](#3-中继服务测试)
4. [智能体 API 测试](#4-智能体-api-测试)
5. [常见问题](#5-常见问题)

---

## 1. 快速开始

### 1.1 环境要求
- Python 3.8+
- Windows / Linux / Mac

### 1.2 安装步骤

#### Windows 用户
1. 解压本文件夹
2. 双击运行 `start.bat`
3. 首次运行会自动创建 `.env` 文件
4. 用记事本打开 `.env`，修改配置
5. 再次双击 `start.bat`

#### Mac / Linux 用户
```bash
# 1. 进入文件夹
cd db-proxy-client

# 2. 复制配置文件
cp .env.example .env

# 3. 编辑配置
vim .env

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行客户端
python client.py
```

---

## 2. 配置说明

编辑 `.env` 文件：

```env
# ==========================================
# 中继服务配置
# ==========================================
RELAY_URL=ws://47.102.145.89:8002  # 云服务器中继服务地址
CLIENT_ID=my_client_001                # 您的客户端唯一标识

# ==========================================
# 数据库配置
# ==========================================
MYSQL_HOST=127.0.0.1
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

#### 中继服务配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| RELAY_URL | 云服务器中继服务的 WebSocket 地址 | ws://your-server:8002 |
| CLIENT_ID | 您的客户端唯一标识（可以自己命名） | school_a_client |

#### 数据库配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| MYSQL_HOST | 数据库地址 | 127.0.0.1 |
| MYSQL_PORT | 数据库端口 | 3306 |
| MYSQL_USER | 数据库用户名 | root |
| MYSQL_PASSWORD | 数据库密码 | your_password |
| MYSQL_DATABASE | 数据库名称 | student_talk_db |

#### 表结构配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| TABLE_NAME | 谈话记录表名 | chat_records |
| STUDENT_ID_FIELD | 学生ID字段名 | student_id |
| CONTENT_FIELD | 谈话内容字段名 | content |
| CREATED_TIME_FIELD | 创建时间字段名 | created_time |
| QUERY_LIMIT | 单次查询最大记录数 | 100 |

### 灵活的表结构适配

本客户端支持适配不同的表结构，无需修改代码。如果您的表结构与默认不同，只需修改表结构配置即可：

**示例1：使用不同的表名和字段名**
```env
TABLE_NAME=talk_history
STUDENT_ID_FIELD=user_id
CONTENT_FIELD=message
CREATED_TIME_FIELD=time
QUERY_LIMIT=50
```

**示例2：使用 talk_record 表（旧版结构）**
```env
TABLE_NAME=talk_record
STUDENT_ID_FIELD=student_id
CONTENT_FIELD=content
CREATED_TIME_FIELD=created_time
```

**安全说明**：表名和字段名只允许包含字母、数字和下划线，确保 SQL 注入安全。

---

## 3. 中继服务测试

### 3.1 启动客户端
运行客户端后，看到以下信息表示连接成功：

```
============================================================
数据库代理客户端启动中...
============================================================
客户端ID: my_client_001
中继服务: ws://47.102.145.89:8002
数据库: 127.0.0.1:3306/student_talk_db
表结构: chat_records
  - 学生ID字段: student_id
  - 内容字段: content
  - 时间字段: created_time
  - 查询限制: 100条
============================================================
正在连接中继服务: ws://47.102.145.89:8002/ws/client/my_client_001
已连接到中继服务: my_client_001
```

### 3.2 验证客户端在线
联系服务提供方，他们可以通过中继服务的 API 查看您的客户端是否在线：

```
GET http://your-server:8002/clients
```

应该会返回您的 `CLIENT_ID`。

---

## 4. 智能体 API 测试

### 4.1 获取 API Key
从服务提供方获取您的 API Key。

### 4.2 访问 API 文档
在浏览器中打开：
```
http://your-server:8000/docs
```

### 4.3 测试步骤

#### 第1步：认证
1. 点击右上角的 **Authorize**
2. 输入您的 API Key
3. 点击 **Authorize** 完成认证

#### 第2步：测试健康检查
找到 `GET /health/lite` 接口，点击 **Try it out**，然后 **Execute**。

预期响应：
```json
{
  "status": "ok"
}
```

#### 第3步：测试学生画像分析
找到 `POST /analyze/simple` 接口，点击 **Try it out**，输入：

```json
{
  "participant_id": "test_student_001"
}
```

点击 **Execute**，等待几秒钟，AI会返回学生画像分析结果。

### 4.4 使用 curl 测试

```bash
# 测试健康检查
curl -X GET "http://your-server:8000/health/lite"

# 测试学生画像分析
curl -X POST "http://your-server:8000/analyze/simple" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"participant_id": "test_student_001"}'
```

---

## 5. 常见问题

### Q1: 客户端连接中继服务失败？
**A:** 检查以下几点：
1. 网络连接是否正常
2. `RELAY_URL` 是否正确
3. 防火墙是否阻止了 WebSocket 连接
4. 中继服务是否正常运行

### Q2: 数据库连接失败？
**A:** 检查：
1. MySQL 服务是否启动
2. 用户名密码是否正确
3. 数据库名称是否正确
4. 用户是否有访问该数据库的权限

### Q3: 如何确认客户端正在运行？
**A:** 看客户端窗口是否显示"已连接到中继服务"。

### Q4: 如何查看日志？
**A:** 客户端窗口会实时显示日志信息。

### Q5: 可以在多台电脑上运行客户端吗？
**A:** 可以！每台电脑使用不同的 `CLIENT_ID` 即可。

### Q6: 数据安全吗？
**A:** 非常安全！
- 您的数据永远在本地，不会上传到云端
- 连接由您主动发起，服务提供方无法主动访问您的内网
- 只有授权的请求才会查询您的数据库
- 表名和字段名有安全验证，防止 SQL 注入

### Q7: 我的表结构和默认不同怎么办？
**A:** 没关系！通过修改 `.env` 文件中的表结构配置即可适配：
- `TABLE_NAME`: 修改为您的表名
- `STUDENT_ID_FIELD`: 修改为您的学生ID字段名
- `CONTENT_FIELD`: 修改为您的内容字段名
- `CREATED_TIME_FIELD`: 修改为您的时间字段名

### Q8: 表名和字段名有什么限制？
**A:** 为了安全起见，表名和字段名只允许包含：
- 字母（a-z, A-Z）
- 数字（0-9）
- 下划线（_）

不允许包含特殊字符或 SQL 关键字。

### Q9: 如何验证表结构配置是否正确？
**A:** 
1. 启动客户端后，查看启动信息中的表结构配置
2. 确保显示的表名和字段名与您的数据库一致
3. 通过智能体 API 测试查询功能

---

## 6. 数据库表结构要求

### 6.1 默认表结构

如果您还没有学生谈话记录表，请按以下结构创建：

```sql
CREATE TABLE chat_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id)
);
```

### 6.2 字段说明（默认结构）

| 字段名 | 类型 | 说明 | 是否必填 |
|--------|------|------|----------|
| id | INT | 自增主键 | 是 |
| student_id | VARCHAR(50) | 学生唯一标识 | 是 |
| content | TEXT | 谈话内容 | 是 |
| created_time | DATETIME | 创建时间 | 是 |

### 6.3 自定义表结构

如果您已有其他结构的表，可以通过配置灵活适配。以下是几种常见场景：

**场景1：表名不同**
```env
TABLE_NAME=talk_history
```

**场景2：字段名不同**
```env
STUDENT_ID_FIELD=user_id
CONTENT_FIELD=message
CREATED_TIME_FIELD=record_time
```

**场景3：完整自定义示例**
```env
TABLE_NAME=conversation_logs
STUDENT_ID_FIELD=participant_id
CONTENT_FIELD=dialogue
CREATED_TIME_FIELD=log_time
QUERY_LIMIT=200
```

### 6.4 插入测试数据

配置完成后，可以插入一些测试数据验证：

```sql
INSERT INTO chat_records (student_id, content, created_time) VALUES
('S2023003', '学生最近学习状态很好，数学成绩进步明显', '2026-04-01 09:00:00'),
('S2023003', '需要关注英语阅读能力的提升', '2026-04-02 14:30:00'),
('S2023005', '该生性格开朗，善于与人交流', '2026-04-03 10:00:00');
```

---

## 7. 技术支持

如果您遇到任何问题，请联系我们的技术支持团队。

---

**祝您使用愉快！**
