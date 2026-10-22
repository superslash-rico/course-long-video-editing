# 课程长视频剪辑 Skill

在本地 ChatCut 剪辑人像口播或软件录屏课程：先确认课程标题、建立一课一目录并归类素材，再按需粗剪、校对字幕，准备真实素材并制作教学动画，衔接用户提供的片头片尾，最后整理上传标题、简介和品牌学员资料 PDF。

当前版本：**v1.3.0 · 同事试用版**。完整技能与字体、参考资源、可编辑组件、课程资料模板共 96 个文件。

**专业动画的最终整体目标尚未达到；完整的整体构图与镜头设计方法已成文，仍待新课程实际制作验证。目前没有符合新标准的完整专业动画样片。** 名签/金句固定视觉保留；项目记录只供局部工艺研究。新增 PDF 预览是资料排版模板说明，不是实际课程成品或动画品质样片。

## 下载与安装

- [v1.3.0 完整技能包与 SHA256](https://github.com/superslash-rico/course-long-video-editing/releases/tag/v1.3.0)
- [直接下载完整 ZIP](https://github.com/superslash-rico/course-long-video-editing/releases/download/v1.3.0/course-long-video-editing-v1.3.0.zip)
- [SHA256 校验文件](https://github.com/superslash-rico/course-long-video-editing/releases/download/v1.3.0/course-long-video-editing-v1.3.0.sha256)
- 或使用 **Code → Download ZIP**。先读[开始使用](course-long-video-editing/开始使用.md)，安装内层完整的 `course-long-video-editing/`，不要只复制 `SKILL.md`。

```sh
git clone https://github.com/superslash-rico/course-long-video-editing.git
cd course-long-video-editing
python3 course-long-video-editing/scripts/verify_package.py
python3 course-long-video-editing/scripts/check_environment.py --package-only
python3 course-long-video-editing/scripts/install_skill.py --dry-run
python3 course-long-video-editing/scripts/install_skill.py
```

Windows 可将 `python3` 换为 `py -3`。安装器只新增完整技能或确认已有同版；已有其他版本时先备份并核对个人修改，按[本机维护工作流](course-long-video-editing/references/learning-and-skill-maintenance.md)升级，不强制覆盖。安装后在新任务中确认技能被发现。

接收电脑需要自己的 ChatCut Desktop、当前可用的本地 Agent 集成和课程原片。截图/浏览器控制、AI 生图或外部资料服务按本机实际能力使用，不依赖原作者账户。Python 检查器只辅助文件核对；随包 PDF 生成器另需 ReportLab/Pillow，也可用当前可用的等价 PDF 制作工具。连接、字体和真实渲染要在接收电脑验证。

MiSans 原版四字重和完整许可位于[字体目录](course-long-video-editing/assets/fonts/)。视频端按[字体说明](course-long-video-editing/assets/fonts/acquisition.md)注册并核对实际字形；安装技能不会自动安装系统字体。PDF 模板可以直接嵌入随包字体。

## 当前制作流程

实际课程剪辑意图 → 确认本课标题 → 建立日期标题目录并归类已供素材 → 判断人像/录屏与确认粗剪状态 → 按需自然教学粗剪 → 两处首尾转场 → 字幕校对 → 真实素材调研/截图 → 专业动画与未覆盖重点句 → 上传标题/简介和学员 PDF → 整片核查与本机复盘。

只说“我想剪辑一个课程长视频”也可启动。标题未知时，Agent 首先询问“这次想剪辑的课程标题是什么？”；已明确给出当前标题则直接复用，不从旧课或文件名擅自推定。收到标题后，在实际项目工作区创建：

```text
YYYYMMDD-课程标题/
├── 原片/
├── 片头/
├── 片尾/
├── 封面/
├── 参考资料/
├── 课程项目.json
└── 创作日志.md
```

日期取用户/客户端当地的建项目日期。尚未给素材就提示实际目录路径；已经给出素材时，Agent 按用途复制、核验并记录来源/目标/摘要，保留原件，同名不同内容另存。完成建档和已供素材归类后再开始剪辑。后续按需增加 `工作文件/`、`预览/`、`交付/`；字幕、动画源码、来源记录、审核片、成片和 PDF 都跟随本课。跨日续作复用原目录，最终上传标题另存，不自动改目录名。只讨论或更新 Skill 不创建课程占位目录。

每课建立独立 ChatCut 工程。应用受管工程包若无法选择存放位置，记录工程与课程目录的映射，不搬动应用数据库。可选标准库助手和归档格式详见[课程建档与资料管理](course-long-video-editing/references/project-start-and-file-management.md)。

- **片头、片尾和封面由用户提供。** 包装仅做片头到正文、正文到片尾两处转场，不自动设计选样、制作封面或插入章节包装。缺素材记待补并继续独立工序。
- **粗剪状态未知先问。** 已粗剪直接校对字幕；需要粗剪时按自然教学去明确口误/失败重录、缩短无意义长空白，保留原意、教学停顿和软件操作链。
- **人像与录屏分流。** 人像可更多使用精心设计的解释动画；录屏保留真实操作为主体，仅在概念和必要重点上加动画。
- **先理解与找素材，再做动画。** 从校对字幕和可选用户材料形成视觉需求，主动检索一手来源、实际采集页面/报告/软件界面，记录原件、派生图、出处和用途；必要时用生成插画补充，明确示意与真实证据的边界。
- **整体设计与镜头细节完整保留。** 每段先设计开场/过程/结果全景，再精修模块和镜头；专业动画覆盖确定后再安排固定金句。金句仅入场声音，无退场叮声。
- **剪辑后交课程资料。** 根据最终视频写一个可直接上传的标题和短简介，整理适用的思维导图、材料与真实来源链接，输出超级斜杠品牌 PDF、可复制文案和可编辑数据。
- **通用经验自动更新本机，GitHub 发布须确认。** 项目原片、私人截图/来源记录、账号、旧工程 ID 和未达标样例不自动写入全局或公开仓库。

## 给 Agent 的任务示例

```text
使用 $course-long-video-editing，在本地 ChatCut 从零剪辑我提供的课程长视频。
先确认本课标题，建立 YYYYMMDD-课程标题 与五类素材目录，由你整理已给素材，
再识别人像/录屏并确认粗剪状态。沿用我给的片头、片尾和封面，完成两处转场。
校对字幕后，根据课程内容主动检索并截图真实素材，完整执行整体构图与镜头方法，
先专业动画，再做未覆盖的重点句。剪辑定稿后整理课程标题、短简介和品牌学员资料 PDF，
包含适用的思维导图、材料/来源链接，并保留可编辑工程、文案与资料源。
按实际结果记录检查和复盘，本机通用规则可更新，GitHub 发布由我确认。
```

先以真实新视频跑通最小原生闭环，再完成长片。若只要字幕、某个片段或一段样片，在任务中明确范围。素材未提供时不编造课程内容或宣称完成了实际剪辑。

## 文档与资源入口

| 入口 | 用途 |
| --- | --- |
| [SKILL.md](course-long-video-editing/SKILL.md) | 完整流程、范围与必要分支 |
| [课程建档与资料管理](course-long-video-editing/references/project-start-and-file-management.md) / [初始化助手](course-long-video-editing/scripts/init_course_project.py) | 标题优先、一课一目录、已供素材归档、续作与工程映射 |
| [接收与粗剪](course-long-video-editing/references/intake-and-rough-cut.md) / [录屏路径](course-long-video-editing/references/screen-tutorial.md) | 粗剪授权、自然节奏与操作保护 |
| [首尾转场](course-long-video-editing/references/branding-intro-outro-transitions.md) / [用户封面](course-long-video-editing/references/covers.md) | 用户供稿与两处衔接 |
| [字幕](course-long-video-editing/references/subtitles.md) | 中文/英文/术语、语气词、样式及合成检查 |
| [真实素材研究](course-long-video-editing/references/material-research-and-capture.md) / [素材表](course-long-video-editing/assets/records/visual-materials-template.json) | 实际采集、事实与来源、派生文件、真实/生成边界 |
| [动画工艺](course-long-video-editing/references/animation-production.md) / [完整整体构图与镜头方法](course-long-video-editing/references/whole-first-design-and-camera.md) | 全景、模块、镜头、人像、声音、可编辑性与验收 |
| [课程标题/简介与 PDF](course-long-video-editing/references/course-companion.md) | 成片内容驱动的上传文案与学员资料 |
| [品牌模板](course-long-video-editing/assets/templates/course-companion/使用说明.md) / [三页 PDF 预览](course-long-video-editing/assets/templates/course-companion/template-preview.pdf) | A4 阅读版式、JSON、官方 Logo、可移植生成器 |
| [参考用途指南](course-long-video-editing/references/example-guide.md) | 固定风格、历史局部工艺与最终标准的边界 |
| [固定视觉预览](course-long-video-editing/assets/reference-previews/) / [局部工艺研究](course-long-video-editing/assets/craft-studies/) | 名签/金句视觉与历史项目记录；不是完整专业样片库 |
| [组件与模板](course-long-video-editing/assets/templates/) / [圆窗组件](course-long-video-editing/assets/components/) | 可编辑资源，需在当前工程重新绑定和验证 |
| [品牌资源](course-long-video-editing/assets/brand/) / [原版字体](course-long-video-editing/assets/fonts/) | 公开品牌配置、两版原始 Logo、MiSans 四字重和许可 |
| [官方工具参考](course-long-video-editing/references/resource-links.md) / [跨机指南](course-long-video-editing/references/environment-and-portability.md) | 当前能力发现与等价工具选择 |
| [同事试用记录](course-long-video-editing/references/colleague-pilot.md) | 用新电脑、新视频记录真实测试 |
| [逐文件清单](course-long-video-editing/assets/manifest.json) / [验证快照](course-long-video-editing/validation/report.json) | 摘要、权利/用途、已检与未检范围 |

## 验证范围

v1.3.0 完整 96 文件包已核对本机源码、冻结 ZIP 和全局安装一致。新增建档/归档助手完成 17 项真实临时文件系统及资源保护检查，覆盖标题/日期/五类目录、已供文件复制及摘要、冲突另存、续作时原件/日志/状态和待归档记录保护。换到含中文/空格的新目录后，包完整性、安装预演及初始化/复制实际运行通过；57 个既有脚本/创作资源/品牌及 PDF 模板路径、整份整体构图与镜头方法保持原字节。

原 v1.2.0 的资料模板 20 项输出/边界/资源保护检查及三页模板逐页渲染检查按原范围沿用；长内容样例保留 48 个导图子项和 18 条来源说明。当前新增建档测试使用合成文件，没有创建实际用户课程，不代表真实对话自动触发或原生剪辑已验收。

这些证据不代表另一台电脑已完成真实原生剪辑，也不证明专业动画审美、连续听感或学生理解达标。完整整体方法和新流程仍需用真实新课程测试。随包 `validation/report.json` 是打包时的检查快照；本次仓库发布以 Release、提交和 GitHub Actions 状态为准。

GitHub Actions 运行包完整性、相对依赖、字体文件、金句数据、环境静态检查和安装预演；不会操作接收电脑的 ChatCut、安装系统字体或代替成片审核。

## 资源与使用边界

本仓库分享完整工作流及配套资源，不对全部文件统一授予 MIT 等开源许可。各项用途、权利和来源以[资源说明](course-long-video-editing/THIRD_PARTY_NOTICES.md)及[逐文件清单](course-long-video-editing/assets/manifest.json)为准。

- Apache-2.0 衍生代码保留固定上游来源、完整许可与改动说明。
- MiSans 四字重保留原始字节、名称、版权及小米完整协议，作为工作流配套字体，不额外转授字体权利。
- 超级斜杠 Logo 与品牌配置用于本品牌课程资料；未附私人联系方式、二维码、客户正文或公司课程台账，不授予独立商标使用权。
- Rico 人像、讲解及课程成片只供观看研究，不充当其他讲师素材或提取为素材库。第三方裸音效不附带；随包候选 WAV 为原创确定性声音配方。
- 私有 MotionGit 包、Key、登录态、原课程大原片、旧工程数据库、私人过程日志和新课专属截图不在仓库中。

核心工作法不依赖原作者账户；用接收方的实际工具与合法素材制作，再依据真实反馈迭代。
