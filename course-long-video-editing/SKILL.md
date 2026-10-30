---
name: course-long-video-editing
description: 剪辑课程长视频、人像口播课和录屏教学课，或续作指定环节。先建课程目录，按需粗剪、校对字幕、按真实网络素材→精致透明PNG生图→代码逻辑文字准备素材，统一进MG设计空间镜头；动画先看随包样片，再做当前原声合成对照，来源说明固定左下角。沿用用户片头片尾和封面，每课加内容与学习目标说明页；按全画布、点阵视差、真实材料与拟人批注标准制作，审核后整理课程资料。
---

# 课程长视频剪辑

先识别本次阶段，只加载对应资料。复用已确认的标题、粗剪状态、风格和授权，主动完成可审核产物；不把内部参数表转交用户填写。

## 每次启动与续作

1. 读取本技能实际目录的`PACKAGE.json`、本课`课程项目.json`/创作日志及当前原生工程。使用下面的阶段入口生成本轮版本记录；不从聊天记忆或工作区旧备份猜当前规则。技能维护任务不据此新建课程。
2. 新课标题未知时先问标题；已确认直接复用。按[建档规则](references/project-start-and-file-management.md)建立`YYYYMMDD-课程标题/`及原片、片头、片尾、封面、参考资料五类目录，归类复制并核验已供文件。续作跨日沿用本课目录。
3. 只做本次授权阶段。粗剪状态未知必须确认；已粗剪则不再剪声、压停顿或重排内容。字幕/动画阶段保护原声、正文时序和已定字幕。当前用户指令优先于历史样例。
4. 片头、片尾、封面沿用用户原件；片头后每课增加[内容与学习目标说明页](references/lesson-overview.md)，再接正文与片尾；不自动设计替代片头片尾或新增章节片。缺件记录到具体项，继续独立工作。新课创建独立工程，续作读正确工程；不沿用样片UUID或旧时间码。
5. AI人像口播以密集优质解释动画为主体，仅少量短节点全屏人像，其余用随内容动态避让的实时圆窗；录屏以清楚可跟做的真实操作为主，概念段才加专业动画。只有真实人像输入才做同步圆窗，核查关联音频与重复字幕。详见[录屏路径](references/screen-tutorial.md)。

## 按阶段读取

先运行`python3 "本技能目录/scripts/workflow_gate.py" prepare --stage 阶段 --output "本课/工作文件/阶段记录-新版本"`。由助手填实际路径/阶段；已有输出不覆盖。动画阶段加`--profile evidence|concept|exercise|mixed`，按当前内容选择，不询问用户填参数。返回的`requiredReading`才是本轮必读集合，其他资料按需要检索。

| 阶段 | `--stage` | 必读与分支 |
|---|---|---|
| 接收/粗剪 | intake | [接收与粗剪](references/intake-and-rough-cut.md)；首次建课再读建档规则 |
| 首尾衔接 | packaging | [用户首尾与衔接](references/branding-intro-outro-transitions.md)及[每课学习目标页](references/lesson-overview.md) |
| 字幕 | subtitles | [字幕](references/subtitles.md)；保留灰底#6B6B6B/80%、直角、无描边阴影、行高1.3，按实际画幅核对 |
| 真实材料 | materials | [素材三级顺序与采集](references/material-research-and-capture.md)；先真实网络/软件素材，次精致透明PNG，后代码关系文字；已有可用项复用，不凑数量 |
| 专业动画 | animation | [素材三级顺序](references/material-research-and-capture.md) → [动画执行](references/animation-production.md) → [整体与镜头完整方法](references/whole-first-design-and-camera.md) → [样片导览](references/example-guide.md) → [原生绑定](references/runtime-and-binding.md)；真实材料再读[原件批注](references/source-annotation-and-camera-acceptance.md) |
| 名签/金句 | emphasis | [名签与金句](references/identity-and-quotes.md)；按真实词级时间/当前底色适配，不冒充专业解释动画 |
| 审核/交付 | review | [品质与交接](references/quality-and-handoff.md)；用户通过动画后才进入[课程简介与资料](references/course-companion.md)；封面按[原件交接](references/covers.md) |
| 技能迭代 | maintenance | [维护与防回退](references/learning-and-skill-maintenance.md) |

