# Excel + RAG 使用指南

## 📋 概述

本系统**完全基于** Excel 文件读取岗位数据，使用向量数据库进行存储，并通过 RAG（检索增强生成）技术为智能体提供真实岗位数据支持。

**已删除旧的 JSON 数据和相关逻辑，系统现在只使用 Excel 导入的数据！

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pandas openpyxl chromadb langchain-chroma sentence-transformers
```

或者安装所有依赖：
```bash
pip install -r requirements.txt
```

---

### 2. 准备 Excel 文件

Excel 文件应包含以下列（列名可以是中文）：

| 列名 | 说明 | 是否必需 |
|------|------|----------|
| 岗位名称 | 岗位名称 | ✅ |
| 地址 | 工作地址 | ⭕ |
| 薪资范围 | 薪资范围 | ⭕ |
| 公司名称 | 公司名称 | ⭕ |
| 所属行业 | 所属行业 | ⭕ |
| 公司规模 | 公司规模 | ⭕ |
| 公司类型 | 公司类型 | ⭕ |
| 岗位编码 | 岗位编码 | ⭕ |
| 岗位详情 | 岗位详情/描述 | ⭕ |
| 更新日期 | 更新日期 | ⭕ |
| 公司详情 | 公司详情 | ⭕ |
| 岗位来源地址 | 岗位来源链接 | ⭕ |

---

### 3. 创建示例 Excel（可选）

如果没有现成的 Excel 文件，可以从现有的 JSON 数据生成示例：

```bash
python create_sample_excel.py
```

这会在 `data/job_data/sample_jobs.xlsx` 创建一个示例 Excel 文件。

---

### 4. 导入 Excel 到向量库

```bash
# 基本导入
python import_excel.py data/job_data/your_file.xlsx

# 导入并清空之前的数据
python import_excel.py data/job_data/your_file.xlsx --clear

# 导入并测试检索功能
python import_excel.py data/job_data/your_file.xlsx --test
```

示例：
```bash
python import_excel.py data/job_data/sample_jobs.xlsx --test
```

---

## 📁 项目结构

```
e:\yuanma\CPCS\
├── data/
│   ├── job_data/              # 岗位数据目录
│   │   ├── job_portraits.json # 原 JSON 数据
│   │   └── sample_jobs.xlsx   # 示例 Excel（生成）
│   ├── vector_db/              # 向量数据库（自动生成）
│   ├── vector_db_manager.py    # 向量库管理模块
│   └── excel_importer.py       # Excel 导入模块
├── agent/
│   └── tools/
│       └── agent_tools.py      # 智能体工具（已更新）
├── prompts/
│   └── main_prompt.txt         # 主提示词（已更新）
├── import_excel.py             # 导入脚本
├── create_sample_excel.py      # 生成示例 Excel
└── RAG_GUIDE.md                # 本文件
```

---

## 🎯 功能说明

### 1. 向量数据库管理 (`data/vector_db_manager.py`)

- 使用 ChromaDB 作为向量数据库
- 使用 Sentence-Transformers 进行 Embedding
- 支持添加、检索、清空文档

### 2. Excel 导入 (`data/excel_importer.py`)

- 读取 Excel 文件（.xlsx 格式）
- 自动解析岗位数据
- 将数据转换为向量文档
- 存储到向量库
- 同时保存 JSON 备份

### 3. 智能体工具 (`agent/tools/agent_tools.py`)

新增工具：
- `search_relevant_jobs(query, top_k)`: 从向量库检索相关岗位

### 4. 提示词优化 (`prompts/main_prompt.txt`)

- 引导智能体优先使用 RAG 检索
- 提供真实岗位数据支持

---

## 💡 使用示例

### 场景 1：用户询问 Java 开发岗位

**用户**：我想了解 Java 开发岗位的情况

**智能体**：（自动调用 `search_relevant_jobs("Java开发")`）
```
找到 3 个相关岗位：

【岗位 1】
岗位名称: Java后端开发工程师
公司名称: 示例科技公司
所属行业: 互联网
薪资范围: 15-30K
工作地址: 北京-朝阳区
匹配度: 92.5%

详细信息:
岗位名称: Java后端开发工程师
...
```

---

### 场景 2：用户询问薪资水平

**用户**：大数据岗位薪资怎么样？

**智能体**：（自动调用 `search_relevant_jobs("大数据")`）
```
根据检索到的岗位数据：

1. 大数据开发工程师 - 20-40K
2. 数据分析师 - 15-25K
3. 算法工程师 - 25-50K

大数据相关岗位的薪资普遍较高，建议...
```

---

## 🔧 API 接口（可选）

如果需要通过 API 使用 RAG 功能，可以添加以下接口：

```python
# 在 api.py 中添加
from data.excel_importer import search_jobs, import_jobs_from_excel

@app.post("/import-excel", summary="导入 Excel 岗位数据")
async def import_excel_endpoint(file_path: str, clear: bool = False):
    success = import_jobs_from_excel(file_path, clear)
    return {"status": "success" if success else "error"}

@app.get("/search-jobs", summary="检索岗位")
async def search_jobs_endpoint(query: str, top_k: int = 5):
    results = search_jobs(query, top_k)
    return {"status": "success", "data": results}
```

---

## 📊 向量数据库

### 数据存储位置
- `data/vector_db/` - ChromaDB 持久化数据

### Embedding 模型
- 默认使用 `all-MiniLM-L6-v2`
- 轻量级，速度快，适合中文

### 检索方式
- 余弦相似度
- 返回最相关的 Top-K 结果

---

## ⚠️ 注意事项

1. **Excel 格式**：确保 Excel 文件使用 UTF-8 编码（保存时选择）
2. **列名匹配**：列名尽量使用中文，系统会自动识别
3. **首次导入**：首次使用需要下载 Embedding 模型（约 100MB）
4. **数据量**：建议首次导入 100-1000 条岗位数据
5. **更新数据**：更新数据时使用 `--clear` 参数清空旧数据

---

## 🎉 总结

现在你可以：
1. ✅ 从 Excel 导入岗位数据
2. ✅ 使用向量数据库存储
3. ✅ 智能体自动检索相关岗位
4. ✅ 基于真实数据提供建议

开始使用吧！🚀
