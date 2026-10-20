# 转向架数据迁移程序

将 Access 数据库 `BogieDB.mdb` 中表 `TblBogieLoaderInfo` 的转向架配置参数，
迁移到 `template.csv`。

## 文件说明

| 文件 | 说明 |
|---|---|
| `bogie数据迁移.md` | 任务描述文档 |
| `BogieDB.mdb` | 数据源（Access 数据库，需单独获取，见下） |
| `migrate_bogie.py` | 迁移脚本：Access → template.csv（依赖 `mdbtools` 的 `mdb-export`） |
| `template.csv` | 迁移目标文件（已填充 830 行数据） |
| `bogie_template_501.json` | bogie 对象 JSON 模板（含 `@xxxx` 占位符） |
| `gen_bogies.py` | 生成脚本：按 CSV 每行 + JSON 模板生成 bogie 对象，输出 `{车型: {架位号: 对象}}` 三层 JSON |
| `bogies.json` | 生成结果（42 车型 / 830 个对象；约 7.8MB，超出推送通道上限未入仓，本地按下面命令生成） |

## 生成 bogie 对象数据

```bash
python3 gen_bogies.py --json bogie_template_501.json --csv template.csv --out bogies.json
```

- 对 CSV 每行深拷贝一份模板，递归替换 value 中整体为 `@xxxx` 的占位符
  （用该行 `xxxx` 列的值；数字转为 JSON 数字，空单元格转为 `""`）；
- 键名中的 `@`（如 `空载@压力1`）和非占位符内容保持原样；
- 空白行（整行无数据，或车型/架位号为空）跳过不生成。

## 字段映射

| template.csv | TblBogieLoaderInfo |
|---|---|
| 车型 | CRHxh |
| 架号 | chNo1 |
| 位号 | BogieNo |
| 架位号 | 架号-位号（如 `M1-2`） |
| 空载压力1 | FreeLoadf1 |
| 空载压力2 | FreeLoadf2 |
| 满载压力1 | FullLoadf1 |
| 满载压力2 | FullLoadf2 |
| 加载头快进位移 | TblBogieType.Jzt1kjcxwy（按车型关联） |
| 加载头间距 | TblBogieCenterPt.Jzt12ZxDist（按车型关联） |
| 联轴节高度下限/上限 | 规则：和谐号 117.1~118.1，复兴号 81.3~82.3 |
| 轴箱与构架间距下限/上限 | 规则：复兴号 311~314；和谐号仅 CRH2A/2A统/2B/2B统/2E→88~91、CRH380A/380A统/380AL/380AL统/CRH2C2→70~73、CRH2C1→78~81，其余留空 |
| 空簧漏气量上限 | 规则：复兴号填 5；和谐号仅 CRH2A统/2B统/380A/380A统/380AL/380AL统/2C2→5、CRH2A/2B/2E/2C1→20，其余留空 |
| 轴距差下限/上限 | 规则：全部车型 0~1 |
| 反复空载 | 规则：复兴号 90；和谐号按架号首字母 T→80、M→70，I/E/F/B/S/V 开头（CRH380B 系/CRH3C）留空 |
| 反复满载 | 规则：和谐号 113.5，复兴号 119 |

车型命名约定：`CRH` 开头为和谐号，`CR` 开头（非 CRH）为复兴号。

其余列（加载头间距、轴距差上下限等）暂无数据源，保持为空。

## 运行

```bash
python3 migrate_bogie.py
```

## 注意

`BogieDB.mdb` 为二进制文件，请从发布渠道单独下载后与本仓库文件放在同一目录再运行脚本。
