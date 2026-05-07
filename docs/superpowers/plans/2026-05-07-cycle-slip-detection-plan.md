# 周跳探测小程序 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个基于 Streamlit 的 GNSS 周跳探测 Web 应用，输入 RINEX 双频观测文件，使用 TurboEdit（GF+MW）算法检测周跳，输出结果表格和交互式图表。

**Architecture:** 分层架构 — `core/` 纯算法层（RINEX 解析 + 周跳探测），不依赖任何 UI 框架；`ui/` Streamlit 展示层；`app.py` 组装两者。算法层编写自动化测试，UI 层手工验证。

**Tech Stack:** Python 3.10+, Streamlit, Plotly, pandas, numpy, georinex, PyInstaller

---

### Task 1: 项目骨架搭建

**Files:**
- Create: `requirements.txt`
- Create: `core/__init__.py`
- Create: `ui/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: 创建 requirements.txt**

```txt
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.0.0
numpy>=1.24.0
georinex>=1.15.0
pyinstaller>=6.0.0
pytest>=7.4.0
```

- [ ] **Step 2: 创建目录结构和空 __init__.py**

```bash
mkdir -p core ui tests
touch core/__init__.py ui/__init__.py tests/__init__.py
```

- [ ] **Step 3: 创建 tests/conftest.py**

```python
import pytest
import numpy as np
import pandas as pd


def make_clean_data(n=100):
    """生成模拟双频观测数据: 无周跳"""
    np.random.seed(42)
    t = pd.date_range("2024-01-01 00:00:00", periods=n, freq="30s")
    L1 = np.cumsum(np.random.randn(n) * 0.01) + 1000000.0
    L2 = np.cumsum(np.random.randn(n) * 0.01) + 800000.0
    P1 = 21000000.0 + np.random.randn(n) * 0.5
    P2 = 21000000.0 + np.random.randn(n) * 0.5
    return pd.DataFrame({"time": t, "sv": "G01", "L1": L1, "L2": L2, "P1": P1, "P2": P2})


def make_slip_data(n=100, slip_idx=50, slip_cycles=5.0):
    """生成包含一个周跳的模拟数据: slip_idx 处 L1 跳变 slip_cycles 周"""
    np.random.seed(42)
    t = pd.date_range("2024-01-01 00:00:00", periods=n, freq="30s")
    L1 = np.cumsum(np.random.randn(n) * 0.01) + 1000000.0
    L1[slip_idx:] += slip_cycles
    L2 = np.cumsum(np.random.randn(n) * 0.01) + 800000.0
    P1 = 21000000.0 + np.random.randn(n) * 0.5
    P2 = 21000000.0 + np.random.randn(n) * 0.5
    return pd.DataFrame({"time": t, "sv": "G01", "L1": L1, "L2": L2, "P1": P1, "P2": P2})


@pytest.fixture
def sample_rinex_data():
    return make_clean_data()


@pytest.fixture
def sample_data_with_slip():
    return make_slip_data()
```

- [ ] **Step 4: 安装依赖并验证**

```bash
cd "/Users/chenjunbin/Desktop/周跳探测小程序"
pip install -r requirements.txt
python -c "import streamlit; import plotly; import pandas; import numpy; import georinex; import pytest; print('All imports OK')"
```

Expected: `All imports OK`

- [ ] **Step 5: 运行空测试套件**

```bash
python -m pytest tests/ -v
```

Expected: no tests collected, exit code 0

- [ ] **Step 6: Commit**

```bash
git init
git add requirements.txt core/__init__.py ui/__init__.py tests/conftest.py tests/__init__.py
git commit -m "chore: init project skeleton with dependencies and test fixtures"
```

---

### Task 2: RINEX 文件解析

**Files:**
- Create: `tests/test_rinex_reader.py`
- Create: `core/rinex_reader.py`

- [ ] **Step 1: 编写测试 — test_rinex_reader.py**

```python
import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from core.rinex_reader import parse_rinex, extract_observations


def create_minimal_rinex3(tmp_path):
    """创建一个最小化的 RINEX 3 观测文件用于测试"""
    content = """     3.03           OBSERVATION DATA    M                   RINEX VERSION / TYPE
pyRINEX                                20240101 000000 UTC PGM / RUN BY / DATE
                                                            MARKER NAME
                                                            MARKER NUMBER
                                                            OBSERVER / AGENCY
                                                            REC # / TYPE / VERS
                                                            ANT # / TYPE
   2112345.6789   1234567.8900   9876543.2100                  APPROX POSITION XYZ
        0.0000        0.0000        0.0000                  ANTENNA: DELTA H/E/N
G   18 C1C L1C D1C S1C C2W L2W D2W S2W                      SYS / # / OBS TYPES
  2024    01    01    00    00   00.0000000     GPS         TIME OF FIRST OBS
                                                            END OF HEADER
"""
    fpath = tmp_path / "test.obs"
    fpath.write_text(content)
    return str(fpath)


