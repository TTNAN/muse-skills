#!/usr/bin/env python3
"""从 skills/*.md 生成 README.md。

用法: python3 scripts/build.py
每条技能一个文件，README 每次全量重新生成，不要手改 README。
条目按分类分组、组内按原 id 排序，展示编号为 001-500 顺排。
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


# “今晚就能用的 10 招”用的手写短描述（比技能原文的痛点更精简），按源文件原 id 索引
TOP10_BLURBS = {
    "004": "各种 App 会员自动续费，钱扣了才发现，一年白白扔掉好几百",
    "008": "想买的东西天天刷价格，降价了不知道，买完第二天降价气到拍大腿",
    "018": "账面突然绿了，还以为自己亏了钱，其实只是除息",
    "027": "README 写得像说明书，访客三秒划走",
    "039": "客户的付款确认混在广告堆里，等你看见已经晚了",
    "046": "一份简历海投 50 家全石沉大海，HR 六秒就扫完了",
    "052": "去年忘了结婚纪念日，被念叨了整整三个月",
    "073": "一肚子话写出来却像流水账，先搭骨架再填肉",
    "093": "手机里八千张照片，找张合影得翻半小时",
    "110": "先说清 Muse 的边界，免得你对它有误会",
}


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
    # 顶部“今晚就能用的 10 招”的链接跳过来时正好落在折叠条目上。
    # 展示编号 seq 为文档顺排（001-500），与源文件原 id 无关。
    seq = s["seq"]
    short_pain = s["pain"][:28] + ("…" if len(s["pain"]) > 28 else "")
    out = [f'<a id="skill-{seq}"></a>', "",
           "<details>", f"<summary><b>{seq}. {s['title']}</b> —— {short_pain}</summary>",
           "", s["pain"], "", "**三句话术，复制就用：**", ""]
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

    # 文档顺排编号 001-500
    ordered: list[dict] = []
    for name, _emoji, _desc in CATEGORIES:
        ordered.extend(by_cat.get(name, []))
    for i, s in enumerate(ordered, 1):
        s["seq"] = f"{i:03d}"
    total = len(ordered)
    top10 = [s for s in ordered if s["top10"]][:10]

    L: list[str] = []
    L += ["# Muse 500 招", "",
          f"*500 个把 Muse 用出花的中文真招——专治各种\"明明可以让 AI 干\"的小麻烦。*",
          "",
          "*🥚 彩蛋：这个 README 是 Muse 自己写的。对，它在给自己写说明书。*",
          "",
          f"![技能](https://img.shields.io/badge/技能-{total}-blue)",
          "![原创](https://img.shields.io/badge/全部-中文原创-orange)",
          "![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen)",
          "",
          "> 这是我每天真在用的 Muse 玩法：搞钱、看财报、做账号、盯降价、整文件……",
          "> 每招只干一件事：**说中你的痛**，**给你三句话术**，再附一句**实话**告诉你哪步它搞不定、必须亲手来。",
          ">",
          "> 500 条刷不到底？全是折叠的，点开才展开。邀请码这页只出现一次，不会在每条里刷屏——你懂的。",
          "",
          "## 怎么用",
          "",
          "不用从头读。直接 Ctrl+F 搜你正头疼的事，点开那条，把三句话术复制给 Muse 就行。",
          "",
          f"Muse 是 Meta 的 AI 个人助理，经你授权能读邮箱、日历、健康数据、银行账单。你动嘴，它动手。还没用过？注册填我邀请码 **{INVITE_CODE}**。",
          "",
          "觉得有用就点个 ⭐ Star，顺手转发给天天被琐事追着跑的朋友。",
          "",
          "## 今晚就能用的 10 招",
          "",
          ]
    for i, s in enumerate(top10, 1):
        blurb = TOP10_BLURBS.get(s["id"], s["pain"])
        L.append(f'{i}. [{s["seq"]}. {s["title"]}](#skill-{s["seq"]})——{blurb}')
    L += ["", "## 十二个场景，500 招全在这", ""]
    idx = " · ".join(f"**{emoji} {name}** {len(by_cat.get(name, []))}" for name, emoji, _d in CATEGORIES)
    L += [idx, "", "---"]
    for name, emoji, desc in CATEGORIES:
        items = by_cat.get(name, [])
        if not items:
            continue
        L += [f"## {emoji} {name}", "", f"> {desc}", ""]
        for s in items:
            L.append(render_skill(s))
        L += ["---", ""]
    L += ["## 🗓️ 更新记录", "",
          "- 2026-10-05 v1.0：500 条首发，全条目折叠式",
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
