# Spec: Skill 自包含 (Skill Self-Containment)

> 定义 skill 如何解析内外部资源路径，消除对项目级目录结构的硬编码依赖，确保 skill 可独立部署。

## ADDED Requirements

### Requirement: 外部资源路径通过哨兵定位
系统 SHALL 通过哨兵文件（`openspec/config.yaml` 或 `.codemaker/` 目录）定位项目根目录，而非硬编码项目级相对路径。当 skill 引用 skill 外部资源（如 `openspec/specs/`）时，SHALL 从哨兵位置解析，而非假定固定目录深度。

#### Scenario: 哨兵文件存在时正确解析
- **WHEN** SKILL.md 引用 `openspec/specs/{name}/spec.md`
- **AND** 从 skill 目录向上查找到 `openspec/config.yaml`
- **THEN** 系统 SHALL 以 `openspec/config.yaml` 所在目录为项目根，拼接 `openspec/specs/{name}/spec.md` 路径读取

#### Scenario: 哨兵文件不存在时降级
- **WHEN** SKILL.md 引用 `openspec/specs/{name}/spec.md`
- **AND** 从 skill 目录向上查找未发现 `openspec/config.yaml` 或 `.codemaker/` 目录
- **THEN** 系统 SHALL 使用 SKILL.md 中声明的降级路径（如 `references/` 下的对应文件），并标注 ⚠️ "规范文件不可用，使用非规范版"

#### Scenario: 纯 skill 内部文件不变
- **WHEN** SKILL.md 引用 `references/design-patterns.md`（skill 自身 references/ 目录内的文件）
- **THEN** 系统 SHALL 直接以 skill 根目录为基准解析，不触发哨兵查找

### Requirement: 外部引用必须声明降级路径
每个对 skill 外部资源的引用 SHALL 按 `{依赖} → {降级行为} → {标注}` 格式声明降级路径，不可仅写路径而不说明不可用时的行为。

#### Scenario: 完整的降级声明格式
- **WHEN** SKILL.md 包含外部资源引用
- **THEN** 引用处 SHALL 附带降级声明，例如：`形式化规范：openspec/specs/{name}/spec.md → 若 openspec/ 目录不存在，以 references/{name}.md 为准 → ⚠️ 缺失形式化规范`

#### Scenario: 无降级声明的硬编码路径
- **WHEN** SKILL.md 包含对项目级路径的引用（如 `openspec/specs/`）
- **AND** 该引用未附带降级声明
- **THEN** 该引用 SHALL 被视为违反自包含原则，需修正

### Requirement: 降级文件必须存在
降级声明中引用的替代文件 SHALL 实际存在于 skill 目录内。不可声明一个不存在的降级路径。

#### Scenario: 降级路径指向存在的文件
- **WHEN** 降级声明为 `以 references/complex-workflow-guide.md 为准`
- **THEN** `references/complex-workflow-guide.md` SHALL 确实存在于 skill 目录中

#### Scenario: 降级路径指向不存在的文件
- **WHEN** 降级声明引用的文件经检查不存在
- **THEN** 系统 SHALL 标记为 Error（-2 分），提示降级路径无效——skill 在无 openspec 环境下将彻底不可用
