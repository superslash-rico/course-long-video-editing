# 课程长视频剪辑 Skill

在本地 ChatCut 中剪辑课程、讲解和教学口播长视频，完成字幕校对、讲师介绍卡、专业教学动画与重点句。

当前版本：**v1.0.2 · 首轮试用版**。

**专业动画的最终整体效果尚未达到本项目的目标；新的整体构图与镜头设计工作法已完整成文，但尚未实施验证。目前没有符合新标准的完整专业动画样片。** 名签和金句已确定的固定视觉保留；项目记录资料仅供局部工艺研究。

## 下载与开始

- [下载 v1.0.2 完整技能包及 SHA256](https://github.com/superslash-rico/course-long-video-editing/releases/tag/v1.0.2)
- 或点击 GitHub 的 **Code → Download ZIP**，解压整个仓库。
- 先读 [开始使用.md](course-long-video-editing/开始使用.md)，保留完整的 `course-long-video-editing/` 子目录，不要只复制 `SKILL.md`。

也可以克隆：

```sh
git clone https://github.com/superslash-rico/course-long-video-editing.git
cd course-long-video-editing
```

接收电脑需准备自己的 ChatCut Desktop、当前可用的本地 Agent 集成、账号和真实课程原片。没有 Python 也能按文档安装和使用；下面的 Python 脚本仅辅助检查及复制技能，不替代剪辑工具。

从仓库根目录运行（Windows 可将 `python3` 换为 `py -3`）：

```sh
python3 course-long-video-editing/scripts/verify_package.py
python3 course-long-video-editing/scripts/check_environment.py --package-only
python3 course-long-video-editing/scripts/check_environment.py
python3 course-long-video-editing/scripts/install_skill.py --dry-run
python3 course-long-video-editing/scripts/install_skill.py
```

安装器只新增完整技能或确认已有同版；遇到不同的既有版本会保留并退出，不覆盖个人修改。默认安装到当前用户的 Codex skills 目录，设置 `CODEX_HOME` 时按其目录解析。技能文件安装后，在新任务中确认被发现；ChatCut 连接和实际渲染另外检查。

MiSans 原版 Regular、Medium、Semibold、Bold 及完整许可作为工作流配套资源位于 [assets/fonts](course-long-video-editing/assets/fonts/)。按[字体说明](course-long-video-editing/assets/fonts/acquisition.md)阅读许可、安装和核对真实字形/字重；安装技能不会自动安装系统字体。

## 给 AI 的任务示例

```text
使用 $course-long-video-editing，在本地 ChatCut 从零完成我提供的课程长视频的字幕与动画。
保留原讲解、原声和顺序。完整执行整体构图与镜头设计工作法，先做专业动画，
再处理动画未覆盖内容的金句。素材使用我提供的路径，完成后交可编辑草稿和审核记录。
```

首次先用真实新工程跑通字幕、一段动画、实时圆窗、声音、预览和导出的最小闭环，再完成整片。若只要先做一个样片，在任务里明确范围。

## 内容目录

| 路径 | 内容 |
| --- | --- |
| [SKILL.md](course-long-video-editing/SKILL.md) | 技能入口与两大剪辑环节 |
| [references/subtitles.md](course-long-video-editing/references/subtitles.md) | 字幕纠错、语气词、英文规范与实际画面检查 |
| [references/animation-production.md](course-long-video-editing/references/animation-production.md) | 选段、真实素材、专业动画、镜头、人像与声音 |
| [完整整体构图与镜头工作法](course-long-video-editing/references/whole-first-design-and-camera.md) | 整体先行、模块精修、目的驱动的镜头、逐层检查与版本交接 |
| [references/example-guide.md](course-long-video-editing/references/example-guide.md) | 固定风格、历史局部工艺和最终标准的用途边界 |
| [assets/reference-previews](course-long-video-editing/assets/reference-previews/) | 已确定的名签、金句视觉；不是专业动画最终样片库 |
| [assets/craft-studies](course-long-video-editing/assets/craft-studies/) | 项目记录的局部材质、透视和对象动作研究 |
| [assets/templates](course-long-video-editing/assets/templates/) | 可编辑名签和金句组件 |
| [assets/components](course-long-video-editing/assets/components/) | 实时圆形人像窗参考实现 |
| [assets/fonts](course-long-video-editing/assets/fonts/) | 四字重、完整许可、安装和字体验证说明 |
| [scripts](course-long-video-editing/scripts/) | 完整性、环境、金句 cues 与安装助手 |
| [validation/report.json](course-long-video-editing/validation/report.json) | 已完成的检查及尚未验证的范围 |
| [同事试用记录](course-long-video-editing/references/colleague-pilot.md) | 在新电脑用新视频试做时的记录表 |

专业动画每段独立设计，先做好开场、过程和结果的整体构图，再深入模块和镜头；金句使用固定风格。FDE 旧画面及源码已从当前技能移出，不作为合格整体样例。

## 验证范围

随包检查及 GitHub Actions 验证文件完整性、依赖、数据和脚本可以执行，不证明动画审美达标、字体已在接收机渲染、连续声音合格或观众已经理解。另一台电脑的真实原生制作、最新方法的成片和用户审美验收仍待试用。

两段现有预览使用 HEVC/HLG，播放兼容性和色彩由实际播放器决定；原生截图可供对照。名签视频有意静音；金句只有定格与时序图，没有连续 MP4。

## 资源与许可

本仓库公开分享完整工作流和配套资源，各资源的权利范围分别说明，未对全部文件统一授予 MIT 等开源许可。详见 [THIRD_PARTY_NOTICES.md](course-long-video-editing/THIRD_PARTY_NOTICES.md) 和逐文件[资源清单](course-long-video-editing/assets/manifest.json)。

- Apache-2.0 衍生代码保留上游来源、完整许可和改动说明。
- 本工作流使用 MiSans。原版字体保持原始名称、字节与版权，附小米完整协议；仅作为工作流文字渲染的配套资源，不额外转授字体权利，不拆出作为独立字体库分发。[官方 FAQ](https://hyperos.mi.com/font/zh/faq/)与[许可原文](https://hyperos.mi.com/font-download/MiSans字体知识产权许可协议.pdf)供使用者阅读。
- 课程画面中的 Rico 人像、声音和讲解仅供观看研究，不用作其他讲师的新课素材或提取为素材库。合成视频中的第三方声音不单独再分发；随包候选 WAV 由原创数学配方生成。
- 私有 MotionGit 包、账户 Key、登录态、旧工程数据库、大原片和作者私人过程日志不在仓库中。

技能的核心工作法不依赖原作者账号或私有服务。使用本地工具和真实素材完成作品，再依据实际反馈更新该技能。
