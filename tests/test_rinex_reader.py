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
