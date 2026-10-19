#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据 CSV 与 JSON 模板生成 bogie 对象数据.

用法:
    python3 gen_bogies.py --json bogie_template_501.json --csv template.csv --out bogies.json

输出结构 (3 层):
    { 车型: { 架位号: <模板深拷贝并替换占位符后的 bogie 对象> } }

替换规则:
    递归遍历模板的 dict / list, 凡 value 整体为 "@xxxx" 形式的字符串,
    用同行 CSV 中 xxxx 列的值替换; 键名中的 @ 不动, 其余内容保持原样.
    CSV 中的数字字符串转为 JSON 数字, 空单元格转为 "".

空白行 (整行无数据, 或 车型/架位号 为空) 跳过不生成.
"""

import argparse
import copy
import csv
import json
import re
import sys
from pathlib import Path

PLACEHOLDER_RE = re.compile(r"^@(.+)$", re.DOTALL)


def to_json_value(text: str):
    """CSV 单元格 -> JSON 值: 数字转数字, 空串保持空串, 其余保持字符串."""
    s = text.strip()
    if s == "":
        return ""
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def substitute(node, row: dict):
    """递归替换模板中的 @xxxx 占位符."""
    if isinstance(node, dict):
        return {k: substitute(v, row) for k, v in node.items()}
    if isinstance(node, list):
        return [substitute(v, row) for v in node]
    if isinstance(node, str):
        m = PLACEHOLDER_RE.match(node)
        if m:
            col = m.group(1)
            if col not in row:
                print(f"警告: 占位符 @{col} 在 CSV 中无此列, 保持原样",
                      file=sys.stderr)
                return node
            return to_json_value(row[col])
    return node


def is_blank(row: dict) -> bool:
    """空白行判定: 整行无数据, 或 车型/架位号 为空."""
    if not any((v or "").strip() for v in row.values()):
        return True
    if not (row.get("车型") or "").strip():
        return True
    if not (row.get("架位号") or "").strip():
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="根据 CSV 与 JSON 模板生成 bogie 对象数据")
    ap.add_argument("--json", required=True, help="JSON 模板文件路径")
    ap.add_argument("--csv", required=True, help="CSV 数据文件路径")
    ap.add_argument("--out", default="bogies.json", help="输出文件路径 (默认 bogies.json)")
    args = ap.parse_args()

    with open(args.json, encoding="utf-8") as f:
        template = json.load(f)
    with open(args.csv, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    data: dict = {}
    skipped = 0
    for lineno, raw in enumerate(rows, start=2):
        row = {k: (v if v is not None else "") for k, v in raw.items()}
        if is_blank(row):
            skipped += 1
            continue
        车型 = row["车型"].strip()
        架位号 = row["架位号"].strip()
        group = data.setdefault(车型, {})
        if 架位号 in group:
            print(f"警告: 第 {lineno} 行 车型={车型} 架位号={架位号} 重复, 覆盖上一条",
                  file=sys.stderr)
        group[架位号] = substitute(copy.deepcopy(template), row)

    out_path = Path(args.out)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total = sum(len(v) for v in data.values())
    print(f"车型数: {len(data)}, 共生成 {total} 个 bogie 对象, "
          f"跳过空白行 {skipped} 行")
    print(f"已写入 {out_path} "
          f"({out_path.stat().st_size / 1024 / 1024:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
