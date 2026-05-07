# 周跳探测小程序 — 设计文档

**日期**: 2026-05-07 | **状态**: 待实现

---

## 1. 概述

一个基于 Web 的 GNSS 周跳探测工具，输入 RINEX 双频观测文件，使用 TurboEdit（GF+MW 组合）算法自动检测周跳，提供结果表格和可视化图表，支持导出 CSV 报告。

**交付物**: Python 源代码 + PyInstaller 打包的可执行文件(Windows `.exe` / macOS `.app`)

---

## 2. 技术栈

| 层 | 选型 |
|---|---|
| Web 框架 | Streamlit |
| 图表 | Plotly |
| 数据处理 | pandas, numpy |
| RINEX 解析 | georinex |
| 打包 | PyInstaller |

---

## 3. 架构

```
周跳探测小程序/
├── app.py                    # Streamlit 主入口
├── core/
│   ├── __init__.py
│   ├── rinex_reader.py       # RINEX 文件解析
│   └── detector.py           # 周跳探测算法 (GF + MW)
├── ui/
│   ├── __init__.py
│   ├── sidebar.py            # 侧边栏 (上传、参数)
│   ├── results.py            # 结果表格
│   └── charts.py             # 可视化图表
├── requirements.txt
└── build.py                  # PyInstaller 打包脚本
```

- `core/` 纯算法层，不依赖任何 UI 框架，可独立测试
- `ui/` Streamlit 展示层
- `app.py` 组装两者

---

## 4. 数据流

```
RINEX文件 → rinex_reader → DataFrame(时间,卫星,L1,L2,P1,P2)
                                    ↓
                              detector (GF+MW)
                                    ↓
                              周跳列表 DataFrame
                                    ↓
                        ┌──────────┴──────────┐
                        ↓                      ↓
                   results.py              charts.py
                  表格 + CSV导出         Plotly时序图(异常标注)
```

---

## 5. 核心算法: TurboEdit

### GF 组合 (Geometry-Free)
- 公式: Φ₁ − Φ₂ (以周为单位)
- 历元间差分超过阈值 → 标记周跳
- 对小周跳敏感，受电离层缓变影响

### MW 组合 (Melbourne-Wübbena)
- 公式: (f₁·Φ₁−f₂·Φ₂)/(f₁−f₂) − (f₁·P₁+f₂·P₂)/(f₁+f₂) (宽度)
- 滑动窗口均值跳变检测
- 噪声大但不受电离层和几何影响，适合探测大周跳

### 合并策略
GF 和 MW 检测结果取并集，同一历元合并去重，输出最终周跳列表。

### 可调参数
- GF 差分阈值 (默认 0.05 周)
- MW 滑动窗口大小 (默认 30 历元)
- MW 跳变阈值 (默认 1.0 周)

---

## 6. 界面布局

- **侧边栏**: 文件上传区域、参数滑块(阈值/窗口)、关于/算法说明
- **主区域 Tab1「周跳结果」**: 周跳列表表格 (PRN, GPS时间, GF跳变量, MW跳变量) + 导出CSV按钮
- **主区域 Tab2「可视化分析」**: 卫星选择下拉框 + GF/MW组合时序图(Plotly, 异常点红色标注)

---

## 7. 打包方案

PyInstaller 打包为单文件:
- Windows: `pyinstaller --onefile --add-data "..." app.py` → `dist/周跳探测.exe`
- macOS: 同上 → `dist/周跳探测.app`

启动后自动打开浏览器访问 `http://localhost:8501`。

---

## 8. 输入输出约定

- **输入**: RINEX 2.x/3.x 观测文件 (`.obs`, `.rnx`, `.??o`)
- **输出**: 
  - 界面表格: PRN, GPS时间, GF跳变(周), MW跳变(周)
  - CSV 文件: 同表格内容
  - 图表: 每个卫星的 GF/MW 时序图, 周跳点红色标注
