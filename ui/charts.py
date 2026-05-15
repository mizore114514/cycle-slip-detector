"""Streamlit 可视化组件：GF/MW 时序图和周跳标注（暗色主题）。"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from core.detector import F1, F2, WL1, WL2

DARK_TEMPLATE = {
    "bg": "#161B22",
    "grid": "#30363D",
    "font": "#E6EDF3",
    "line_blue": "#58A6FF",
    "line_green": "#00D4AA",
    "line_orange": "#F78166",
    "slip_marker": "#F78166",
}


def _dark_layout(fig, title, xaxis_title, yaxis_title, height=400):
    """为 Plotly 图表应用暗色主题。"""
    fig.update_layout(
        title=dict(text=title, font=dict(color=DARK_TEMPLATE["font"], size=16)),
        xaxis=dict(
            title=xaxis_title,
            gridcolor=DARK_TEMPLATE["grid"],
            zerolinecolor=DARK_TEMPLATE["grid"],
            title_font=dict(color=DARK_TEMPLATE["font"]),
            tickfont=dict(color=DARK_TEMPLATE["font"]),
        ),
        yaxis=dict(
            title=yaxis_title,
            gridcolor=DARK_TEMPLATE["grid"],
            zerolinecolor=DARK_TEMPLATE["grid"],
            title_font=dict(color=DARK_TEMPLATE["font"]),
            tickfont=dict(color=DARK_TEMPLATE["font"]),
        ),
        plot_bgcolor=DARK_TEMPLATE["bg"],
        paper_bgcolor=DARK_TEMPLATE["bg"],
        height=height,
        hovermode="x",
        legend=dict(font=dict(color=DARK_TEMPLATE["font"])),
        margin=dict(t=40, b=20, l=20, r=20),
    )


def render_charts(df: pd.DataFrame, slips: pd.DataFrame, params: dict):
    """渲染 GF/MW 组合时序图，周跳点暖橙标注。

    Args:
        df: 观测数据 DataFrame
        slips: 检测到的周跳列表
        params: 检测参数字典（含 gf_threshold, mw_window, mw_threshold）
    """
    st.markdown(
        '<h3 style="color:#00D4AA;">📈 可视化分析</h3>', unsafe_allow_html=True
    )

    satellites = sorted(df["sv"].unique())
    selected_sv = st.selectbox("选择卫星", satellites)

    sv_data = df[df["sv"] == selected_sv].sort_values("time").copy()
    sv_slips = slips[slips["sv"] == selected_sv] if not slips.empty else pd.DataFrame()

    # ── GF 组合时序图 ──
    fig_gf = go.Figure()
    sv_data["gf_value"] = WL1 * sv_data["L1"] - WL2 * sv_data["L2"]

    fig_gf.add_trace(
        go.Scatter(
            x=sv_data["time"],
            y=sv_data["gf_value"],
            mode="lines",
            name="GF 组合",
            line=dict(color=DARK_TEMPLATE["line_blue"], width=2),
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
                    name="周跳",
                    marker=dict(color=DARK_TEMPLATE["slip_marker"], size=12, symbol="x"),
                )
            )

    _dark_layout(fig_gf, f"{selected_sv} — GF 组合时序图", "时间", "GF (米)")

    st.plotly_chart(fig_gf, use_container_width=True)

    # ── MW 组合时序图 ──
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
            line=dict(color=DARK_TEMPLATE["line_blue"], width=2),
        )
    )
    fig_mw.add_trace(
        go.Scatter(
            x=sv_data["time"],
            y=sv_data["mw_mean"],
            mode="lines",
            name=f"滑动均值 (窗口={mw_window})",
            line=dict(color=DARK_TEMPLATE["line_green"], width=1.5, dash="dash"),
        )
    )
    fig_mw.add_trace(
        go.Scatter(
            x=sv_data["time"],
            y=sv_data["mw_mean"] + mw_threshold,
            mode="lines",
            name="阈值上界",
            line=dict(color=DARK_TEMPLATE["line_orange"], width=0.5, dash="dot"),
        )
    )
    fig_mw.add_trace(
        go.Scatter(
            x=sv_data["time"],
            y=sv_data["mw_mean"] - mw_threshold,
            mode="lines",
            name="阈值下界",
            line=dict(color=DARK_TEMPLATE["line_orange"], width=0.5, dash="dot"),
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
                    name="周跳",
                    marker=dict(color=DARK_TEMPLATE["slip_marker"], size=12, symbol="x"),
                )
            )

    _dark_layout(fig_mw, f"{selected_sv} — MW 组合时序图", "时间", "MW (宽巷周数)")

    st.plotly_chart(fig_mw, use_container_width=True)
