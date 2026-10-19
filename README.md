# 转向架数据迁移程序

将 Access 数据库 `BogieDB.mdb` 中表 `TblBogieLoaderInfo` 的转向架配置参数，
迁移到 `template.csv`。

## 文件说明

| 文件 | 说明 |
|---|---|
| `bogie数据迁移.md` | 任务描述文档 |
| `BogieDB.mdb` | 数据源（Access 数据库，需单独获取，见下） |
| `migrate_bogie.py` | 迁移脚本（依赖 `mdbtools` 的 `mdb-export`） |
| `template.csv` | 迁移目标文件（已填充 830 行数据） |

## 字段映射

| template.csv | TblBogieLoaderInfo |
|---|---|
| 车型 | CRHxh |
| 架号 | chNo1 |
| 位号 | BogieNo |
| 架位号 | 架号-位号（如 `M1-2`） |
| 空载压力1 | Loadf1 |
| 空载压力2 | Loadf2 |
| 满载压力1 | FullLoadf1 |
| 满载压力2 | FullLoadf2 |
| 加载头快进位移 | TblBogieType.Jzt1kjcxwy（按车型关联） |
| 加载头间距 | TblBogieCenterPt.Jzt12ZxDist（按车型关联） |
| 联轴节高度下限/上限 | 规则：和谐号 117.1~118.1，复兴号 81.3~82.3 |
| 轴箱与构架间距下限/上限 | 规则：复兴号 311~314；和谐号仅 CRH2A/2A统/2B/2B统/2E→88~91、CRH380A/380A统/380AL/380AL统/CRH2C2→70~73、CRH2C1→78~81，其余留空 |

车型命名约定：`CRH` 开头为和谐号，`CR` 开头（非 CRH）为复兴号。

其余列（加载头间距、轴距差上下限等）暂无数据源，保持为空。

## 运行

```bash
python3 migrate_bogie.py
```

## 注意

`BogieDB.mdb` 为二进制文件，请从发布渠道单独下载后与本仓库文件放在同一目录再运行脚本。
