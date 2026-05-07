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
WL_WL = C / (F1 - F2)  # 宽巷波长 (~0.862 m)


def detect_gf(df: pd.DataFrame, threshold: float = 0.05) -> pd.DataFrame:
    """使用 GF（Geometry-Free）组合检测周跳。

    GF = λ1·L1 − λ2·L2 (以米为单位，消除几何项和钟差)
    历元间差分超过阈值 → 标记为周跳。

    Args:
        df: 单个卫星的观测数据，需含 L1、L2、time 列 (L1/L2 以周为单位)
        threshold: 历元间 GF 差分的检测阈值（米）

    Returns:
        检测到的周跳列表 DataFrame，列: time, sv, gf_value, gf_diff, gf_jump
    """
    if len(df) < 2:
        return pd.DataFrame(columns=["time", "sv", "gf_value", "gf_diff", "gf_jump"])

    data = df.sort_values("time").copy()
    data["gf_value"] = WL1 * data["L1"] - WL2 * data["L2"]
    data["gf_diff"] = data["gf_value"].diff()
    slips = data[np.abs(data["gf_diff"]) > threshold].copy()

    if len(slips) == 0:
        return pd.DataFrame(columns=["time", "sv", "gf_value", "gf_diff", "gf_jump"])

    slips["gf_jump"] = slips["gf_diff"]
    sv = df["sv"].iloc[0] if "sv" in df.columns else "UNKNOWN"
    slips["sv"] = sv
    return slips[["time", "sv", "gf_value", "gf_diff", "gf_jump"]].reset_index(drop=True)


def detect_mw(
    df: pd.DataFrame, window: int = 30, threshold: float = 1.0
) -> pd.DataFrame:
    """使用 MW（Melbourne-Wübbena）组合检测周跳。

    NWL = (f1·L1−f2·L2)/(f1−f2) − (f1·P1+f2·P2)/((f1+f2)·λWL)  [宽巷周数]
    滑动窗口均值与当前值差超过阈值 → 标记为周跳。

    Args:
        df: 单个卫星的观测数据，需含 L1、L2、P1、P2、time 列 (L用周, P用米)
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


def detect_cycle_slips(
    df: pd.DataFrame,
    gf_threshold: float = 0.05,
    mw_window: int = 30,
    mw_threshold: float = 1.0,
) -> pd.DataFrame:
    """对 RINEX 解析后的观测数据执行 TurboEdit 周跳探测。

    对每个卫星分别运行 GF 和 MW 检测，结果取并集去重。

    Args:
        df: 观测数据，需含 time, sv, L1, L2, P1, P2 列
        gf_threshold: GF 检测阈值（米）
        mw_window: MW 滑动窗口大小（历元数）
        mw_threshold: MW 检测阈值（宽巷周数）

    Returns:
        周跳列表 DataFrame，列: sv, time, gf_jump, mw_jump
    """
    all_slips = []

    for sv, group in df.groupby("sv"):
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