def test_extract_observations_with_sample_data(sample_rinex_data):
    """测试从 DataFrame 中提取卫星观测值"""
    result = extract_observations(sample_rinex_data)
    assert isinstance(result, pd.DataFrame)
    assert "L1" in result.columns
    assert "L2" in result.columns
    assert "P1" in result.columns
    assert "P2" in result.columns
    assert "sv" in result.columns
    assert "time" in result.columns


def test_extract_observations_str():
    """测试列名兼容 — L1 可以是 'L1' 也可能是别的名称"""
    df = pd.DataFrame({
        "time": pd.date_range("2024-01-01", periods=3, freq="30s"),
        "sv": "G01",
        "L1C": [100.0, 101.0, 102.0],
        "L2W": [80.0, 81.0, 82.0],
        "C1C": [21000000.0, 21000001.0, 21000002.0],
        "C2W": [21000000.0, 21000001.0, 21000002.0],
    })
    result = extract_observations(df)
    assert "L1" in result.columns
    assert "L2" in result.columns
    assert "P1" in result.columns
    assert "P2" in result.columns
```

- [ ] **Step 2: 运行测试 — 确认失败**

```bash
python -m pytest tests/test_rinex_reader.py -v
```

Expected: FAIL with ImportError (文件不存在)

- [ ] **Step 3: 实现 core/rinex_reader.py**

```python
"""RINEX 观测文件解析模块。

支持 RINEX 2.x 和 3.x 格式，使用 georinex 库解析，
输出标准化的 pandas DataFrame。
"""

import pandas as pd
import georinex as gr


def parse_rinex(filepath: str) -> pd.DataFrame:
    """解析 RINEX 观测文件，返回标准化 DataFrame。

    Args:
        filepath: RINEX 文件路径

    Returns:
        包含观测值的 DataFrame，列包含 time, sv, L1, L2, P1, P2
    """
    ds = gr.load(filepath, use="all")
    df = ds.to_dataframe()
    df = df.reset_index()
    return extract_observations(df)


def extract_observations(df: pd.DataFrame) -> pd.DataFrame:
    """从 georinex 输出的 DataFrame 中提取标准化的双频观测值。

    处理 RINEX 3 命名约定（如 L1C, L2W, C1C, C2W）并统一映射到
    标准列名 L1, L2, P1, P2。
    """
    col_map = {}

    for col in df.columns:
        if col in ("L1", "L1C", "L1P", "L1W"):
            col_map[col] = "L1"
        elif col in ("L2", "L2C", "L2P", "L2W", "L2X"):
            col_map[col] = "L2"
        elif col in ("C1", "C1C", "C1P", "C1W", "P1"):
            col_map[col] = "P1"
        elif col in ("C2", "C2C", "C2P", "C2W", "P2"):
            col_map[col] = "P2"

    needed = {"L1", "L2", "P1", "P2", "sv", "time"}
    result = df.rename(columns=col_map)

    for name in needed:
        if name not in result.columns and name in result.columns:
            pass

    available = [c for c in needed if c in result.columns]
    return result[available]
```

- [ ] **Step 4: 运行测试 — 应通过**

```bash
python -m pytest tests/test_rinex_reader.py -v
```

Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add core/rinex_reader.py tests/test_rinex_reader.py
git commit -m "feat: add RINEX file parser with standardized column mapping"
```

---

### Task 3: 周跳探测 — GF 组合

**Files:**
- Create: `tests/test_detector.py`
- Create: `core/detector.py`

- [ ] **Step 1: 编写 GF 检测测试**

