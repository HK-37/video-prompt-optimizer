# video-prompt-optimizer — 视频提示词优化 Skill

> 把“一个人打桌子”“两人对峙然后召唤机甲”这类自然语言，转成视频模型更容易执行的提示词。重点是意图、动作轨迹、空间关系、人物表演、光色和镜头衔接，不是堆华丽形容词。

**当前状态：开发预览版。** 已有完整的方法框架、参考词料、提示词扫描与回归测试；仍在补齐专业知识到优化规则的系统转化、更多题材和真实案例。它不是一个保证生成效果的成品服务。

## 能做什么

- 先登记创作用途、观众、不可变项与允许变化项，再做最小必要改写。
- 把模糊动作展开成可观察的轨迹、受力、姿态、视线与时序。
- 处理人物身份、空间、遮挡、光色和多镜头连续性；知道何时需要参考图而非继续堆词。
- 按模型能力调整提示词表达，不假定所有模型都支持同一参数字段。
- 用 `scripts/lint_prompt.py` 扫描部分客观硬伤，用回归测试检查改动是否破坏既有用例。

**边界**：本仓库负责提示词与验收建议，不直接生成视频、不代替剪辑后期、不保证跨模型稳定复现。具体模型的功能与限制以对应官方文档和实际返回为准。

## 安装与使用

这是一个供支持 Skill 的 Agent 宿主读取的技能目录，不是独立的 Web 应用。将整个目录放到宿主约定的技能目录，按 `SKILL.md` 开始执行；结构维护见 `STRUCTURE.md`，能力与缺口见 `ROADMAP.md`。

只需要 Python 标准库即可运行客观检查：

```bash
python scripts/lint_prompt.py tests/cases/crime_confront.txt
python scripts/run_regression.py
```

`lint_prompt.py` 只检查有限规则，不等于审美评价或生成成功证明。视频生成、素材获取与成片验收由使用者的工具链负责。

## 体系化知识库如何接入

本 Skill 与公开的 [影像创作专业知识库](https://github.com/HK-37/image-video-creation-knowledge) 深度结合。知识库采用 **CC BY 4.0**，代码与知识数据分仓库、分许可维护。

**仅克隆 Skill 不会自动获得知识库。** 普通 Git 克隆只下载当前仓库；Agent 需要能读取知识库的 Markdown 文件，才能启用知识增强。推荐使用两个独立目录：

```text
your-workspace/
├── skills/video-prompt-optimizer/       # 本仓库
└── knowledge/image-video-creation/      # 公开知识库，建议 v1.1.0 或更新明确版本
```

在知识库目录执行：

```bash
git clone --branch v1.1.0 --depth 1 https://github.com/HK-37/image-video-creation-knowledge.git .
```

Agent 宿主将 `knowledge/image-video-creation/` 登记为创作知识源，先读取 `kb/MOC-index.md`，再按任务加载相关条目。也可将公开知识库作为项目子模块或数据依赖，但那需要另行执行初始化／更新，不是默认自动下载。

未配置知识库时仍可使用公开参考文件，但必须明确提示：**当前未启用体系化知识增强，不代表本 Skill 的完整知识驱动状态。** 具体协议、版本与许可要求见 [docs/knowledge-source.md](docs/knowledge-source.md)。

## 结构

```text
video-prompt-optimizer/
├── SKILL.md                 # 执行入口：意图登记、转写流程与交付约束
├── STRUCTURE.md             # 知识归档规则与维护边界
├── ROADMAP.md               # 当前能力、缺口与开发状态
├── references/              # 方法论、词料、风格包与参考模板
├── scripts/                 # 客观扫描与回归工具，仅标准库
├── tests/                   # 正反面用例及回归基线
└── docs/                    # 知识源配置与发布边界
```

## 测试

```bash
python scripts/run_regression.py
```

修改规则或扫描器后必须重跑。测试通过只证明机械检查与基线未回归，不证明任意模型的画面效果。真实生成对照须记录输入、模型与版本、输出、失败类别及成本。

## 素材与许可

不上传私人素材、未公开项目数据、凭据、私有路径或无权分发的第三方图片、视频、论文全文。单案例经验必须标明适用范围，不得写成行业统一公式。

本项目自有代码与文档采用 [MIT](LICENSE) © 2026 HK-37。公开 URL 指向的外部资料保留其原权利；MIT 许可证不重新授权这些第三方内容。
