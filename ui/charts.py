"""Streamlit 可视化组件：GF/MW 时序图和周跳标注。"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from core.detector import F1, F2, WL1, WL2


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

    # GF 组合时序图
    fig_gf = go.Figure()
    sv_data["gf_value"] = WL1 * sv_data["L1"] - WL2 * sv_data["L2"]

    fig_gf.add_trace(
        go.Scatter(
            x=sv_data["time"],
            y=sv_data["gf_value"],
            mode="lines",
            name="GF 组合",
            line=dict(color="#1f77b4", width=1),
        )
    )

    if not sv_slips.empty and "gf_jump" in sv_slips.columns:
        gf_slips = sv_slips[sv_slips["gf_jump"] != "-"]
        if not gf_slips.empty:
            slip_times = gf_slips["time"].tolist()
            slip_vals = sv_data[sv_data["time"].isin(slip_times)]["gf_value"].tolist()
            fig_gf.add_trace(
                go.Scatter(
                    x=slip_times,
                    y=slip_vals,
                    mode="markers",
                    name="周跳点",
                    marker=dict(color="red", size=10, symbol="x"),
                )
            )

    fig_gf.update_layout(
        title=f"{selected_sv} — GF 组合时序图",
        xaxis_title="时间",
        yaxis_title="GF (米)",
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
    sv_data["mw_mean"] = (
        sv_data["mw_value"].rolling(window=mw_window, min_periods=mw_window).mean()
    )

    fig_mw = go.Figure()
    fig_mw.add_trace(
        go.Scatter(
            x=sv_data["time"],
            y=sv_data["mw_value"],
            mode="lines",
            name="MW 组合",
            line=dict(color="#2ca02c", width=1),
        )
    )
    fig_mw.add_trace(
        go.Scatter(
            x=sv_data["time"],
            y=sv_data["mw_mean"],
            mode="lines",
            name=f"滑动均值 (窗口={mw_window})",
            line=dict(color="#ff7f0e", width=1.5, dash="dash"),
        )
    )
    fig_mw.add_trace(
        go.Scatter(
            x=sv_data["time"],
            y=sv_data["mw_mean"] + mw_threshold,
            mode="lines",
            name="阈值上界",
            line=dict(color="red", width=0.5, dash="dot"),
            showlegend=True,
        )
    )
    fig_mw.add_trace(
        go.Scatter(
            x=sv_data["time"],
            y=sv_data["mw_mean"] - mw_threshold,
            mode="lines",
            name="阈值下界",
            line=dict(color="red", width=0.5, dash="dot"),
            showlegend=True,
        )
    )

    if not sv_slips.empty and "mw_jump" in sv_slips.columns:
        mw_slips = sv_slips[sv_slips["mw_jump"] != "-"]
        if not mw_slips.empty:
            mw_slip_times = mw_slips["time"].tolist()
            mw_slip_vals = (
                sv_data[sv_data["time"].isin(mw_slip_times)]["mw_value"].tolist()
            )
            fig_mw.add_trace(
                go.Scatter(
                    x=mw_slip_times,
                    y=mw_slip_vals,
                    mode="markers",
                    name="周跳点",
                    marker=dict(color="red", size=10, symbol="x"),
                )
            )

    fig_mw.update_layout(
        title=f"{selected_sv} — MW 组合时序图",
        xaxis_title="时间",
        yaxis_title="MW (宽巷周数)",
        height=400,
        hovermode="x",
    )
    st.plotly_chart(fig_mw, use_container_width=True)
