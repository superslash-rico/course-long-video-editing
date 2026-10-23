# 在新工程重建这段工艺示范

这是一条由多项资产组成的46秒示范，不是把gallery.html单独导入即可得到完整视频。gallery.html只负责名签/金句段的背景。完整资源清单见[assembly.json](assembly.json)。

1. 将整个技能保留完整，或先复制相关完整源目录到新的测试工作区；从当前原生工具创建独立16:9测试工程，读取实际fps与轨道ID，不在已有成片上试改项目fps。
2. 依assembly导入HTML、Remotion、示范背景、名签、金句与两种原创候选声音，记录新asset IDs。MG同时提交自然尺寸、properties与容量秒数转换的整数微秒；声音从接收方本地文件导入。
3. 创建base/overlay/sfx三个轨道。由助手写assets-map.json和tracks-map.json，分别以assembly的逻辑key映射到新返回ID；不是要求用户逐项填参数，也不含原作者旧ID。
4. 运行`python3 scripts/build_demo_plan.py --assets assets-map.json --tracks tracks-map.json --fps 60 --output demo-plan.json`，fps使用刚读到的真实值；4K项目可显式给width/height，非16:9会要求重设计。输出只有可审阅放置字段，不会调用编辑器。按当前工具schema校核，再传给原生edit_item并提供当前project/timeline路由。
5. 回读5个图形实例、6个候选声音和实际有效值；Remotion段已提供8秒的新机位，不是把24秒机位硬截。名签6秒、金句8秒及相应cues对应实例。示例cues无真实口播，正式新课需真实词级生成。
6. 检查整体、主要阅读单位、退让纸面、转镜与结果，改一次强调色后导出短段、显式恢复；导出完整示范并核实际编码/色彩/fps，连续试听候选声。与原生联系表对照，只给实际完成的检查状态。

源码/参数可编辑，示范动作时刻仅服务自制内容；新课程重新做理解目标、真实材料、布局、声音和读时。Rico身份仅用于固定名签示例，其他讲师从真实介绍确认，不照搬身份。字体正常注册与实际原生渲染需接收方复核。
