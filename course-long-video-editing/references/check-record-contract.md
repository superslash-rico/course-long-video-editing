# 检查脚本的规范化记录

所有脚本只读输入/生成工作区报告，不直接改ChatCut、启动转写、上传、发消息或改账户。当前工具schema由接收方实时读取；助手把原生返回值整理为以下记录，不把本机私有RPC桥、旧UUID或某版内部数据库当便携API。原始回执留本课，分享只带通用结构。

## 命令

```sh
python3 scripts/course_checks.py plan plan.json
python3 scripts/course_checks.py materials materials.json
python3 scripts/course_checks.py mapping mapping.json
python3 scripts/course_checks.py captions captions.json
python3 scripts/course_checks.py protection before.json --after after.json --changes changes.json
python3 scripts/course_checks.py bindings binding.json
python3 scripts/course_checks.py quotes quotes.json
```

退出0表示该项结构检查通过，2表示失败；可选工具脚本3表示未运行，不能解释为通过。输入文件位于本课工作目录；上面的文件名不是要求用户提供的新表单。

## 核心结构

- **plan**：`paragraphs:[{id}]`与`decisions:[{paragraphId,treatment,reason}]`覆盖全文。treatment为animation/quote/screen/presenter/transition。`scenes`每项记录id、timelineSeconds、mode（full-frame/local/transparent）、understandingGoal、visibleChange、wholeDesign及shots的at/until（场景局部秒）。`quotes`用实际timelineSeconds判断冲突；semanticCandidateSeconds只是分析上下文，不用于盲删。
- **materials**：每项id/source/identity/boundary/state。identity区分real-page、real-photo、source-video与自制/生成illustration；state区分collected、imported-reference、used、unavailable。used必须有productionFile和usedIn。截图原件、生产裁切、事实/权限审核由来源记录补全。
- **mapping**：`{sourceSeconds:[a,b],timelineSeconds:[c,d],rate:1}`，只表示恒速段。不要把微秒直接放进seconds；复杂变速保留原生源映射或逐帧映射，不强行伪装恒速。
- **captions**：cards每项id/text/seconds，totalCount、paginationComplete、visibleCaptionTrackCount。逐页收全且去重，期望唯一确认主字幕。样式以继承后的有效值另记，不只比单个轨道字段。
- **protection**：before/after各含canvas、durationSeconds、sourceTranscriptHash、captionCards、items。items以助手显式映射的稳定key识别（可从旧条目映射到新时间线），kind区分voice、presenter-copy、sfx等，包含实际源区间、时轴区间、速率、增益、淡化/静音和相关有效属性。省略无关UI排序/缓存等序列化细节，但不能省略真实媒体状态。changes列allowedAddedItems、allowedDeletedItems和expectedChanges（每项明确新的字段值）；expectedTopLevel仅用于已授权上游变更。overlay/subtitle阶段即使在changes中写了声音改变也会拒绝；粗剪/混音阶段按用户授权范围另记stage与完整差异理由。
- **bindings**：properties为当前原生key/defaultValue数组，overrides为实际已保存覆盖或null，expected为期望有效值。按合并后比较，保留false、0和空文本。未知覆盖需查当前schema；给原生发送`{}`通常是空补丁，恢复应显式写回目标值后回读。
- **quotes**：`quotes:[{id,values:{text,cues,seconds},durationSeconds}]`。以当前JS字符串UTF-16半开区间覆盖每行；不把示例cues视为新句真实时间。

规范化示例见[fixtures](../validation/fixtures/)。这些是合成测试记录，不能作为新课已读全文或已核实事实的证据。

## 真实词级时间生成

```sh
python3 scripts/build_quote_cues.py --transcript source.json --requests chosen-quotes.json --time-unit us --output final-quotes-v1.json
```

明确选择seconds/ms/us。支持tokens或utterances[].tokens，使用start/end/text，跳过显式hidden/deleted/silence及原生静音占位。requests为数组，每项id/sourceSeconds/rows，row有display和actual anchor（字段名anchor）。锚点必须在窗口内唯一；缺失、歧义、跨行重叠或退场余量不足则失败，不猜时间。生成文件保留实际原话与精简文案关系；核对原声和画面后再导入。

## 实际媒体与声音

`inspect_media.py file --decode --width 1920 --height 1080 --fps 30 --transfer bt709`检查真实导出，依当前发现的ffprobe/ffmpeg；可用--ffprobe/--ffmpeg指明路径，不打包开发机工具路径。编码/色彩与请求不同需查当前导出profile后重导，不能只信按钮或提交成功。

`measure_sound.py sfx.wav --voice speech.mp4 --voice-start 30 --voice-duration 1.2`给出48kHz双声道sample peak、active RMS及可调初始增益建议；不修改原声，不把它当LUFS/真峰值或听审。原声已有过零峰值时按基线区分，实际混音另测。AAC等有损输出不应强求逐样本等于线性PCM相加；输出fps可能带来小于一输出帧的时间量化，需实测当前版本，不能全局补偿固定16.7ms。


实际实例时长可用`python3 scripts/bind_instance.py --defaults copied/defaults.json --duration-frames 480 --fps 60 --output instance-values.json`生成。输出propertyOverrides用于当前实例，seconds为8；不自动压缩旧相机/词级节奏。短于旧cameraJSON的区间要求重新编排。圆窗的正数预览回退只服务未绑定验证，生产仍显式绑定。

sourceAudioEnabled等规范化字段是检查语义，并非保证可写的原生字段。当前Desktop画面与声音是独立条目，有声视频新加可能同时产生关联音频；先读返回和inspect_item，再针对音频ID静音/移除，并禁用副本派生字幕。不要把整份回读对象直接当写请求。


画面条目的sourceAudioEnabled=false只说明它本身没有嵌入音轨，仍可能有已创建的关联音频条目。新圆窗副本的规范化记录必须包含linkedAudibleAudioKeys，已核实无可听关联声才填空数组；未检查不填空。保护器拒绝overlay/subtitle阶段新增voice。结合实际audioItems、links、静音/增益与完整字幕轨核对，不能凭单个布尔值断言没有双声。
