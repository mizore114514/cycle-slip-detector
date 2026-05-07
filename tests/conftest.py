import pytest
import numpy as np
import pandas as pd


C = 299792458.0
F1 = 1575.42e6
F2 = 1227.60e6
WL1 = C / F1
WL2 = C / F2


def make_clean_data(n=100):
    """生成模拟双频观测数据: 无周跳，L1/L2 与 P1/P2 量级一致"""
    np.random.seed(42)
    t = pd.date_range("2024-01-01 00:00:00", periods=n, freq="30s")
    rho = 21000000.0 + np.cumsum(np.random.randn(n) * 0.1)
    L1 = rho / WL1 + np.random.randn(n) * 0.002
    L2 = rho / WL2 + np.random.randn(n) * 0.002
    P1 = rho + np.random.randn(n) * 0.1
    P2 = rho + np.random.randn(n) * 0.1
    return pd.DataFrame({"time": t, "sv": "G01", "L1": L1, "L2": L2, "P1": P1, "P2": P2})


def make_slip_data(n=100, slip_idx=50, slip_cycles=5.0):
    """生成包含一个周跳的模拟数据: slip_idx 处 L1 跳变 slip_cycles 周"""
    np.random.seed(42)
    t = pd.date_range("2024-01-01 00:00:00", periods=n, freq="30s")
    rho = 21000000.0 + np.cumsum(np.random.randn(n) * 0.1)
    L1 = rho / WL1 + np.random.randn(n) * 0.002
    L1[slip_idx:] += slip_cycles
    L2 = rho / WL2 + np.random.randn(n) * 0.002
    P1 = rho + np.random.randn(n) * 0.1
    P2 = rho + np.random.randn(n) * 0.1
    return pd.DataFrame({"time": t, "sv": "G01", "L1": L1, "L2": L2, "P1": P1, "P2": P2})


@pytest.fixture
def sample_rinex_data():
    return make_clean_data()


@pytest.fixture
def sample_data_with_slip():
    return make_slip_data()