```python
import pytest
import pandas as pd
import numpy as np
from core.detector import detect_gf


def test_gf_no_slip(sample_rinex_data):
    """无周跳数据: GF 检测应返回空结果"""
    result = detect_gf(sample_rinex_data, threshold=0.05)
    assert len(result) == 0


def test_gf_with_slip(sample_data_with_slip):
    """有周跳数据: GF 应检测到第50个历元处的跳变"""
    result = detect_gf(sample_data_with_slip, threshold=0.05)
    assert len(result) >= 1
    slip_time = result.iloc[0]["time"]
    assert slip_time == sample_data_with_slip.iloc[50]["time"]


def test_gf_computation():
    """验证 GF 组合计算公式正确"""
    df = pd.DataFrame({
        "time": pd.date_range("2024-01-01", periods=5, freq="30s"),
        "sv": "G01",
        "L1": [100.0, 100.1, 100.2, 100.3, 105.3],  # last point has 5-cycle slip
        "L2": [80.0, 80.1, 80.2, 80.3, 80.3],
        "P1": [21000000.0] * 5,
        "P2": [21000000.0] * 5,
    })
    result = detect_gf(df, threshold=0.05)
    assert len(result) == 1
    assert abs(result.iloc[0]["gf_jump"]) > 4.0  # ~5 cycle jump
```

- [ ] **Step 2: 运行测试 — 确认失败**

```bash
python -m pytest tests/test_detector.py::test_gf_no_slip -v
```

Expected: FAIL (ImportError, 文件不存在)

- [ ] **Step 3: 实现 GF 检测代码**

```python
"""周跳探测核心算法模块。

实现 TurboEdit 方法: GF（Geometry-Free）组合 + MW（Melbourne-Wübbena）组合。
"""

import numpy as np
import pandas as pd


# GPS 频段常量
F1 = 1575.42e6   # L1 频率 (Hz)
F2 = 1227.60e6   # L2 频率 (Hz)
C = 299792458.0  # 光速 (m/s)
WL1 = C / F1     # L1 波长 (~0.190 m)
WL2 = C / F2     # L2 波长 (~0.244 m)


def detect_gf(df: pd.DataFrame, threshold: float = 0.05) -> pd.DataFrame:
    """使用 GF（Geometry-Free）组合检测周跳。

    GF = L1 - L2 (以周为单位)
    历元间差分超过阈值 → 标记为周跳。

    Args:
        df: 单个卫星的观测数据，需含 L1、L2、time 列
        threshold: 历元间 GF 差分的检测阈值（周）

    Returns:
        检测到的周跳列表 DataFrame，列: time, sv, gf_value, gf_diff, gf_jump
    """
    if len(df) < 2:
        return pd.DataFrame(columns=["time", "sv", "gf_value", "gf_diff", "gf_jump"])

    data = df.sort_values("time").copy()
    data["gf_value"] = data["L1"] - data["L2"]
    data["gf_diff"] = data["gf_value"].diff()
    slips = data[np.abs(data["gf_diff"]) > threshold].copy()

    if len(slips) == 0:
        return pd.DataFrame(columns=["time", "sv", "gf_value", "gf_diff", "gf_jump"])

    slips["gf_jump"] = slips["gf_diff"]
    sv = df["sv"].iloc[0] if "sv" in df.columns else "UNKNOWN"
    slips["sv"] = sv
    return slips[["time", "sv", "gf_value", "gf_diff", "gf_jump"]].reset_index(drop=True)
```

- [ ] **Step 4: 运行测试 — 应通过**

```bash
python -m pytest tests/test_detector.py -v
```

Expected: 3 passed (test_gf_no_slip, test_gf_with_slip, test_gf_computation)

- [ ] **Step 5: Commit**

```bash
git add core/detector.py tests/test_detector.py
git commit -m "feat: add GF (Geometry-Free) cycle slip detection"
```

---

### Task 4: 周跳探测 — MW 组合

**Files:**
- Modify: `core/detector.py` — 添加 `detect_mw` 函数
- Modify: `tests/test_detector.py` — 添加 MW 测试

- [ ] **Step 1: 更新 imports，然后追加 MW 检测测试到 tests/test_detector.py**

将 test_detector.py 顶部的 import 行改为:

```python
from core.detector import detect_gf, detect_mw, F1, F2, WL1, WL2
```

然后在文件末尾追加:

```python
def test_mw_no_slip(sample_rinex_data):
    """无周跳数据: MW 检测应返回空结果"""
    result = detect_mw(sample_rinex_data, window=30, threshold=1.0)
    assert len(result) == 0


def test_mw_with_slip(sample_data_with_slip):
    """有周跳数据: MW 应检测到异常"""
    result = detect_mw(sample_data_with_slip, window=5, threshold=1.0)
    assert len(result) >= 1


def test_mw_values_reasonable():
    """验证 MW 组合值在合理范围内（通常在几个宽巷波长范围内）"""
    np.random.seed(123)
    n = 200
    df = pd.DataFrame({
        "time": pd.date_range("2024-01-01", periods=n, freq="30s"),
        "sv": "G01",
        "L1": np.cumsum(np.random.randn(n) * 0.01) + 1e6,
        "L2": np.cumsum(np.random.randn(n) * 0.01) + 8e5,
        "P1": 21000000.0 + np.random.randn(n) * 0.5,
        "P2": 21000000.0 + np.random.randn(n) * 0.5,
    })
    df = df.sort_values("time")
    df["mw_value"] = (df["L1"] - df["L2"]) - (F1 - F2) / (F1 + F2) * (
        df["P1"] / WL1 + df["P2"] / WL2
    )
    assert df["mw_value"].std() < 5.0
```

