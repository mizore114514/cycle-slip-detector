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
