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

    available = [c for c in needed if c in result.columns]
    return result[available]
