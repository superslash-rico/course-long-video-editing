---
name: course-long-video-editing
description: 剪辑课程长视频、人像口播课和录屏教学课，或续作指定环节。先建课程目录，按需粗剪、校对字幕、采集真实材料；动画先看随包样片，再做当前原声合成对照，来源说明固定左下角。沿用用户片头片尾和封面，动画审核后整理课程简介及品牌学员PDF。
---

# 课程长视频剪辑

先识别本次阶段，只加载对应资料。复用已确认的标题、粗剪状态、风格和授权，主动完成可审核产物；不把内部参数表转交用户填写。

## 每次启动与续作

1. 读取本技能实际目录的`PACKAGE.json`、本课`课程项目.json`/创作日志及当前原生工程。使用下面的阶段入口生成本轮版本记录；不从聊天记忆或工作区旧备份猜当前规则。技能维护任务不据此新建课程。
2. 新课标题未知时先问标题；已确认直接复用。按[建档规则](references/project-start-and-file-management.md)建立`YYYYMMDD-课程标题/`及原片、片头、片尾、封面、参考资料五类目录，归类复制并核验已供文件。续作跨日沿用本课目录。
3. 只做本次授权阶段。粗剪状态未知必须确认；已粗剪则不再剪声、压停顿或重排内容。字幕/动画阶段保护原声、正文时序和已定字幕。当前用户指令优先于历史样例。
4. 片头、片尾、封面沿用用户原件；只做首尾衔接，不自动设计替代品或新增章节片。缺件记录到具体项，继续独立工作。新课创建独立工程，续作读正确工程；不沿用样片UUID或旧时间码。
5. 人像口播按内容设计较多解释动画；录屏以清楚可跟做的真实操作为主，概念段才加专业动画。只有真实人像输入才做同步圆窗，核查关联音频与重复字幕。详见[录屏路径](references/screen-tutorial.md)。

## 按阶段读取

先运行`python3 "本技能目录/scripts/workflow_gate.py" prepare --stage 阶段 --output "本课/工作文件/阶段记录-新版本"`。由助手填实际路径/阶段；已有输出不覆盖。动画阶段加`--profile evidence|concept|exercise|mixed`，按当前内容选择，不询问用户填参数。返回的`requiredReading`才是本轮必读集合，其他资料按需要检索。

| 阶段 | `--stage` | 必读与分支 |
|---|---|---|
| 接收/粗剪 | intake | [接收与粗剪](references/intake-and-rough-cut.md)；首次建课再读建档规则 |
| 首尾衔接 | packaging | [用户首尾与两处转场](references/branding-intro-outro-transitions.md) |
| 字幕 | subtitles | [字幕](references/subtitles.md)；保留灰底#6B6B6B/80%、直角、无描边阴影、行高1.3，按实际画幅核对 |
| 真实材料 | materials | [调研与截图](references/material-research-and-capture.md)；已有审批与材料时核对台账，不重新搜集凑数量 |
| 专业动画 | animation | [动画执行](references/animation-production.md) → [整体与镜头完整方法](references/whole-first-design-and-camera.md) → [样片导览](references/example-guide.md) → [原生绑定](references/runtime-and-binding.md)；真实材料再读[原件批注](references/source-annotation-and-camera-acceptance.md) |
| 名签/金句 | emphasis | [名签与金句](references/identity-and-quotes.md)；按真实词级时间/当前底色适配，不冒充专业解释动画 |
| 审核/交付 | review | [品质与交接](references/quality-and-handoff.md)；用户通过动画后才进入[课程简介与资料](references/course-companion.md)；封面按[原件交接](references/covers.md) |
| 技能迭代 | maintenance | [维护与防回退](references/learning-and-skill-maintenance.md) |

只有换机/环境故障才读[环境与跨机](references/environment-and-portability.md)，只有问题排查才读[失败模式](references/failure-patterns.md)。缺原片/转写/连接时用[部分输入分支](references/partial-inputs-and-design-previews.md)，明确准备稿与实际原生合成的差别。完整制作按[20项检查](references/production-checkpoints.md)检查适用项，不一次加载所有参考文档。

## 动画必须落实的质量基线

- **先看真实动态样片，再制作。** 按[样片导览](references/example-guide.md)播放匹配案例、查看全景/细节抵达/停留末端/返回四帧，写出本段要继承的机制。`prepare`只生成路径和版本锁，不证明看过。旧中性组件示范只用于技术启动。
- **来源在原件里读。** 网页、报告、招聘中的事实默认直接圈框、高亮、划线，保留日期、单位、范围、否定和优先/验证等限定，标记与原件共享坐标。覆盖讲解、回顾、练习等所有引用实例；不将原文另抄成主要证据卡。抽象方法与明确自制示意仍可独立图解。 来源说明条统一固定在屏幕左下角、用安静小字呈现，避开字幕与人像；使用SourceCredit，保持屏幕坐标，不进入运镜世界。
- **镜头真实作用于前景。** 全景到特写有明显尺度反差，推近后主要阅读单位尽量大且完整；结合透视、厚度、遮挡和视差，有目的地推拉/摇移，阅读时持续慢推。背景始终在主体后，配角退让时纸面保持实心。
- **先做代表段，再批量。** 用本课素材与语音锚点设计，原生导入/保存回读，导出当前代表段；用`workflow_gate.py compare`与匹配样片组成四状态对照，实际查看并修复后再扩展。既有整批授权继续有效，不新增逐镜头用户审批。
- **交审核前遍历全课。** 每段都有明确理解任务；所有真实材料引用均复查原位批注，包含末尾与练习。检查入退场邻帧、最大运动、字形/遮挡、实时圆窗、动作声与普通字幕。用当前源、实例、参数和导出建立同版证据，`workflow_gate.py check`只检查证据完整性，不能代替观看/听审。

样片用于学习质量和机制，不直接插入新课，不继承案例事实、数量、旧编舞或时间码。保持原声与自然教学节奏，不擅自配音、改身份或加BGM；声音按[动作与混音](references/sound-design-and-cues.md)验收。AI生图只补充明确示意，不能生成假证据。

## 交接与迭代

本课保存源、版本锁、参考观察、场景清单、原生回读、实际对照和当前审核片。动画自查后交带真实讲话、普通字幕和前后余量的审核片；用户确认当前版本后，才进行正式成片、课程资料定稿和最终交接。已确认不重复询问，沉默不视为批准。

每次迭代更新对应的唯一规则、适用样片/配方和真实失败测试，检查旧表述冲突；保留完整镜头方法、字幕/原声保护及授权边界。新版先做隔离试跑和迁移验证，再备份安装。本机迭代、可分享包、GitHub发布和下一课实际审美分别记录，不以文档或脚本全绿宣称从此不会退步。
