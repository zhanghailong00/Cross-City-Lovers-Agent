# 异地情侣智能汇合出行规划系统开发设计文档

## 1. 项目定位

本项目旨在构建一个“LLM + 规则引擎 + 数据服务”混合式 Agent 系统，面向异地情侣的汇合出行规划场景。

目标不是单纯寻找地理中点，而是在综合考虑：

- 双方交通可达性
- 总预算约束
- 公平性
- 城市游玩价值
- 输出可解释性

后，为用户推荐一个最优汇合城市，并给出双方详细出行方案。

## 2. MVP 范围

第一版只实现以下能力：

1. 接收一段中文自然语言输入。
2. 结构化解析出双方城市、日期、天数、预算和偏好。
3. 生成 5 个以内的候选汇合城市。
4. 为双方生成去程交通方案。
5. 对候选城市进行配对与评分，给出 Top1 + Top3。
6. 输出用户可读结果和结构化 JSON。

第一版边界约束：

- 仅支持中国境内城市
- 仅支持高铁/动车
- 仅支持去程
- 预算按“两人总预算”处理
- 可运行在估算/Mock 模式
- LLM 仅负责理解和解释，不负责数值决策

## 3. 核心设计原则

### 3.1 LLM 的职责

LLM 只负责：

- 用户意图解析
- 候选城市补充与语义去噪
- 推荐理由生成

LLM 不负责：

- 车次事实生成
- 票价计算
- 排名决策
- 最优解选择

### 3.2 业务决策职责

- 数据提供层负责“事实”
- 规则和算法层负责“决策”
- Agent 编排层负责“流程”
- API 层负责“对外协议”

## 4. 总体架构

```text
用户输入
  -> 意图解析
  -> 约束标准化
  -> 候选城市生成
  -> 交通方案获取
  -> 双边路线配对
  -> 城市评分排序
  -> Top-K 选择
  -> 推荐解释生成
  -> 最终格式化输出
```

## 5. 核心数据模型

### 5.1 Intent

结构化用户意图对象，包含：

- `origin_a`
- `origin_b`
- `departure_date`
- `days`
- `total_budget`
- `preferences`
- `priority`
- `allow_transfer`
- `transport_mode`
- `data_mode`

### 5.2 CandidateCity

候选汇合城市对象，包含：

- 城市名称
- 城市等级
- 高铁枢纽等级
- 旅游体验分
- 消费等级
- 标签

### 5.3 TransportOption

单条交通方案对象，包含：

- 出发城市
- 到达城市
- 日期
- 交通方式
- 车次
- 出发/到达站
- 出发/到达时间
- 时长
- 价格
- 数据来源级别

### 5.4 PairedRoutePlan

某个候选城市下，双方最佳交通组合对象，包含：

- 双方具体路线
- 汇合站点
- 汇合时间
- 等待时间
- 总耗时
- 总成本
- 时间差
- 费用差
- 路线分

### 5.5 CityRecommendation

城市级推荐结果对象，包含：

- 城市
- 代表性双边路线
- 路线分
- 城市分
- 最终分
- 推荐标签

### 5.6 FinalRecommendationResult

最终返回对象，包含：

- 推荐城市
- 备选城市
- 最佳方案
- 备选方案摘要
- 推荐理由
- 风险提示

## 6. 评分模型设计

### 6.1 路线层评分

路线层针对某个候选城市下的一组具体双人路线组合进行评分。

核心指标：

- 双方总耗时
- 双方总花费
- 双方耗时差
- 双方费用差
- 等待时间
- 预算惩罚

评分方向统一为“越低越好”。

### 6.2 城市层评分

城市层基于该城市下的最佳路线组合，再叠加：

- 城市消费水平
- 城市体验分
- 高铁通达性

形成最终综合排序。

### 6.3 硬约束

第一版建议使用以下硬过滤：

- 单边行程不超过 8 小时
- 双方等待不超过 120 分钟
- 交通总花费不超过交通预算的 130%
- 第一版默认仅保留直达方案

## 7. LangGraph 工作流节点

### 7.1 ParseIntent

输入：`raw_query`

输出：`intent`

### 7.2 NormalizeConstraints

输入：`intent`

输出：`normalized_intent`、`warnings`

### 7.3 GenerateCandidateCities

输入：`normalized_intent`

输出：`candidate_cities`

### 7.4 FetchTransportOptions

输入：`normalized_intent`、`candidate_cities`

输出：`transport_options_map`

### 7.5 PairRoutes

输入：`transport_options_map`

输出：`paired_route_plans`

### 7.6 ScoreCandidates

输入：`paired_route_plans`、`candidate_cities`

输出：`ranked_recommendations`

### 7.7 SelectTopK

输入：`ranked_recommendations`

输出：`top_result`、`alternative_results`

### 7.8 GenerateExplanation

输入：`top_result`、`alternative_results`

输出：`reasoning`、`notes`

### 7.9 FormatFinalResponse

输入：上游全部关键结果

输出：`final_result`

## 8. 目录结构

```text
app/
  api/
  core/
  domain/
  providers/
  repositories/
  schemas/
  services/
  utils/
  workflows/
  prompts/
config/
data/
docs/
tests/
```

## 9. 配置与安全设计

### 9.1 配置分层

- `config/settings.toml`：公共配置，可提交
- `config/secrets.toml`：本地敏感配置，不提交
- `config/secrets.example.toml`：敏感配置模板，可提交

### 9.2 密钥管理原则

- 任何 API Key 不得写死在代码中
- 不得把真实密钥写入示例文件
- 生产环境建议通过环境变量或密钥服务注入

## 10. 第一阶段开发顺序

### 10.1 骨架阶段

目标：

- 建好项目目录
- 建好配置体系
- 定义核心领域模型
- 建立最小 API 入口
- 建立最小 LangGraph 工作流

### 10.2 无 LLM MVP 阶段

目标：

- 先用规则和估算跑通完整推荐闭环

### 10.3 LLM 接入阶段

目标：

- 提升意图解析与解释生成能力

### 10.4 数据增强阶段

目标：

- 增强交通数据真实性

## 11. 第一版落地重点

第一版最关键的不是页面，而是：

1. 数据模型稳定
2. 路线配对逻辑稳定
3. 评分解释清晰
4. 流程结构可扩展

因此，当前代码骨架应优先围绕：

- 配置
- 模型
- 工作流状态
- 服务层边界
- API 协议

展开，而不是过早投入复杂前端或真实外部接口整合。