- [ ] **Step 2: 运行测试 — 确认失败**

```bash
python -m pytest tests/test_detector.py::test_mw_no_slip -v
```

Expected: FAIL (ImportError, detect_mw 不存在)

- [ ] **Step 3: 在 core/detector.py 中添加 MW 检测函数**

在 `detect_gf` 函数之后追加:

```python
def detect_mw(
    df: pd.DataFrame, window: int = 30, threshold: float = 1.0
) -> pd.DataFrame:
    """使用 MW（Melbourne-Wübbena）组合检测周跳。

    MW = (L1 - L2) - (f1-f2)/(f1+f2) * (P1/λ1 + P2/λ2)   [宽巷周数]
    滑动窗口均值与当前值差超过阈值 → 标记为周跳。

    Args:
        df: 单个卫星的观测数据，需含 L1、L2、P1、P2、time 列
        window: 滑动窗口大小（历元数）
        threshold: 跳变检测阈值（宽巷周数）

    Returns:
        检测到的周跳列表 DataFrame，列: time, sv, mw_value, mw_mean, mw_jump
    """
    if len(df) < window:
        return pd.DataFrame(columns=["time", "sv", "mw_value", "mw_mean", "mw_jump"])

    data = df.sort_values("time").copy()
    data["mw_value"] = (data["L1"] - data["L2"]) - (F1 - F2) / (F1 + F2) * (
        data["P1"] / WL1 + data["P2"] / WL2
    )
    data["mw_mean"] = data["mw_value"].rolling(window=window, min_periods=window).mean()
    data["mw_diff"] = np.abs(data["mw_value"] - data["mw_mean"])
    slips = data[data["mw_diff"] > threshold].copy()

    if len(slips) == 0:
        return pd.DataFrame(columns=["time", "sv", "mw_value", "mw_mean", "mw_jump"])

    slips["mw_jump"] = slips["mw_diff"]
    sv = df["sv"].iloc[0] if "sv" in df.columns else "UNKNOWN"
    slips["sv"] = sv
    return slips[["time", "sv", "mw_value", "mw_mean", "mw_jump"]].reset_index(drop=True)
```

- [ ] **Step 4: 运行测试 — 应通过**

```bash
python -m pytest tests/test_detector.py -v
```

Expected: 6 passed (3 GF + 3 MW)

- [ ] **Step 5: Commit**

```bash
git add core/detector.py tests/test_detector.py
git commit -m "feat: add MW (Melbourne-Wübbena) cycle slip detection"
```

---

### Task 5: 周跳探测 — 合并与主接口

**Files:**
- Modify: `core/detector.py` — 添加 `detect_cycle_slips` 函数
- Modify: `tests/test_detector.py` — 添加合并检测测试

- [ ] **Step 1: 更新 imports，然后追加合并检测测试**

将 test_detector.py 顶部的 import 行改为:

```python
from core.detector import detect_gf, detect_mw, detect_cycle_slips, F1, F2, WL1, WL2
from tests.conftest import make_clean_data, make_slip_data
```

然后在文件末尾追加:

在 tests/test_detector.py 末尾追加:

```python
def test_detect_cycle_slips_combined(sample_data_with_slip):
    """合并检测: GF + MW 结果取并集"""
    result = detect_cycle_slips(sample_data_with_slip)
    assert len(result) >= 1
    assert "time" in result.columns
    assert "sv" in result.columns
    assert "gf_jump" in result.columns
    assert "mw_jump" in result.columns


def test_detect_cycle_slips_multi_satellite():
    """多卫星数据: 每个卫星独立检测"""
    df = pd.concat(
        [make_clean_data(), make_clean_data().assign(sv="G02")],
        ignore_index=True,
    )
    # Introduce slip on G02 only
    mask = (df["sv"] == "G02") & (df.index >= 50)
    df.loc[mask, "L1"] += 10.0
    result = detect_cycle_slips(df, gf_threshold=0.05)
    assert len(result) >= 1
    assert all(result["sv"] == "G02")  # slips only on G02


def test_detect_cycle_slips_empty_on_clean_data(sample_rinex_data):
    """干净数据: 无周跳检出"""
    result = detect_cycle_slips(sample_rinex_data)
    assert len(result) == 0
```

