# v1.4.0 逐项落实与验证

20项均已落实到规则、资源或检查路径；下表分别给本机证据和新课/接收方仍需验证的内容。实施完成不等于20项都获用户成片验收。

| 项 | 已落实 | 本机证据 | 仍需验证 |
| --- | --- | --- | --- |
| 1 输入与续作 | 保留一课一目录、素材分类、原件及续作；新增授权和当前原生目标记录。<br>[project-start-and-file-management.md](../references/project-start-and-file-management.md)、[init_course_project.py](../scripts/init_course_project.py) | 既有17项建档测试保留历史范围；本轮异目录复制/不覆盖通过。 | 接收方真实新课程建档及断点续作。 |
| 2 本地与转写 | 优先本地Desktop，读取实时能力，复用已有转写；云上传按当次授权。<br>[environment-and-portability.md](../references/environment-and-portability.md)、[subtitles.md](../references/subtitles.md) | 本机官方原生连接、独立探针工程与原工程路由分别核实。 | 接收方账号、云转写和当前连接，不复制作者配置。 |
| 3 字幕边界 | 区分源ASR纠错、真实口误、显示精简与剪声权限；按用户确认。<br>[subtitles.md](../references/subtitles.md)、[course_checks.py](../scripts/course_checks.py) | 457条真实字幕全量结构复核，改源/多字幕轨/分页反例通过。 | 新课逐句听校、断行、术语和口误确认。 |
| 4 时序与保护 | 源/正文/成片时间、单位、速率和fps明确；非目标讲话/字幕受保护。<br>[runtime-and-binding.md](../references/runtime-and-binding.md)、[course_checks.py](../scripts/course_checks.py) | 真实课程保护及秒/微秒、变速、重叠、意外改声正反例通过。 | 新课的实际包装/粗剪映射和复杂变速。 |
| 5 全文覆盖 | 按段列理解任务、表现手段和原因；动画后再选剩余金句，保留跟做。<br>[production-checkpoints.md](../references/production-checkpoints.md)、[course_checks.py](../scripts/course_checks.py) | 漏段及实际覆盖冲突反例；宽语义窗口不盲删通过。 | 新课完整内容与动画必要性，由实际理解判断。 |
| 6 真实素材 | 真实截图/操作原件、上下文、生产裁切、导入和实际使用位置逐层记录。<br>[material-research-and-capture.md](../references/material-research-and-capture.md)、[visual-materials-template.json](../assets/records/visual-materials-template.json) | 采集/参考导入/真实使用状态及缺生产绑定反例通过；真实课经验匿名归档。 | 每课重新打开和截取相关材料，版权/隐私与版本核对。 |
| 7 事实与解释 | 日期、主体、条件、否定与真实/生成分层；不以示意图冒充证据。<br>[material-research-and-capture.md](../references/material-research-and-capture.md)、[case-recipes.json](../assets/examples/portable-workflow/case-recipes.json) | 生成示意冒充事实、仅导入当实际使用的结构反例通过。 | 新课事实一手来源和语义审核，不能自动判真。 |
| 8 动态参考与代表样段 | 按动态分析整体/细节/材质/时序，用带原声与人像的实际样段验收新课。<br>[example-guide.md](../references/example-guide.md)、[quality-rubric.md](../references/quality-rubric.md) | 自制46秒原生示范含HTML/Remotion/名签/金句/SFX，12帧查看及完整解码。 | 通用示范无真实讲话；用户整体审美和新课有声代表样段仍需验收。 |
| 9 可见过程与整体 | 全景先成立，再让同一对象经步骤转为结果；避免完成态巡展。<br>[whole-first-design-and-camera.md](../references/whole-first-design-and-camera.md)、[scene.js](../assets/components/course-stage/scene.js) | 24秒同一笔记过程、全景/细节和结果原生导出并抽帧自查。 | 新课逻辑、全景美感、目标学生能否复述。 |
| 10 背景与图层 | 确认的深紫黑、点阵、横向淡紫光实现为HTML/Remotion组件；背景底层，纸面实心。<br>[background.js](../assets/components/course-stage/background.js)、[surface.js](../assets/components/course-stage/surface.js) | 浏览器alpha/遮挡正反例及本机原生整体/配角纸面检查通过。 | 新片所有重叠/反面/极值；接收方GPU和真实字体。 |
| 11 镜头力度与停留 | 全景/特写有强尺度差、快速转镜与可感知读时缩放；机位可编辑。<br>[camera.js](../assets/components/course-stage/camera.js)、[test_camera.mjs](../scripts/test_camera.mjs) | 13项镜头不变量通过；原生示范近景主字放大，改色/4K60片段验证。 | 新课节奏和力度的实际观看，不套固定机位/时长。 |
| 12 阅读单位与大字 | 特写按主要对象/列/步骤取景，完整保留条件、单位与主要文字。<br>[whole-first-design-and-camera.md](../references/whole-first-design-and-camera.md)、[validate_runtime.mjs](../scripts/validate_runtime.mjs) | 3处主要阅读区实际矩形/遮挡检查；修复纸条盖字并通过反例。 | 新增长标题、中英混排、真实截图细节及字幕/人物安全区。 |
| 13 交接与细节 | 同对象交接、旧字退出、邻帧/反字/空场/穿透和最大缩放逐项查。<br>[quality-rubric.md](../references/quality-rubric.md)、[regressions.md](../assets/examples/portable-workflow/regressions.md) | 寻帧顺序无关、读区无遮挡、故意移回错误位置可检出；原生联系表自查。 | 新内容每处交接邻帧和连续观看。 |
| 14 人像与字幕联动 | 处理实时输入，显式绑定实际时长；按人像重设路线，检查关联音频和派生字幕。<br>[effect.html](../assets/components/presenter-circle/effect.html)、[bind_instance.py](../scripts/bind_instance.py) | 原生8秒60fps中6.5秒仍圆窗，首尾当前输入恢复；双声反例通过。 | 真实新讲师裁切/运动、所有安全区；无自动人脸追踪。 |
| 15 声音编排与混音 | 分镜就选动作材质/锚点/音色，阅读留静，跨段查重复；只在名签/金句入场响。<br>[sound-design-and-cues.md](../references/sound-design-and-cues.md)、[measure_sound.py](../scripts/measure_sound.py) | 原创候选配方/示范6事件、音画解码、峰值/静音窗口测量通过。 | 真实原声下贴合、可懂度、重复疲劳与主观试听；候选声未获固定音色认可。 |
| 16 名签与金句排布 | 保留已定视觉，新增版位/暗场参数；等专业动画实际覆盖确定后安排。<br>[identity-and-quotes.md](../references/identity-and-quotes.md)、[identity-slash](../assets/templates/identity-slash/) | 默认无props与修改属性浏览器通过；原生实例和示范有效。 | 新讲师真实身份、运动与字幕避让；不能照搬Rico身份。 |
| 17 真实词级跟读 | 词级唯一锚点、明确单位、静音占位排除、UTF-16全覆盖及退场余量。<br>[build_quote_cues.py](../scripts/build_quote_cues.py)、[validate_quote.py](../scripts/validate_quote.py) | 真实18条金句重建最大差1.91e-13秒；歧义/缺锚/emoji/占位反例通过。 | 每课重新对照真实原声，精简句与锚点关系逐句审核。 |
| 18 原生绑定与还原 | 源/默认+覆盖/实例/当前片一致；保留false/0/空串，试改显式还原。<br>[runtime-and-binding.md](../references/runtime-and-binding.md)、[course_checks.py](../scripts/course_checks.py) | 原生强调色改绿后还原紫；3秒4K60片与1080p对照PSNR36.7dB，实例时长回读通过。 | 接收方当前schema及所选控件；新会话技能发现与应用连接。 |
| 19 输出与全片验收 | 实际编码/色彩/fps/解码、抽帧、原声保护、连续看听和用户认可分别记录。<br>[quality-and-handoff.md](../references/quality-and-handoff.md)、[inspect_media.py](../scripts/inspect_media.py) | 46秒1080p30、3秒4K60、8秒圆窗完整解码与BT.709实查；真实课程结构保护通过。 | 连续全片视听/最终审美、真实新课标题简介与学员PDF内容对照。 |
| 20 共享复用与维护 | 组件/脚本/案例/反例/许可/20项表同步；无私有原片/旧ID，显式备份升级。<br>[learning-and-skill-maintenance.md](../references/learning-and-skill-maintenance.md)、[colleague-pilot.md](../references/colleague-pilot.md) | 官方Skill格式、全包/闭合/秘密扫描及独立目录安装测试按validation报告记录。 | 实体第二台电脑、其他系统/Agent版本和同事独立完成一门真实课程。 |

完整资源定位见[机器可读落实表](20-point-audit.json)，实际测试与历史范围见[验证报告](report.json)。
