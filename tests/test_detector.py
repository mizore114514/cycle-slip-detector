import pytest
import pandas as pd
import numpy as np
from core.detector import detect_gf, detect_mw, detect_cycle_slips, F1, F2, WL1, WL2, C, WL_WL
from tests.conftest import make_clean_data, make_slip_data


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
    assert abs(result.iloc[0]["gf_jump"]) > 0.9  # 5-cycle slip * WL1 ≈ 0.95m


def test_mw_no_slip(sample_rinex_data):
    """无周跳数据: MW 检测应返回空结果"""
    result = detect_mw(sample_rinex_data, window=30, threshold=1.0)
    assert len(result) == 0


def test_mw_with_slip(sample_data_with_slip):
    """有周跳数据: MW 应检测到异常"""
    result = detect_mw(sample_data_with_slip, window=5, threshold=1.0)
    assert len(result) >= 1


def test_mw_values_reasonable():
    """验证 MW 组合值在合理范围内（宽巷周数标准差应 < 5 周）"""
    np.random.seed(123)
    n = 200
    t = pd.date_range("2024-01-01", periods=n, freq="30s")
    rho = 21000000.0 + np.cumsum(np.random.randn(n) * 0.1)
    df = pd.DataFrame({
        "time": t,
        "sv": "G01",
        "L1": rho / WL1 + np.random.randn(n) * 0.01,
        "L2": rho / WL2 + np.random.randn(n) * 0.01,
        "P1": rho + np.random.randn(n) * 0.5,
        "P2": rho + np.random.randn(n) * 0.5,
    })
    df = df.sort_values("time")
    df["mw_value"] = (df["L1"] - df["L2"]) - (F1 - F2) / (F1 + F2) * (
        df["P1"] / WL1 + df["P2"] / WL2
    )
    assert df["mw_value"].std() < 5.0


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
    mask = (df["sv"] == "G02") & (df.groupby("sv").cumcount() >= 50)
    df.loc[mask, "L1"] += 10.0
    result = detect_cycle_slips(df, gf_threshold=0.05)
    assert len(result) >= 1
    assert all(result["sv"] == "G02")


def test_detect_cycle_slips_empty_on_clean_data(sample_rinex_data):
    """干净数据: 无周跳检出"""
    result = detect_cycle_slips(sample_rinex_data)
    assert len(result) == 0


def test_end_to_end_pipeline():
    """端到端测试: 生成数据 → 提取观测 → 检测周跳 → 验证"""
    from core.rinex_reader import extract_observations

    np.random.seed(42)
    n = 120
    t = pd.date_range("2024-01-01 00:00:00", periods=n, freq="30s")
    rho = 21000000.0 + np.cumsum(np.random.randn(n) * 0.05)

    L1 = rho / WL1 + np.random.randn(n) * 0.002
    L2 = rho / WL2 + np.random.randn(n) * 0.002
    P1 = rho + np.random.randn(n) * 0.1
    P2 = rho + np.random.randn(n) * 0.1

    # 注入两个周跳
    L1[30:40] += 3.0
    L2[30:40] += 3.0
    L1[80:90] += 8.0
    L2[80:90] += 8.0

    df = pd.DataFrame({
        "time": t,
        "sv": "G01",
        "L1": L1,
        "L2": L2,
        "P1": P1,
        "P2": P2,
    })

    result = detect_cycle_slips(df, gf_threshold=0.05, mw_window=20, mw_threshold=1.0)
    assert len(result) >= 2


def test_charts_dark_theme():
    """验证 Plotly 图表应用暗色主题配色"""
    from ui.charts import render_charts
    from unittest.mock import MagicMock, patch
    import plotly.graph_objects as go

    np.random.seed(42)
    n = 60
    t = pd.date_range("2024-01-01", periods=n, freq="30s")
    df = pd.DataFrame({
        "time": t,
        "sv": "G01",
        "L1": np.cumsum(np.random.randn(n) * 0.01) + 1e6,
        "L2": np.cumsum(np.random.randn(n) * 0.01) + 8e5,
        "P1": 21000000.0 + np.random.randn(n) * 0.3,
        "P2": 21000000.0 + np.random.randn(n) * 0.3,
    })

    slips_df = pd.DataFrame({
        "sv": ["G01"],
        "time": [df.iloc[30]["time"]],
        "gf_jump": ["5.0"],
        "mw_jump": ["3.0"],
    })

    captured_figs = []

    def fake_selectbox(label, options):
        return "G01"

    def fake_plotly_chart(fig, **kwargs):
        captured_figs.append(fig)

    with patch("streamlit.selectbox", fake_selectbox), \
         patch("streamlit.plotly_chart", fake_plotly_chart), \
         patch("streamlit.subheader"), \
         patch("streamlit.markdown"):
        render_charts(df, slips_df, {})

    assert len(captured_figs) == 2  # GF + MW

    gf_fig = captured_figs[0]
    assert gf_fig.layout.plot_bgcolor == "#161B22"
    gf_line = gf_fig.data[0]
    assert gf_line.line.color == "#58A6FF"

    mw_fig = captured_figs[1]
    assert mw_fig.layout.plot_bgcolor == "#161B22"
