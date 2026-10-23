# 可复用组件、导入与新课适配

先读本课实际画面、完整口播和既定设计，再选择组件。用户已确定本系列方向时延续；其他讲师/品牌按其当前规范。组件解决已验证的技术工艺，每段的理解目标、全景、事实、文字、时序与声音仍由助手设计。

## 背景与专业动画舞台

[course-stage](../assets/components/course-stage/resource.json)提供同一套HTML和Remotion模块，入口及全部相对依赖一起复制，不能在全局安装内制作当前视频。

| 文件 | 直接复用的能力 | 新课必须调整 |
| --- | --- | --- |
| `background.js` / `stage.tsx`中的CourseBackground | 深紫黑#0C0A14、可见安静点阵、中部横向淡紫微光、前景相机驱动的弱远景视差 | 与实际前景共用相机状态；不把固定屏幕漂移当镜头联动 |
| `background-only.html` | 独立完整画幅背景，适合放在所有主体之后 | 使用background-properties.json；实际相机尺度/焦点以当前前景为准 |
| `surface.js` / OpaquePaper | 独立前景堆叠、实心纸面、厚度、阴影、内容弱化和表面明度 | 配角退让用tone/contentOpacity；reveal仅用于有意入退场，不把整纸变透明 |
| `camera.js` | 秒驱动短转镜、连续阅读缩放、随机寻帧、相机/物体独立 | 每个主要阅读单位的取景、抵达/停留/离开；示范机位和时刻不是通用剧情 |
| `index.html` / `remotion-example.tsx` | 自制的全景—特写—同对象结果示范 | 新片文字、可见变化、纸面布局及相机，不能只换标题就视为已适配 |

参数以1920×1080设计坐标为示例。背景模块按画幅高度缩放点距/半径；Remotion舞台从当前useVideoConfig取尺寸，HTML组件按自然画布在项目放置缩放。默认整体示范为16:9；9:16、1:1或很长文本需重新设计，未声明为已自动适配。

```sh
python3 scripts/create_scene.py --output "本课/工作文件/动画/新场景" --title "当前场景标题" --kind html
```

路径相对当前工作区，仅作调用示例。助手从已确认课程信息推导路径和内容，不把此命令变成要求用户填写的表单。`--kind remotion`选择TSX示例，`--kind background`选择纯背景。脚本拒绝覆盖已有目录或写入安装包，输出scene-record.json说明下一步。对专业场景，读取并重写shots/content/seconds后再导入；纯背景没有独立自动播放时钟。

原生导入：当前工具读取工程/主线及schema，push_asset指向本课源入口，提交对应properties与实际资产容量；再edit_item放置，使用新返回ID。背景独立作为资产时其轨道在全部主体后。导入后inspect_asset、inspect_item核对有效值，再查实际合成和当前导出。不要重放原作者请求/UUID。

[纯背景原生截图](../assets/examples/portable-workflow/background-native.png)来自搬迁后冷安装副本的实际导出。HTML背景和Remotion的CourseBackground共用已确定参数；新场景继续用实际相机状态驱动弱远景响应。

## 名签、金句、实时圆窗

- [identity-slash](../assets/templates/identity-slash/resource.json)：固定A斜杠名签。Rico课程可延续已确认身份，其他讲师先从真实介绍确认；姓名可有、身份未知则留空。`seconds`等于当前实例时长，可由bind_instance.py生成。默认值支持无props挂载，但不能替代真实参数绑定检查。
- [quote-highlight-follow](../assets/templates/quote-highlight-follow/resource.json)：C大字+B荧光+D跟读与半透明暗场。新增文字区X/Y/宽、行距、未读透明度和暗场中心/半径控制，均为组件自然画布坐标；结合原片移动人像和字幕选位。每条重建真实词级cues，不能用示范节奏冒充口播。完整字形/行首/条件/退场逐句核对。
- [presenter-circle](../assets/components/presenter-circle/resource.json)：处理当前真实输入的圆窗；路线不是人脸自动追踪。正数示范时长只兼容未绑定验证；实际落位由bind_instance.py按帧数/fps显式写入seconds，不依赖隐式宿主时长；长连续动画可共用副本，最后才还原。副本源声音和重复字幕均关闭。媒体sourceIn/rate/时间偏移取当前切段，不从片头重新播。

## 声音

使用[声音编排说明](sound-design-and-cues.md)。随包WAV为原创候选，原生库声音由接收方合法账户检索取得；不会随包提供本课原库裸音效。当前示范中的候选声音不是已获固定音色认可。名签/金句仅入场，专业动作按材质与含义选择，跨段检查重复疲劳。

## 查看与验证

[通用工艺示范](../assets/examples/portable-workflow/preview.mp4)与[实际导出联系表](../assets/examples/portable-workflow/native-contact.jpg)只展示组件、全景/特写、参数与布局，不是真实课程、真实软件运行、科学证据或真实ASR。

Python标准库检查：`python3 scripts/selftest.py`。可选Node/Playwright离线布局与圆窗输入检查：`node scripts/validate_runtime.mjs --output "本课/工作文件/证据/runtime"`；未装可选依赖时标not-run，不自动联网安装。原生导出仍按当前ChatCut执行，浏览器通过不能替代原生通过。具体已测范围见[状态记录](provenance-and-validation.md)。