只有换机/环境故障才读[环境与跨机](references/environment-and-portability.md)，只有问题排查才读[失败模式](references/failure-patterns.md)。缺原片/转写/连接时用[部分输入分支](references/partial-inputs-and-design-previews.md)，明确准备稿与实际原生合成的差别。完整制作按[20项检查](references/production-checkpoints.md)检查适用项，不一次加载所有参考文档。

## 动画必须落实的质量基线

制作前读取[课程动画统一标准](references/lesson-visual-standard.md)：全画布无固定挡带、可见点阵视差、真实前景空间镜头、跨段运镜变化、主体Logo、真实材料/自制文件、拟人笔迹及按内容调度圆窗。代表段和整课当前输出均按此检查；不能只更新文档或参数。

- **先材料，后MG。** 逐段实际检索课程相关真实视频、音频、照片与软件功能截图；真实材料不合适或不足时用生图技能补精致透明PNG抠图；代码卡片与文字排在第三位，负责抽象逻辑和关系。代码实现合成、遮罩和相机不属于第三级内容替代。无材料不能直接把整课归为概念图解。按[素材规则](references/material-research-and-capture.md)保存检索实录、实收文件和素材计划，代表段前运行素材关卡。
- **先看真实动态样片，再制作。** 按[样片导览](references/example-guide.md)播放匹配案例、查看全景/细节抵达/停留末端/返回四帧，写出本段要继承的机制。`prepare`只生成路径和版本锁，不证明看过。旧中性组件示范只用于技术启动。
- **来源在原件里读。** 网页、报告、招聘中的事实默认直接圈框、高亮、划线，保留日期、单位、范围、否定和优先/验证等限定，标记与原件共享坐标。覆盖讲解、回顾、练习等所有引用实例；不将原文另抄成主要证据卡。抽象关系在完成素材评估后可独立图解，不能借“概念段”跳过真实素材检索和PNG补充评估。 来源说明条统一固定在屏幕左下角、用安静小字呈现，避开字幕与人像；使用SourceCredit，保持屏幕坐标，不进入运镜世界。
- **镜头真实作用于前景。** 全景到特写有明显尺度反差，推近后主要阅读单位尽量大且完整；结合透视、厚度、遮挡和视差，有目的地推拉/摇移，阅读时持续慢推。背景始终在主体后，配角退让时纸面保持实心。
- **先做代表段，再批量。** 用本课素材与语音锚点设计，原生导入/保存回读，导出当前代表段；用`workflow_gate.py compare`与匹配样片组成四状态对照，实际查看并修复后再扩展。既有整批授权继续有效，不新增逐镜头用户审批。
- **交审核前遍历全课。** 每段都有明确理解任务；所有真实材料引用均复查原位批注，包含末尾与练习。检查入退场邻帧、最大运动、字形/遮挡、实时圆窗、动作声与普通字幕。用当前源、实例、参数和导出建立同版证据，`workflow_gate.py check`只检查证据完整性，不能代替观看/听审。

样片用于学习质量和机制，不直接插入新课，不继承案例事实、数量、旧编舞或时间码。保持原声与自然教学节奏，不擅自配音或改身份；完整制作按本系列默认轻量电子纯音乐配乐，局部字幕/动画任务不据此新增整课音乐；声音按[动作与混音](references/sound-design-and-cues.md)验收。AI生图只补充明确示意，不能生成假证据。

## 交接与迭代

本课保存源、版本锁、参考观察、场景清单、原生回读、实际对照和当前审核片。动画自查后交带真实讲话、普通字幕和前后余量的审核片；用户确认当前版本后，才进行正式成片、课程资料定稿和最终交接。已确认不重复询问，沉默不视为批准。

每次迭代更新对应的唯一规则、适用样片/配方和真实失败测试，检查旧表述冲突；保留完整镜头方法、字幕/原声保护及授权边界。新版先做隔离试跑和迁移验证，再备份安装。本机迭代、可分享包、GitHub发布和下一课实际审美分别记录，不以文档或脚本全绿宣称从此不会退步。