- [ ] **Step 2: 运行测试 — 确认失败**

```bash
python -m pytest tests/test_detector.py::test_detect_cycle_slips_combined -v
```

Expected: FAIL (ImportError)

- [ ] **Step 3: 在 core/detector.py 末尾添加合并检测主函数**

在文件末尾追加:

```python
def detect_cycle_slips(
    df: pd.DataFrame,
    sv_col: str = "sv",
    gf_threshold: float = 0.05,
    mw_window: int = 30,
    mw_threshold: float = 1.0,
) -> pd.DataFrame:
    """对 RINEX 解析后的观测数据执行 TurboEdit 周跳探测。

    对每个卫星分别运行 GF 和 MW 检测，结果取并集去重。

    Args:
        df: 观测数据，需含 time, sv, L1, L2, P1, P2 列
        sv_col: 卫星标识列名
        gf_threshold: GF 检测阈值（周）
        mw_window: MW 滑动窗口大小（历元数）
        mw_threshold: MW 检测阈值（宽巷周数）

    Returns:
        周跳列表 DataFrame，列: sv, time, gf_jump, mw_jump
    """
    all_slips = []

    for sv, group in df.groupby(sv_col):
        gf_slips = detect_gf(group, threshold=gf_threshold)
        mw_slips = detect_mw(group, window=mw_window, threshold=mw_threshold)

        merged = pd.merge(
            gf_slips[["time", "sv", "gf_jump"]],
            mw_slips[["time", "sv", "mw_jump"]],
            on=["time", "sv"],
            how="outer",
        )
        all_slips.append(merged)

    if not all_slips:
        return pd.DataFrame(columns=["sv", "time", "gf_jump", "mw_jump"])

    result = pd.concat(all_slips, ignore_index=True)
    result = result.sort_values(["sv", "time"]).reset_index(drop=True)
    result["gf_jump"] = result["gf_jump"].fillna("-")
    result["mw_jump"] = result["mw_jump"].fillna("-")
    return result[["sv", "time", "gf_jump", "mw_jump"]]
```

- [ ] **Step 4: 运行完整测试套件**

```bash
python -m pytest tests/test_detector.py -v
```

Expected: 9 passed (3 GF + 3 MW + 3 combined)

- [ ] **Step 5: Commit**

```bash
git add core/detector.py tests/test_detector.py
git commit -m "feat: add unified cycle slip detection with GF+MW merge"
```

---

### Task 6: UI — 侧边栏

**Files:**
- Create: `ui/sidebar.py`

- [ ] **Step 1: 实现 ui/sidebar.py**

```python
"""Streamlit 侧边栏组件：文件上传和参数配置。"""

import streamlit as st


def render_sidebar():
    """渲染侧边栏，返回上传的文件对象和参数配置。"""
    st.sidebar.title("🔭 周跳探测小程序")

    st.sidebar.header("📁 数据输入")
    uploaded_file = st.sidebar.file_uploader(
        "上传 RINEX 观测文件",
        type=["obs", "rnx", "o", "rnx.gz", "crx", "crx.gz"],
        help="支持 RINEX 2.x 和 3.x 观测文件",
    )

    st.sidebar.header("⚙️ 检测参数")
    gf_threshold = st.sidebar.slider(
        "GF 检测阈值（周）",
        min_value=0.01,
        max_value=1.0,
        value=0.05,
        step=0.01,
        help="历元间 GF 差分的阈值，值越小越敏感",
    )
    mw_window = st.sidebar.slider(
        "MW 滑动窗口（历元数）",
        min_value=5,
        max_value=100,
        value=30,
        step=5,
        help="MW 滑动平均的窗口大小",
    )
    mw_threshold = st.sidebar.slider(
        "MW 检测阈值（周）",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.1,
        help="MW 值与滑动均值的偏差阈值",
    )

    st.sidebar.header("ℹ️ 关于")
    st.sidebar.markdown(
        """
        **TurboEdit 算法**
        - **GF 组合**: Φ₁−Φ₂，对小周跳敏感
        - **MW 组合**: 宽巷相位减窄巷伪距，探测大周跳
        - 两种方法互补，取并集输出结果
        """
    )

    return {
        "uploaded_file": uploaded_file,
        "gf_threshold": gf_threshold,
        "mw_window": mw_window,
        "mw_threshold": mw_threshold,
    }
```

