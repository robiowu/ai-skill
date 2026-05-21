# Spec: 知识案例化指导 (Knowledge Codification)

## ADDED Requirements

### Requirement: 案例模板规范指导
当 skill 设计包含知识积累需求时，系统 SHALL 指导用户使用统一的案例模板，确保案例可匹配、可操作、可复用。

#### Scenario: 推荐案例模板
- **WHEN** 用户表示 skill 需要案例积累（如审查类、分析类 skill）
- **THEN** 系统 SHALL 输出案例模板，包含：元信息（来源、严重度、类别）、触发模式（trigger_patterns）、模式描述、检查规则、关联知识

#### Scenario: 案例反例检测
- **WHEN** 用户提供的案例缺少触发模式或检查规则不可操作
- **THEN** 系统 SHALL 标记为设计缺陷，并给出修改建议（如"触发模式请改为可机械匹配的关键词列表"）

### Requirement: 触发模式可机械匹配性检查
系统 SHALL 检查案例的触发模式是否满足可机械匹配标准——基于关键词、正则、代码结构模式，而非语义理解。

#### Scenario: 合格的触发模式
- **WHEN** 触发模式为 "diff 中出现 `Cache`/`cache`/`CacheKey`/`cacheKey` 相关变量或函数"
- **THEN** 系统 SHALL 判定为合格，因为关键词可机械匹配

#### Scenario: 不合格的触发模式
- **WHEN** 触发模式为 "代码中存在对性能有隐患的操作"
- **THEN** 系统 SHALL 判定为不合格，因为"性能隐患"无法机械判断，需改为具体模式（如"循环内存在数据库查询"）

### Requirement: 检查规则可操作性检查
系统 SHALL 检查案例的检查规则是否遵循"找到 X → 比对 Y → 判断 Z"的可操作格式。

#### Scenario: 可操作的检查规则
- **WHEN** 检查规则为 "找到 CacheKey 生成逻辑和查询条件构建逻辑，逐一对比维度，判断 CacheKey 中的维度是否完整覆盖了所有影响查询结果的参数"
- **THEN** 系统 SHALL 判定为合格，因为明确了"找什么 → 比什么 → 怎么判断"

#### Scenario: 不可操作的检查规则
- **WHEN** 检查规则为 "注意缓存键的正确性"
- **THEN** 系统 SHALL 判定为不合格，因为没有具体的操作步骤，需要改写为可执行格式

### Requirement: 案例去项目化检查
系统 SHALL 检查案例是否去除了项目特定的变量名、路径、工单号，保留通用模式。

#### Scenario: 未去项目的案例
- **WHEN** 案例中直接出现了 `ProjectA_UserService`、`config/db_prod.yaml` 等特定名称
- **THEN** 系统 SHALL 建议替换为通用描述（如 "用户服务模块"、"数据库配置文件"），并提示"去项目化有利于案例跨项目复用"
