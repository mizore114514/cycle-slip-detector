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
