#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转向架数据迁移程序
==================
数据源: BogieDB.mdb (Access 数据库, 表 TblBogieLoaderInfo)
迁移目标: template.csv

字段映射:
    车型     <- CRHxh
    架号     <- chNo1
    位号     <- BogieNo
    架位号   <- 架号-位号 (如 M1-2)
    空载压力1 <- Loadf1
    空载压力2 <- Loadf2
    满载压力1 <- FullLoadf1
    满载压力2 <- FullLoadf2

用法: python3 migrate_bogie.py
"""

import csv
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MDB_FILE = BASE_DIR / "BogieDB.mdb"
TEMPLATE_FILE = BASE_DIR / "template.csv"

TARGET_COLUMNS = [
    "车型", "架号", "位号", "架位号",
    "加载头间距", "加载头快进位移",
    "轴距差下限", "轴距差上限",
    "联轴节高度下限", "联轴节高度上限",
    "空载压力1", "空载压力2", "满载压力1", "满载压力2",
    "轴箱与构架间距下限", "轴箱与构架间距上限",
    "空簧漏气量上限",
]

FILLED = {
    "车型": "CRHxh",
    "架号": "chNo1",
    "位号": "BogieNo",
    "空载压力1": "Loadf1",
    "空载压力2": "Loadf2",
    "满载压力1": "FullLoadf1",
    "满载压力2": "FullLoadf2",
}


def export_table() -> list[dict]:
    """用 mdb-export 导出 Access 表为字典列表。"""
    proc = subprocess.run(
        ["mdb-export", str(MDB_FILE), "TblBogieLoaderInfo"],
        capture_output=True, text=True, check=True,
    )
    return list(csv.DictReader(proc.stdout.splitlines()))


def migrate(records: list[dict]) -> list[dict]:
    rows = []
    for rec in records:
        架号 = (rec.get("chNo1") or "").strip()
        位号 = (rec.get("BogieNo") or "").strip()
        row = {col: "" for col in TARGET_COLUMNS}
        row["车型"] = (rec.get(FILLED["车型"]) or "").strip()
        row["架号"] = 架号
        row["位号"] = 位号
        row["架位号"] = f"{架号}-{位号}" if 架号 and 位号 else ""
        for target, src in FILLED.items():
            if target in ("车型", "架号", "位号"):
                continue
            row[target] = (rec.get(src) or "").strip()
        rows.append(row)
    return rows


def main() -> int:
    if not MDB_FILE.exists():
        print(f"错误: 找不到数据源 {MDB_FILE}", file=sys.stderr)
        return 1

    records = export_table()
    print(f"从 TblBogieLoaderInfo 读出 {len(records)} 条记录")
    rows = migrate(records)

    with open(TEMPLATE_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TARGET_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"已写入 {TEMPLATE_FILE}，共 {len(rows)} 行数据")
    return 0


if __name__ == "__main__":
    sys.exit(main())
