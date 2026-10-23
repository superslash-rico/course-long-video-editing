# 课程长视频剪辑 Skill

当前版本 **v1.4.0**，包含完整工作法、可复用动画组件、检查脚本、案例、原版 MiSans 配套字体与许可、品牌学员 PDF 模板，共 **155 个技能文件**。使用本机 ChatCut Desktop 处理人像口播、录屏教学和混合课程。

## 直接安装

在 Codex 对话中把下面这段话交给 Agent：

```text
请使用 skill-installer 安装这个完整的课程长视频剪辑 Skill：
https://github.com/superslash-rico/course-long-video-editing/tree/v1.4.0/course-long-video-editing
请核对完整资源；如已有旧版，先保留本机改动、备份并按随包说明升级。
```

这是固定的 v1.4.0 安装入口。安装后在下一轮或新会话确认技能已加载，再说“我要剪辑一个课程长视频”，提供课程标题、素材位置和粗剪状态即可。Agent 按已知信息继续，不让用户填写分镜或动画参数表。

也可下载 [v1.4.0 完整安装包](https://github.com/superslash-rico/course-long-video-editing/releases/download/v1.4.0/course-long-video-editing-v1.4.0.zip)及 [SHA256](https://github.com/superslash-rico/course-long-video-editing/releases/download/v1.4.0/course-long-video-editing-v1.4.0.sha256)，解压后将完整 `course-long-video-editing/` 目录交给 Agent，按[开始使用](course-long-video-editing/开始使用.md)安装。保留全部相对目录。

开发者也可运行：

```sh
git clone --branch v1.4.0 https://github.com/superslash-rico/course-long-video-editing.git
cd course-long-video-editing
python3 course-long-video-editing/scripts/verify_package.py
python3 course-long-video-editing/scripts/install_skill.py
```

默认安装到当前 Codex 技能根；其他 Agent 可用 `--target-root` 指向其支持的技能目录。Python 只是辅助工具，Windows 可用 `py -3`。已有已识别且未修改的旧版可显式加 `--upgrade --backup-root "备份目录"`；未知或已修改版本会保留，需先检查合并。

## 可复用资源

| 资源 | 能力与入口 |
| --- | --- |
| 确认的动画背景 | 深紫黑 `#0C0A14`、可见简约点阵、中部横向淡紫光；位于全部主体后，随实际镜头弱联动；[组件说明](course-long-video-editing/references/reusable-production-kit.md) |
| 教学动画舞台 | HTML / Remotion 共用背景、实心纸面、厚度阴影和秒驱动镜头；全景—特写强反差、利落转镜、读时缓慢推进 |
| 名牌、金句、实时圆窗 | 可编辑参数、版位控制、真实词级跟读；圆窗按实际时长和当前输入恢复，按新人物重设裁切和路线 |
| 检查器 | 全文覆盖、真实材料状态、时间映射、字幕全量分页、原声保护、有效参数、UTF-16 cues、媒体与声音信号；[检查契约](course-long-video-editing/references/check-record-contract.md) |
| 案例与反例 | [46秒自制原生示范](course-long-video-editing/assets/examples/portable-workflow/preview.mp4)、[重建说明](course-long-video-editing/assets/examples/portable-workflow/rebuild-demo.md)、[挡字等反例](course-long-video-editing/assets/examples/portable-workflow/regressions.md)、[纯背景实测图](course-long-video-editing/assets/examples/portable-workflow/background-native.png) |
| 学员资料 | 原版字体、官方品牌资源、可编辑资料模板和 PDF 生成器；[模板说明](course-long-video-editing/assets/templates/course-companion/使用说明.md) |

新课先复制组件到本课源码目录，再根据实际讲解设计全景、过程、读时、机位、人物和声音。背景及工艺直接复用，示范时间码和布局仅服务示范内容。

## 剪辑流程与使用条件

确认标题 → 建立 `YYYYMMDD-课程标题/`，归类原片/片头/片尾/封面/参考资料 → 按需自然教学粗剪 → 使用用户首尾并制作两处转场 → 校对字幕 → 理解全课、主动采集真实来源与画面 → 教学动画 → 未覆盖内容的名牌/金句 → 整片核查 → 成片标题、简介和品牌学员 PDF → 复盘。

已有粗剪可直接进入字幕；局部任务遵循指定范围。录屏保持真实操作可看清、可跟做。片头片尾及封面由用户提供，不默认新做。事实截图和软件运行结果使用真实材料，生成插画明确标为示意。优先本地 ChatCut Desktop，云转写等外部服务按当次需要与授权，已有转写不重复做。

接收方需要自己的 ChatCut Desktop、可用 Agent 集成和课程素材；从当前工具读取工程、schema、画幅/fps并重新绑定资产，使用自己的合法素材与服务。安装 Skill 不会复制作者账号或注册系统字体；视频端按[字体说明](course-long-video-editing/assets/fonts/acquisition.md)核对实际原生字形。PDF 生成器另需 ReportLab/Pillow 或等价工具。

## 已验证和仍需验证

本机已运行 Python 46 项、镜头 13 项、浏览器 12 项、安装 15 项、包损坏反例 4 项；实际原生 HTML/Remotion 导入、强调色修改与还原、1080p30 / 4K60 导出及完整解码、8秒实时圆窗恢复、独立目录冷安装后背景原生导出均有分项记录。开发所用真实课程另外复核了18条词级金句、457条字幕及非目标源保护。

[20项逐项落实表](course-long-video-editing/validation/20-point-audit.md)说明每项实现、证据和待验证内容；[验证报告](course-long-video-editing/validation/report.json)保留封包时快照。该快照中的 GitHub 发布未做项描述封包时状态，本次发布状态以 [Release](https://github.com/superslash-rico/course-long-video-editing/releases/tag/v1.4.0)、提交和 Actions 为准。

仍需由接收方验证：实体第二台电脑、新会话技能发现与当前原生连接、自己的真实有声样段与完整一课、连续视听与最终审美、学生理解，以及真实课程配套资料内容。其他系统/Agent/ChatCut版本和未测画幅按实际结果记录。通用示范无真实讲师口播，金句节奏为合成输入，未宣称为用户最终审美标杆。

同事首次使用执行[接收验收流程](course-long-video-editing/references/colleague-pilot.md)。GitHub Actions 自动检查完整资源、相对依赖、字体摘要、字幕/保护等正反例、镜头不变量与隔离安装；实际视听与审美在本地完成。

## 资源与维护

全部资源按[来源与使用说明](course-long-video-editing/THIRD_PARTY_NOTICES.md)和[逐文件清单](course-long-video-editing/assets/manifest.json)使用，未对所有文件统一授予 MIT 等许可。Apache 衍生代码、MiSans 原版字体/完整许可、超级斜杠品牌分别保留自身权利边界。

本版分享包采用自制工艺示范，不含当前课程人像/口播、第三方裸音效、私人日志、旧工程 UUID、登录配置或私有 MotionGit 包。原创候选音效附配方，实际音色仍需选择和试听。已公开旧版本保持历史记录，各旧版资源按其当时的说明使用。

通用经验按用户授权维护本机 Skill；向 GitHub 发布按当次明确授权执行。变更见 [CHANGELOG](course-long-video-editing/CHANGELOG.md)，入口见 [SKILL.md](course-long-video-editing/SKILL.md)。
