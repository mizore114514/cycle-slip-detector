"""Streamlit 结果展示组件：周跳表格和 CSV 导出。"""

import streamlit as st
import pandas as pd


def render_results(slips: pd.DataFrame):
    """展示周跳检测结果表格并提供 CSV 导出。

    Args:
        slips: detect_cycle_slips 返回的周跳 DataFrame
    """
    st.markdown(
        '<h3 style="color:#00D4AA;">📋 周跳检测结果</h3>', unsafe_allow_html=True
    )

    if slips.empty:
        st.success("未检测到周跳，观测数据质量良好。")
        return

    n_slips = len(slips)
    st.markdown(
        f'共检测到 <span style="color:#F78166;font-weight:700;">{n_slips}</span> 处周跳',
        unsafe_allow_html=True,
    )

    display_df = slips.copy()

    def fmt_gf(val):
        if val == "-":
            return "-"
        return f"{float(val):.3f}"

    display_df["GF跳变(米)"] = display_df["gf_jump"].apply(fmt_gf)

    def fmt_mw(val):
        if val == "-":
            return "-"
        return f"{float(val):.3f}"

    display_df["MW跳变(周)"] = display_df["mw_jump"].apply(fmt_mw)

    st.dataframe(
        display_df[["sv", "time", "GF跳变(米)", "MW跳变(周)"]].rename(
            columns={"sv": "卫星", "time": "时间"}
        ),
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
