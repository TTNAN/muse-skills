#!/usr/bin/env python3
"""从 skills/*.md 生成 README.md。

用法: python3 scripts/build.py
每条技能一个文件，README 每次全量重新生成，不要手改 README。
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
README_PATH = ROOT / "README.md"

# 作者的 Muse 邀请码（只在 README 文首出现一次，不再每条重复）
INVITE_CODE = "VRPX8E"

CATEGORIES = [
    ("搞钱与副业", "💰", "把 AI 变成印钞机：副业接单、薅羊毛、记账对账"),
    ("金融与投资", "📈", "财报、持仓、汇率、保险：钱的事先看清"),
    ("独立开发", "🛠️", "一个人的开发团队：宣发、文档、用户反馈"),
    ("工作与效率", "💼", "开会、待办、邮件、文档，少加点班"),
    ("生活日常", "🏠", "天天要用的杂事：提醒、证件、快递、家里的事"),
    ("购物与省钱", "🛒", "比价、凑单、盯降价、审订阅"),
    ("内容创作与涨粉", "📣", "做账号、写东西、追热点"),
    ("出行与预订", "✈️", "机票酒店、行程单、签证材料"),
    ("健康与运动", "🏃", "手表数据、睡眠、体检报告翻译"),
    ("文件与云盘", "📁", "找文件、整理照片、合同发票"),
    ("组合技", "🔗", "两个能力串起来，1+1 大于 2"),
    ("实话实说", "💡", "Muse 做不到的事，先说清"),
]


def parse_skill(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError(f"frontmatter 解析失败: {path}")
    fm_raw, body = m.group(1), m.group(2)
    fm: dict = {}
    for line in fm_raw.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip().strip('"').strip("'")
    tags = [t.strip().strip('"').strip("'") for t in fm.get("tags", "[]").strip("[]").split(",") if t.strip()]

    pain = re.search(r"\*\*痛点\*\*：(.+?)(?=\n\*\*三步做法\*\*)", body, re.DOTALL)
    steps = re.findall(r"^[123]\.\s*(.+)$", body, re.MULTILINE)
    shihua = re.search(r"\*\*实话\*\*：(.+)", body, re.DOTALL)

    return {
        "id": fm.get("id", ""),
        "title": fm.get("title", ""),
        "category": fm.get("category", ""),
        "tags": tags,
        "top10": fm.get("top10", "false").lower() == "true",
        "pain": pain.group(1).strip() if pain else "",
        "steps": [s.strip() for s in steps],
        "shihua": shihua.group(1).strip() if shihua else "",
    }


def render_skill(s: dict) -> str:
    # 每条技能渲染为可折叠的 <details>；锚点放在 details 外面，
    # 顶部“新手先看”表格的链接跳过来时正好落在折叠条目上。
    short_pain = s["pain"][:28] + ("…" if len(s["pain"]) > 28 else "")
    out = [f'<a id="skill-{s["id"]}"></a>', "",
           "<details>", f"<summary><b>{s['id']}. {s['title']}</b> —— {short_pain}</summary>",
           "", s["pain"], "", "**你可以这样跟 Muse 说：**", ""]
    for i, step in enumerate(s["steps"], 1):
        out.append(f"{i}. {step}")
        out.append("")
    if s["shihua"]:
        out += [f'**实话**：{s["shihua"]}', ""]
    out += ["</details>", ""]
    return "\n".join(out)


def main() -> None:
    skills = [parse_skill(p) for p in sorted(SKILLS_DIR.glob("*.md"))]
    skills.sort(key=lambda s: s["id"])
    by_cat: dict[str, list] = {c[0]: [] for c in CATEGORIES}
    for s in skills:
        by_cat.setdefault(s["category"], []).append(s)

    total = len(skills)
    top10 = [s for s in skills if s["top10"]][:10]

    L: list[str] = []
    L += ["# Muse 中文技能库", "",
          f"*{total} 条中文原创 Muse 玩法：一个真痛点 + 三步照做 + 一句大实话，复制粘贴就能用。*",
          "",
          "*🥚 彩蛋：这个 README 是 Muse 自己写的。对，它在给自己写说明书。*",
          "",
          f"![技能](https://img.shields.io/badge/技能-{total}-blue)",
          "![原创](https://img.shields.io/badge/全部-中文原创-orange)",
          "![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen)",
          "",
          "> 这是我平时真在用的 Muse 玩法合集：搞钱、看财报、做账号、盯降价、整文件……每条只解决一个具体的小麻烦，不讲虚的。",
          ">",
          "> 每条固定三段式：**痛点**（一句话说中你）→ **三步**（复制去跟 Muse 说）→ **实话**（哪一步它搞不定、必须你亲手来）。",
          ">",
          "> 条目太多刷不到底？每条都是折叠的，点开才展开；邀请码只在这一页出现一次，不会在每条里刷屏。",
          "",
          "## 🧭 先对齐：Muse 是什么",
          "",
          "Muse 是 Meta 的 AI 个人助理。经你授权后，它能读你的邮箱、日历、健康数据、银行账单，帮你查、帮你记、帮你盯。你动嘴，它动手。",
          "",
          f"🆕 还没用过？注册时填我的邀请码 **{INVITE_CODE}**",
          "",
          "## ⚡ 30 秒上手",
          "",
          "1. **挑一条**：从下面「先看这 10 条」里找一件你正头疼的事，点开折叠条目",
          "",
          "2. **复制三步**：把三步话术粘贴给 Muse，照着说一遍就行",
          "",
          "3. **觉得有用**：右上角点个 ⭐ Star，转发给同样被琐事追着跑的朋友",
          "",
          "## 🎯 先看这 10 条",
          "",
          "| 技能 | 解决什么 |",
          "| --- | --- |",
          ]
    for s in top10:
        short_pain = s["pain"][:28] + ("…" if len(s["pain"]) > 28 else "")
        L.append(f'| [{s["id"]}. {s["title"]}](#skill-{s["id"]}) | {short_pain} |')
    L += ["", "## 🗂 全部分类", ""]
    for name, emoji, desc in CATEGORIES:
        n = len(by_cat.get(name, []))
        L.append(f"- {emoji} {name}（{n} 条）— {desc}")
    L += ["", "---", ""]
    for name, emoji, desc in CATEGORIES:
        items = by_cat.get(name, [])
        if not items:
            continue
        L += [f"## {emoji} {name}", "", f"> {desc}", ""]
        for s in items:
            L.append(render_skill(s))
        L += ["---", ""]
    L += ["## 🗓️ 更新记录", "",
          "- 2026-10-05 v2.0：500 条，全条目折叠式，头部文案重写",
          "- 2026-10-05 v1.0：110 条首发（搞钱/金融/独立开发加重版）",
          "",
          "## 📣 内容运营",
          "",
          "想把这里的技能改成 X（推特）帖子？看 [docs/x-content-plan.md](docs/x-content-plan.md)：一条技能 = 一条帖子的改写公式。",
          "",
          "## 🤝 来加一条",
          "",
          "看到缺的玩法？欢迎投稿，详见 [CONTRIBUTING.md](CONTRIBUTING.md)。",
          "",
          "## ⚠️ 说明",
          "",
          "- 技能描述的是 Muse 的能力用法，涉及银行、券商、医疗的内容仅供参考，不构成专业建议；动钱、诊断、下单这些事，永远以官方 App 和专业人士为准。",
          "- 本项目内容为原创，MIT 协议开源。",
          "",
          "## ☕ 请我喝杯咖啡",
          "",
          "如果这个库帮你省了点时间，欢迎请我喝杯咖啡。",
          "",
          "| 支付宝 | 微信支付 |",
          "| ------ | -------- |",
          "| ![支付宝收款码](assets/alipay.jpg) | ![微信支付收款码](assets/wechat-pay.png) |",
          "",
          "---",
          "",
          "*🥚 彩蛋：这个 README 是 Muse 自己写的。对，它在给自己写说明书。*",
          ""]
    README_PATH.write_text("\n".join(L), encoding="utf-8")
    print(f"done: {total} skills -> README.md")


if __name__ == "__main__":
    main()
