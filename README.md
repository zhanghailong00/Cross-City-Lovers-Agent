# Cross-City Lovers Agent

LLM 驱动的异地情侣智能汇合出行规划系统。

当前仓库为第一阶段可演示版本，已经实现从自然语言输入到结构化汇合方案输出的最小闭环。

## 当前版本

- 版本定位：`MVP v1 / v0.1.0`
- 当前状态：可本地运行、可接口演示、可继续扩展
- 数据模式：以估算交通数据为主，尚未接入真实票务接口

## 已实现能力

- 支持中文自然语言输入
- 支持解析双方出发城市、日期、天数、预算等基础信息
- 支持生成候选汇合城市
- 支持生成双方去程交通方案
- 支持路线配对、评分、排序
- 支持返回 Top1 推荐城市与备选城市
- 支持返回结构化 JSON 和用户可读展示文本
- 支持 FastAPI 接口调用
- 支持最小自动化测试

## 示例输入

```text
我在北京，她在杭州，2026-05-01出发，玩3天，预算2000，想找个适合见面的城市
```

## 示例输出能力

- 推荐城市：南京
- 备选城市：合肥、苏州、武汉
- 双方详细去程方案
- 汇合时间
- 推荐理由
- 风险提示

## 技术栈

- Python
- FastAPI
- LangGraph
- Pydantic
- unittest

说明：

- 当前项目在未安装 `langgraph` 的环境下，也可以自动降级为顺序执行模式，方便本地开发。

## 项目结构

```text
app/
  api/            # API 入口
  core/           # 配置与基础设施
  domain/         # 领域模型
  providers/      # 外部能力提供层
  repositories/   # 数据读取层
  schemas/        # 请求响应结构
  services/       # 业务服务层
  utils/          # 通用工具
  workflows/      # 工作流编排
  prompts/        # Prompt 模板
config/           # 配置文件
data/             # 种子数据
docs/             # 开发设计文档
scripts/          # 本地脚本
tests/            # 测试
```

## 快速开始

### 1. 准备配置文件

```powershell
Copy-Item config/secrets.example.toml config/secrets.toml
```

### 2. 安装依赖

```powershell
python -m pip install -e .
```

如果你使用 Conda，也可以执行：

```powershell
conda env update -f environment.yml --prune
```

### 3. 运行测试

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

### 4. 启动服务

直接启动：

```powershell
python -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload
```

或使用脚本启动：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_local.ps1
```

如果依赖未安装完成，也可以先执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_env.ps1
```

### 5. 打开接口文档

```text
http://127.0.0.1:8000/docs
```

## 主要接口

### `POST /api/v1/plans/generate`

请求体：

```json
{
  "raw_query": "我在北京，她在杭州，2026-05-01出发，玩3天，预算2000，想找个适合见面的城市"
}
```

返回特点：

- `data.best_plan`：结构化最佳方案
- `data.other_plans`：备选方案
- `data.reasoning`：推荐理由
- `data.notes`：提示信息
- `data.display_text`：用户可读展示版本

## 文档

- 开发设计文档：[docs/development_design.md](docs/development_design.md)
- 版本说明：[CHANGELOG.md](CHANGELOG.md)

## 当前限制

- 当前交通方案为估算数据，不代表真实票务结果
- 当前仅支持高铁/动车场景
- 当前仅支持去程规划
- 当前意图解析仍以规则为主，复杂表达的兼容度有限
- 当前尚未接入真实 LLM 主流程和真实交通 API

## 安全说明

- 真实密钥不得提交到仓库
- 本地密钥文件应写入 `config/secrets.toml`
- 仓库中仅保留 `config/secrets.example.toml` 作为模板

## 建议发布信息

- 推荐标签：`v0.1.0`
- 推荐发布名：`MVP v1 - Demo Release`

