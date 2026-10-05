#!/usr/bin/env python3
"""校验 skills/*.md 是否符合投稿规范（CONTRIBUTING.md）。

用法: python3 scripts/check.py
任一规则失败即退出码非 0，并打印全部问题。CI 在每个 PR 上跑这个。
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"

CATEGORIES = {
    "搞钱与副业", "金融与投资", "独立开发", "工作与效率",
    "生活日常", "购物与省钱", "内容创作与涨粉", "出行与预订",
    "健康与运动", "文件与云盘", "组合技", "实话实说",
}


def parse_frontmatter(text: str, path: pathlib.Path):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        return None, None
    fm = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, m.group(2)


def main() -> int:
    issues: list[str] = []
    seen_ids: dict[str, str] = {}

    for path in sorted(SKILLS_DIR.glob("*.md")):
        slug = path.stem
        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text, path)
        if fm is None:
            issues.append(f"{slug}: frontmatter 解析失败（必须以 --- 开头结尾）")
            continue

        sid = fm.get("id", "")
        if not sid:
            issues.append(f"{slug}: 缺少 id")
        elif not re.fullmatch(r"\d{3}", sid):
            issues.append(f"{slug}: id 必须是 3 位数字（当前 {sid!r}）")
        elif not slug.startswith(sid + "-"):
            issues.append(f"{slug}: 文件名须以 {sid}- 开头")
        if sid in seen_ids:
            issues.append(f"{slug}: id {sid} 与 {seen_ids[sid]} 重复")
        else:
            seen_ids[sid] = slug

        if not fm.get("title"):
            issues.append(f"{slug}: 缺少 title")
        if fm.get("category") not in CATEGORIES:
            issues.append(f"{slug}: 分类非法 {fm.get('category')!r}（只能从既有分类里选）")
        if "top10" in fm and fm["top10"] not in ("true", "false"):
            issues.append(f"{slug}: top10 只能是 true/false")

        pain = re.search(r"\*\*痛点\*\*：(.+?)(?=\n\*\*三步做法\*\*)", body, re.DOTALL)
        if not pain:
            issues.append(f"{slug}: 找不到「**痛点**：」段落")
        elif len(pain.group(1).strip()) > 65:
            issues.append(f"{slug}: 痛点太长（{len(pain.group(1).strip())} 字，上限 65）")

        steps = re.findall(r"^[123]\.\s*(.+)$", body, re.MULTILINE)
        if len(steps) != 3:
            issues.append(f"{slug}: 三步做法必须是 3 步（当前 {len(steps)} 步）")
        elif not any("「" in s for s in steps):
            issues.append(f"{slug}: 三步里至少一步要有「」引用的可复制原话")

        shihua = re.search(r"\*\*实话\*\*：(.+)", body, re.DOTALL)
        if not shihua:
            issues.append(f"{slug}: 缺少「**实话**：」段落")
        elif "你" not in shihua.group(1) and "本人" not in shihua.group(1):
            issues.append(f"{slug}: 「实话」要写清哪一步必须你本人动手")

        words = len(re.sub(r"\s", "", body))
        if not (120 <= words <= 240):
            issues.append(f"{slug}: 正文 {words} 字（要求 120–220 字）")
        if "邀请码" in body:
            issues.append(f"{slug}: 正文不许出现「邀请码」（构建脚本会自动追加）")

    if issues:
        print(f"check 失败：{len(issues)} 个问题\n")
        for i in issues:
            print(" -", i)
        return 1
    print(f"check 通过 ✅（{len(seen_ids)} 条技能）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
