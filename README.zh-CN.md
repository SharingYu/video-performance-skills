# Video Performance Skills

**从视频、小说或原创点子出发，把故事、表演和制作衔接起来。**

[English](README.md) · [三条路线](docs/THREE-ROUTES.md) · [统一入口](skills/video-creation/SKILL.md) · [调用示例](examples/three-routes/README.md)

面向 AI 视频创作者的技能包：一个总入口，视频观察和表演导演两个专业模块，以及来源、长文本和进度工具。由现有助手完成创作与观察，本地工具不调用模型 API。

## 三个方向

| 输入 | 工作路线 |
| --- | --- |
| 视频链接或文件 | 取得真实视频→观察故事与互动→保住亮点→按要求复刻或换角色 |
| 小说 | 分段回读→原著事实与人物账本→改编取舍→分集→剧本→制作交接 |
| 原创想法或参考视频 | 比较机制→角色选择与后果→剧本→表演亮点与分镜 |

三条路线共享来源、角色与剧情状态、制作交接和审查，不要求每次从头跑全流程。[完整路线](docs/THREE-ROUTES.md) · [现有能力与缺口](docs/CAPABILITIES.md)。

## 它解决什么问题

一只猫想偷点心，发现同伴盯着自己的爪子，停住，顺势假装认真摆正餐垫。

只拍到“伸爪”和“餐垫摆好了”，动作结果虽然齐全，笑点却可能丢掉。真正需要保住的是：**发现被看见 → 停住 → 过于认真地掩饰**，以及同伴的回应和自己的余韵。

这套方法把这些过程写成可见、可检查的要求，而非只写“可爱”“尴尬”或“电影感”。以上为原创虚构的文字示例，并非实测生成视频。[查看完整案例](examples/reference/output.md)。

## 安装

准备 [Node.js 22.20+](https://github.com/vercel-labs/skills)，在项目目录运行：

```bash
npx skills add SharingYu/video-performance-skills --skill video-creation performance-direction video-observation
```

按提示选择使用的 AI 助手，也可指定：

```bash
npx skills add SharingYu/video-performance-skills --skill video-creation performance-direction video-observation --agent codex
npx skills add SharingYu/video-performance-skills --skill video-creation performance-direction video-observation --agent claude-code
```

没有 Node.js 也可下载 ZIP，手动复制技能目录。观察脚本还需在独立 Python 环境安装依赖，不安装视频模型。[安装说明与 Claude Code 插件用法](docs/INSTALL.md)。

## 怎么用

直接用中文向助手提出任务。视频需能被当前助手读取；也可以先提供具体观察记录。

统一从 **video-creation** 开始：“复刻这个视频，角色换成……”“把这本小说改成红果向漫剧”“根据这个点子原创，或在参考基础上重新改编”。它会选对应路线，只调用当前需要的专业模块。[三路线示例](examples/three-routes/README.md)。

**先读懂本地视频**

```text
用 video-observation 读这个本地视频。先覆盖每个镜头，含糊的互动再回看。
重点记大致看向谁、身体做了什么、搭档怎样回应和先后顺序。
实际打开返回图片后再记观察，然后交给 performance-direction 提取必保亮点。
```

支持逐镜概览、指定时段连续图、保留全景对应的局部放大和观察记录。标准是正常观看能读懂的动作与互动。[本地视频使用示例](examples/observation/README.md)。

**复刻精髓**

```text
用 performance-direction 拆解这个参考：找出真正有趣的眼神、姿态、
动作和反应，区分观察事实与导演解释。做一张表演事件卡，标出必保过程，
允许换场景和机位。先不生成视频。
```

**原创笑点**

```text
用 performance-direction 为两位成年图书馆工作人员设计无对白的暖喜剧。
Alex 想表现得专业，容易用力过猛；Robin 会安静地帮他留面子。
两人正在布置图书展台。提出三个机制不同的亮点，比较后选一个展开表演事件卡。
```

**审查已有片段**

```text
用 performance-direction 对照事件卡审这个候选。分别判断动作过程、
邻镜连续、亮点兑现和节奏。指出细节已看见、明确缺失还是证据不足，
不能因为首尾状态正确就认定中间表演成立。
```

它会按你的任务范围工作，不要求每次都从头跑完整流程。技能主体以英文维护，输出语言遵循用户要求。

## 包里有什么

- 参考精髓拆解、原创亮点设计两个入口。
- 三路线总入口，以及共享的来源、人物状态、分集承接和制作交接。
- 长文本分块回读、内容哈希、进度与产物版本；工具返回正文不等于小说分析已完成。
- 本地视频观察工具：逐镜查看、按疑问回查和放大；导出图片不会自动记成“看过”。
- 六组共用事件卡：观众期待与回报、可见表演链、必保细节、注意力交接、可变条件、证据或原创意图。
- 分镜与审片交接：把必保细节关联镜头职责、实际采用区间和返修原因。
- 技术、动作、连续性、亮点、节奏分别验收；看不见的过程保留“待核”。
- 猫和成年人的原创虚构文字案例，以及十项边界验收材料。

可供 H3、其他视频模型、动画或真人拍摄流程参考，视频执行后端独立接入。[完整工作流](docs/WORKFLOW.md)。

## 验证范围

v0.3 增加三路线总入口和项目来源工具。文本测试验证原文字节、Unicode分块、改文失效、续读与产物历史；媒体测试用临时测试片验证时间对应、裁切和观察记账。文字案例不是视频质量分数。

助手需要实际接收并查看图片，工具成功不等于理解正确。静帧序列可支持可见动作与先后关系，实时节奏和听感需另行观察。当前没有测得成片质量提升比例、观众笑感或爆款概率。[验证说明](docs/VALIDATION.md)。

小说分析、改编与脚本方法已可使用。整季对白漫剧还需要实际画面、稳定音色、口型、字幕与剪辑验证，平台发布另行接入；不能把本机H3短片经验当成整季自动上线已验证。[能力边界](docs/CAPABILITIES.md)。

欢迎提交可复现的反例、自有素材案例、翻译和有明确作用的工具适配。[贡献指南](CONTRIBUTING.md) · [后续方向](docs/ROADMAP.md)。

由 [SharingYu](https://github.com/SharingYu) 维护。[来源、固定版本与采用范围](docs/ATTRIBUTION.md)。本仓库发布的贡献采用 [MIT](LICENSE)；外链资料按原作者条款使用，未打包其完整技能库、手册或教学视频。