- [ ] **Step 2: Commit**

```bash
git add ui/sidebar.py
git commit -m "feat: add sidebar UI with file upload and parameter controls"
```

---

### Task 7: UI — 结果表格

**Files:**
- Create: `ui/results.py`

- [ ] **Step 1: 实现 ui/results.py**

```python
"""Streamlit 结果展示组件：周跳表格和 CSV 导出。"""

import streamlit as st
import pandas as pd


def render_results(slips: pd.DataFrame):
    """展示周跳检测结果表格并提供 CSV 导出。

    Args:
        slips: detect_cycle_slips 返回的周跳 DataFrame
    """
    st.subheader("📋 周跳检测结果")

    if slips.empty:
        st.success("未检测到周跳，观测数据质量良好。")
        return

    st.markdown(f"共检测到 **{len(slips)}** 处周跳")

    display_df = slips.copy()
    if "gf_jump" in display_df.columns:
        def fmt_gf(val):
            if val == "-":
                return "-"
            return f"{float(val):.3f}"
        display_df["GF跳变(周)"] = display_df["gf_jump"].apply(fmt_gf)
    if "mw_jump" in display_df.columns:
        def fmt_mw(val):
            if val == "-":
                return "-"
            return f"{float(val):.3f}"
        display_df["MW跳变(周)"] = display_df["mw_jump"].apply(fmt_mw)

    show_cols = ["sv", "time"]
    if "GF跳变(周)" in display_df.columns:
        show_cols.append("GF跳变(周)")
    if "MW跳变(周)" in display_df.columns:
        show_cols.append("MW跳变(周)")

    st.dataframe(
        display_df[show_cols].rename(columns={"sv": "卫星", "time": "时间"}),
        use_container_width=True,
        hide_index=True,
    )

    csv = slips.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 导出 CSV",
        data=csv,
        file_name="cycle_slips.csv",
        mime="text/csv",
    )
```

- [ ] **Step 2: Commit**

```bash
git add ui/results.py
git commit -m "feat: add results table UI with CSV export"
```

---

### Task 8: UI — 可视化图表

**Files:**
- Create: `ui/charts.py`

- [ ] **Step 1: 实现 ui/charts.py**

