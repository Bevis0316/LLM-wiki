#!/usr/bin/env python3
"""
LLM Wiki 與教學簡報自動化檢查腳本（無需第三方套件）
用途：輔助執行 AGENTS.md 中的「檢查關卡 1」與「檢查關卡 4」
使用方式：在專案根目錄執行 `python scripts/check_wiki.py`
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "01_原始資料"
WIKI_DIR = ROOT / "02_Wiki"
SLIDES_JS = ROOT / "docs" / "slides-data.js"


def list_md_files(directory: Path, ignore_prefixes=("_", "README")) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(
        p for p in directory.glob("*.md")
        if not any(p.name.startswith(pref) for pref in ignore_prefixes)
    )


def parse_frontmatter(text: str) -> dict:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}
    block = match.group(1)
    data = {"sources": []}
    in_sources = False
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("sources:"):
            in_sources = True
            continue
        if in_sources:
            if stripped.startswith("- "):
                data["sources"].append(stripped[2:].strip().strip('"').strip("'"))
            elif stripped and not line.startswith(" "):
                in_sources = False
        if not in_sources and ":" in stripped:
            k, v = stripped.split(":", 1)
            data[k.strip()] = v.strip()
    return data


def extract_wikilinks(text: str) -> list[str]:
    links = re.findall(r"\[\[([^\[\]|#]+)(?:[#|][^\[\]]+)?\]\]", text)
    return [l.strip() for l in links]


def check_phase_a():
    print("=" * 60)
    print("【檢查關卡 1】01_原始資料 與 02_Wiki 完整性檢查")
    print("=" * 60)

    raw_files = list_md_files(RAW_DIR)
    raw_names = {f"01_原始資料/{p.name}" for p in raw_files}
    print(f"- 原始資料篇數：{len(raw_files)} 篇（作業要求至少 5 篇）")
    if len(raw_files) < 5:
        print("  [警告] 原始資料尚不足 5 篇！")

    wiki_files = list_md_files(WIKI_DIR)
    wiki_stems = {p.stem for p in wiki_files}
    print(f"- Wiki 概念頁數：{len(wiki_files)} 頁")

    errors = 0
    for wf in wiki_files:
        content = wf.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        sources = fm.get("sources", [])
        if not sources:
            print(f"  [錯誤] {wf.name} 缺少 YAML frontmatter 的 sources 來源標註")
            errors += 1
        else:
            for src in sources:
                if src not in raw_names and not (ROOT / src).exists():
                    print(f"  [錯誤] {wf.name} 參照的來源不存在：{src}")
                    errors += 1

        for link in extract_wikilinks(content):
            link_stem = Path(link).stem
            if link_stem not in wiki_stems and not (ROOT / f"{link}.md").exists():
                print(f"  [警告] {wf.name} 包含尚未建立的雙向連結：[[{link}]]")

    if errors == 0 and len(wiki_files) > 0:
        print("  [通過] 所有 Wiki 概念頁均具備有效來源追溯。")
    return wiki_stems, errors


def check_phase_b(wiki_stems: set[str]):
    print("\n" + "=" * 60)
    print("【檢查關卡 4】docs/slides-data.js 與 Wiki 來源對應檢查")
    print("=" * 60)

    if not SLIDES_JS.exists():
        print("  [錯誤] 找不到 docs/slides-data.js")
        return 1

    js_text = SLIDES_JS.read_text(encoding="utf-8")
    match = re.search(r"window\.SLIDES_DATA\s*=\s*(\{.*\});?", js_text, re.DOTALL)
    if not match:
        print("  [錯誤] 無法解析 docs/slides-data.js 中的 window.SLIDES_DATA")
        return 1

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"  [錯誤] slides-data.js JSON 格式錯誤：{e}")
        return 1

    slides = data.get("slides", [])
    print(f"- 簡報總頁數：{len(slides)} 頁")

    errors = 0
    unmatched = 0
    placeholder_hits = 0

    for idx, slide in enumerate(slides, 1):
        title = slide.get("title", f"Slide {idx}")
        sources = slide.get("sources", [])
        raw_dump = json.dumps(slide, ensure_ascii=False)
        if "待從" in raw_dump or "TODO" in raw_dump:
            placeholder_hits += 1

        if not sources:
            print(f"  [錯誤] 第 {idx} 頁《{title}》缺少 sources 來源欄位")
            errors += 1
            continue

        for src in sources:
            if src == "總覽":
                continue
            if wiki_stems and src not in wiki_stems:
                print(f"  [警告] 第 {idx} 頁《{title}》對應的 Wiki 頁面尚未建立：[[{src}]]")
                unmatched += 1

    if placeholder_hits > 0:
        print(f"  [提醒] 共有 {placeholder_hits} 頁仍包含範例佔位文字（尚未以實際 Wiki 內容替換）。")
    if errors == 0 and unmatched == 0 and wiki_stems:
        print("  [通過] 簡報所有頁面皆與 02_Wiki/ 頁面 100% 對應！")
    return errors


def main():
    wiki_stems, err_a = check_phase_a()
    err_b = check_phase_b(wiki_stems)
    print("\n" + "=" * 60)
    total_err = err_a + err_b
    print(f"檢查結束：共發現 {total_err} 個阻斷錯誤。")
    sys.exit(1 if total_err > 0 else 0)


if __name__ == "__main__":
    main()
