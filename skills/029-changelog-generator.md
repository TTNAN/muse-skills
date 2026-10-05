---
id: "029"
title: "更新日志一键生成"
category: "独立开发"
tags: ["更新日志", "发版", "开源"]
top10: false
---

**痛点**：每次发版写 changelog，全靠翻 commit 记录回忆，漏功能是常事。

**三步做法**：
1. 发版前把 commit 列表丢给 Muse：「按新功能、修复、breaking change 分组，写成用户能看懂的更新日志」。
2. 让它把黑话翻译成人话，「别写 fix null pointer，写清楚什么情况下会闪退」。
3. 存成 CHANGELOG.md，以后每次发版走同一套流程。

**实话**：commit 列表得你亲手丢；存文件和 push 也得你自己来。
