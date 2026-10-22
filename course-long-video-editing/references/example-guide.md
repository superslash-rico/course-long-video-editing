# 如何使用参考资源：固定风格与局部工艺分开

课程资料另有[品牌PDF模板预览](../assets/templates/course-companion/template-preview.pdf)，它仅说明学员资料的阅读版式，不是专业动画样片或真实新课成品。

**目前没有按最新“整体构图与镜头设计工作法”制作并通过用户审核的完整专业动画样片。** 新方法已成文，尚未实施验证；早期阶段的认可不能写成最终整体质量达标。制作须以[完整工作法](whole-first-design-and-camera.md)及当前用户要求为准。

## 1. reference-previews：已确定的名签与金句视觉

这个目录只保留已确定的固定包装方向，不放专业动画整体验收样片。

- 名签：[原生显示](../assets/reference-previews/identity-slash-native.jpg)、[9秒静音预览](../assets/reference-previews/identity-slash-silent.mp4)、[可编辑组件](../assets/templates/identity-slash/resource.json)。学习透明斜杠、字级和进退场，按当前讲师填真实姓名与身份。静音是刻意移除未经核实可再分发的旧库音轨，正式新片仍配合适入场声。
- 金句：[原生定格](../assets/reference-previews/quote-hybrid-native.jpg)、[9帧时序图](../assets/reference-previews/quote-hybrid-motion.jpg)、[可编辑组件](../assets/templates/quote-highlight-follow/resource.json)。保留 C+B+D、半透明背景及仅入场音效的固定方向。新文字、换行、口播和构图需重算 cues 并原生检查；本目录没有金句连续 MP4。
- [视频元数据](../assets/reference-previews/preview-metadata.json)只描述名签预览，不代表所有新实例已验证。

## 2. craft-studies：项目记录仅供局部工艺研究

- [历史局部工艺视频，约26.7秒](../assets/craft-studies/project-record/project-record-partial-craft.mp4)
- [原生定格](../assets/craft-studies/project-record/project-record-native.jpg)、[12帧时序图](../assets/craft-studies/project-record/project-record-chronology.jpg)
- [视频范围说明](../assets/craft-studies/project-record/preview-metadata.json)、[时序范围说明](../assets/craft-studies/project-record/chronology-metadata.json)
- [衍生源码入口](../assets/examples/project-record/src/ExplodedRecordPurple.tsx)、[默认值](../assets/examples/project-record/defaults.json)、[属性](../assets/examples/project-record/properties.json)、[用途限制](../assets/examples/project-record/resource.json)

这段曾被用户评价为早期课程中较好的动画；最新反馈明确整体设计目标尚未达到。现在仅研究其中的纸面厚度/阴影/透视、对象拆解与归位、身份连续及部分运动实现，**不得把它的整体构图当作当前标准，不能照搬布局、相机路径或直接改字投产**。

先按新方法独立设计本段开场、过程和结果全景，再决定哪些局部组件可用。便携源保留相对依赖和 Apache 许可，字体用随包原版 MiSans；`labelsJSON`只控制 key/t/body，`clockJSON`及`cameraPlan.ts`仍为旧例编舞，按新口播重设计。约24.7秒的源编舞不能直接当26.7秒完整预览的通用时轴。

MG 源只画图形，人像/原声/字幕/SFX为独立合成层。新片重新绑定自己的素材，并按[运行时指南](runtime-and-binding.md)核对真实映射。素材存在、代码能运行与最终审美达标分别验证。

## 3. 已移出的历史探索

用户最新明确指出 FDE 询盘交接画面不符合新的整体标准。其视频、全景图、时序图及旧研究源码已归档到作者项目的技能包外，不进入本技能，也不作为正向样例或默认模板。其他被退回的 P1 板面、大窗小窗、逻辑连线、复杂背景及未获最终整体认可的批量改稿同样不作为当前成功样例。

后续只有实际按新方法制作并通过用户审核的完整样片，才能作为“新标准达标成片”加入；记录对应源码、构图/镜头方案、当前合成、审核范围和版本。当前不得为了填满示例库而以旧成片代替。

## 4. 播放、声音与资源边界

项目记录研究视频与名签预览保持原 HEVC/HLG；播放器色彩处理可能影响外观，原生图供对照，时序图仅辅助看动作顺序，不替代连续观看、听审或最终验色。项目记录含原课程合成声音，只供学习，不提取人像/声音当新课素材。名签预览静音，金句没有连续视频。

[声音配方](../assets/audio/generate_candidates.py)提供原创候选，尚未获用户固定音色认可。上游代码、MiSans与视听资源各自边界见[第三方说明](../THIRD_PARTY_NOTICES.md)。