```python
"""Streamlit 可视化组件：GF/MW 时序图和周跳标注。"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from core.detector import F1, F2, WL1, WL2, detect_gf


def render_charts(df: pd.DataFrame, slips: pd.DataFrame, params: dict):
    """渲染 GF/MW 组合时序图，周跳点红色标注。

    Args:
        df: 观测数据 DataFrame
        slips: 检测到的周跳列表
        params: 检测参数字典（含 gf_threshold, mw_window, mw_threshold）
    """
    st.subheader("📈 可视化分析")

    satellites = sorted(df["sv"].unique())
    selected_sv = st.selectbox("选择卫星", satellites)

    sv_data = df[df["sv"] == selected_sv].sort_values("time").copy()
    sv_slips = slips[slips["sv"] == selected_sv] if not slips.empty else pd.DataFrame()

    gf_threshold = params.get("gf_threshold", 0.05)

    # GF 组合时序图
    fig_gf = go.Figure()
    sv_data["gf_value"] = sv_data["L1"] - sv_data["L2"]
    sv_data["gf_diff"] = sv_data["gf_value"].diff().abs()

    fig_gf.add_trace(go.Scatter(
        x=sv_data["time"],
        y=sv_data["gf_value"],
        mode="lines",
        name="GF 组合",
        line=dict(color="#1f77b4", width=1),
    ))

    if not sv_slips.empty:
        slip_times = sv_slips["time"].tolist()
        slip_vals = sv_data[sv_data["time"].isin(slip_times)]["gf_value"].tolist()
        fig_gf.add_trace(go.Scatter(
            x=slip_times,
            y=slip_vals,
            mode="markers",
            name="周跳点",
            marker=dict(color="red", size=10, symbol="x"),
        ))

    fig_gf.update_layout(
        title=f"{selected_sv} — GF 组合时序图",
        xaxis_title="时间",
        yaxis_title="GF (周)",
        height=400,
        hovermode="x",
    )
    st.plotly_chart(fig_gf, use_container_width=True)

    # MW 组合时序图
    mw_window = params.get("mw_window", 30)
    mw_threshold = params.get("mw_threshold", 1.0)

    sv_data["mw_value"] = (sv_data["L1"] - sv_data["L2"]) - (F1 - F2) / (F1 + F2) * (
        sv_data["P1"] / WL1 + sv_data["P2"] / WL2
    )
    sv_data["mw_mean"] = sv_data["mw_value"].rolling(
        window=mw_window, min_periods=mw_window
    ).mean()

    fig_mw = go.Figure()
    fig_mw.add_trace(go.Scatter(
        x=sv_data["time"],
        y=sv_data["mw_value"],
        mode="lines",
        name="MW 组合",
        line=dict(color="#2ca02c", width=1),
    ))
    fig_mw.add_trace(go.Scatter(
        x=sv_data["time"],
        y=sv_data["mw_mean"],
        mode="lines",
        name=f"滑动均值 (窗口={mw_window})",
        line=dict(color="#ff7f0e", width=1.5, dash="dash"),
    ))
    fig_mw.add_trace(go.Scatter(
        x=sv_data["time"],
        y=sv_data["mw_mean"] + mw_threshold,
        mode="lines",
        name=f"阈值上界",
        line=dict(color="red", width=0.5, dash="dot"),
        showlegend=True,
    ))
    fig_mw.add_trace(go.Scatter(
        x=sv_data["time"],
        y=sv_data["mw_mean"] - mw_threshold,
        mode="lines",
        name=f"阈值下界",
        line=dict(color="red", width=0.5, dash="dot"),
        showlegend=True,
    ))

    if not sv_slips.empty and "mw_jump" in sv_slips.columns:
        mw_slip_times = sv_slips[sv_slips["mw_jump"] != "-"]["time"].tolist()
        mw_slip_vals = sv_data[sv_data["time"].isin(mw_slip_times)]["mw_value"].tolist()
        fig_mw.add_trace(go.Scatter(
            x=mw_slip_times,
            y=mw_slip_vals,
            mode="markers",
            name="周跳点",
            marker=dict(color="red", size=10, symbol="x"),
        ))

    fig_mw.update_layout(
        title=f"{selected_sv} — MW 组合时序图",
        xaxis_title="时间",
        yaxis_title="MW (宽巷周数)",
        height=400,
        hovermode="x",
    )
    st.plotly_chart(fig_mw, use_container_width=True)
```

- [ ] **Step 2: Commit**

```bash
git add ui/charts.py
git commit -m "feat: add visualization charts with GF/MW timeseries and slip markers"
```

---

### Task 9: 主入口 — app.py

**Files:**
- Create: `app.py`

- [ ] **Step 1: 实现 app.py**

```python
"""周跳探测小程序 — Streamlit 主入口。

使用: streamlit run app.py
"""

import streamlit as st
import tempfile
import os

from core.rinex_reader import parse_rinex
from core.detector import detect_cycle_slips
from ui.sidebar import render_sidebar
from ui.results import render_results
from ui.charts import render_charts


st.set_page_config(
    page_title="周跳探测小程序",
    page_icon="🔭",
    layout="wide",
)

params = render_sidebar()

if params["uploaded_file"] is None:
    st.title("🔭 周跳探测小程序")
    st.markdown(
        """
        ### 使用说明
        1. 在左侧上传 RINEX 双频观测文件
        2. 调整检测参数（或使用默认值）
        3. 查看周跳检测结果和可视化图表
        4. 导出 CSV 结果报告

        ### 支持的数据
        - RINEX 2.x / 3.x 观测文件
        - 双频观测值（L1/L2 + P1/P2）
        - GPS / BDS / Galileo / GLONASS
        """
    )
    st.stop()

with tempfile.NamedTemporaryFile(suffix=".rnx", delete=False) as tmp:
    tmp.write(params["uploaded_file"].read())
    tmp_path = tmp.name

try:
    with st.spinner("正在解析 RINEX 文件..."):
        df = parse_rinex(tmp_path)

    with st.spinner("正在检测周跳..."):
        slips = detect_cycle_slips(
            df,
            gf_threshold=params["gf_threshold"],
            mw_window=params["mw_window"],
            mw_threshold=params["mw_threshold"],
        )

    tab1, tab2 = st.tabs(["📋 周跳结果", "📈 可视化分析"])

    with tab1:
        render_results(slips)

    with tab2:
        if not df.empty:
            render_charts(df, slips, params)
        else:
            st.warning("无法加载观测数据。")

finally:
    os.unlink(tmp_path)
```

- [ ] **Step 2: 安装 georinex（如需额外组件）**

```bash
pip install georinex
```

- [ ] **Step 3: 运行并验证**

```bash
cd "/Users/chenjunbin/Desktop/周跳探测小程序"
streamlit run app.py
```

手动测试：上传一个 RINEX 文件（如果有），验证：
- 文件成功解析
- 周跳结果表格显示正确
- 可视化图表正常渲染
- CSV 导出按钮可用
- 参数滑块能调整检测灵敏度

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add main Streamlit app entry point"
```

---

### Task 10: 打包脚本

**Files:**
- Create: `build.py`

- [ ] **Step 1: 实现 build.py**

```python
"""PyInstaller 打包脚本。

用法:
    python build.py          # 正常打包
    python build.py --run     # 打包后直接运行
"""

import subprocess
import sys
import platform
import os


def build():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    icon_flag = []

    system = platform.system()
    if system == "Windows":
        sep = ";"
        ext = ".exe"
        name = "周跳探测"
    else:
        sep = ":"
        ext = ""
        name = "周跳探测"

    add_data_pairs = []

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", name,
        "--add-data", f"core{os.sep}core",
        "--add-data", f"ui{os.sep}ui",
        "--hidden-import", "georinex",
        "--hidden-import", "plotly.express",
        "--hidden-import", "pandas",
        "--hidden-import", "streamlit",
        "--collect-all", "streamlit",
        "--collect-all", "plotly",
        str(os.path.join(project_dir, "run_app.py")),
    ]

    print(f">>> {' '.join(cmd)}")
    subprocess.check_call(cmd)
    print(f"\n=== 打包完成 ===")
    print(f"可执行文件: dist/{name}{ext}")


if __name__ == "__main__":
    build()
```

- [ ] **Step 2: 创建启动包装器 run_app.py**

```python
"""PyInstaller 可执行文件的启动包装器。

双击运行后启动 Streamlit 服务器并自动打开浏览器。
"""

import sys
import os
import subprocess
import webbrowser
import time
import threading


def open_browser(port):
    time.sleep(1.5)
    webbrowser.open(f"http://localhost:{port}")


def main():
    port = 8501

    if getattr(sys, "frozen", False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    app_path = os.path.join(base_dir, "app.py")

    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        app_path,
        "--server.port", str(port),
        "--server.headless", "true",
        "--browser.serverAddress", "localhost",
    ])


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 运行打包**

```bash
cd "/Users/chenjunbin/Desktop/周跳探测小程序"
python build.py
```

Expected: dist/ 目录下生成 `周跳探测`（macOS）或 `周跳探测.exe`（Windows）

- [ ] **Step 4: 验证可执行文件**

```bash
# macOS
./dist/周跳探测
# 验证: 浏览器自动打开到 http://localhost:8501
```

- [ ] **Step 5: Commit**

```bash
git add build.py run_app.py
git commit -m "feat: add PyInstaller build script"
```

---

### Task 11: 全流程集成测试

**Files:**
- Modify: `tests/test_detector.py` — 追加端到端测试

- [ ] **Step 1: 添加端到端集成测试**

在 test_detector.py 末尾追加:

```python
def test_end_to_end_pipeline():
    """端到端测试: 解析 → 检测 → 结果验证"""
    from core.rinex_reader import extract_observations
    from core.detector import detect_cycle_slips

    np.random.seed(42)
    n = 120
    t = pd.date_range("2024-01-01 00:00:00", periods=n, freq="30s")

    L1 = np.cumsum(np.random.randn(n) * 0.005) + 1e6
    L2 = np.cumsum(np.random.randn(n) * 0.005) + 8e5

    # 注入两个周跳
    L1[30:40] += 3.0
    L2[30:40] += 3.0
    L1[80:90] += 8.0
    L2[80:90] += 8.0

    P1 = 21000000.0 + np.random.randn(n) * 0.3
    P2 = 21000000.0 + np.random.randn(n) * 0.3

    df = pd.DataFrame({
        "time": t,
        "sv": "G01",
        "L1": L1,
        "L2": L2,
        "P1": P1,
        "P2": P2,
    })

    result = detect_cycle_slips(df, gf_threshold=0.05, mw_window=20, mw_threshold=1.0)
    assert len(result) >= 2  # should detect both slip events
```

- [ ] **Step 2: 运行完整测试套件**

```bash
python -m pytest tests/ -v
```

Expected: 所有测试通过 (约 12 个测试)

- [ ] **Step 3: Commit**

```bash
git add tests/test_detector.py
git commit -m "test: add end-to-end integration test"
```
