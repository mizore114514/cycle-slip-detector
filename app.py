"""周跳探测小程序 — Streamlit 主入口。

使用: streamlit run app.py
"""

import streamlit as st
import tempfile
import os

from core.rinex_reader import parse_rinex
from core.detector import detect_cycle_slips
from ui.sidebar import render_sidebar
from ui.results import render_results
from ui.charts import render_charts


st.set_page_config(
    page_title="周跳探测小程序",
    page_icon="🔭",
    layout="wide",
)

params = render_sidebar()

if params["uploaded_file"] is None:
    st.title("🔭 周跳探测小程序")
    st.markdown(
        """
        ### 使用说明
        1. 在左侧上传 RINEX 双频观测文件
        2. 调整检测参数（或使用默认值）
        3. 查看周跳检测结果和可视化图表
        4. 导出 CSV 结果报告

        ### 支持的数据
        - RINEX 2.x / 3.x 观测文件
        - 双频观测值（L1/L2 + P1/P2）
        - GPS / BDS / Galileo / GLONASS
        """
    )
    st.stop()

with tempfile.NamedTemporaryFile(suffix=".rnx", delete=False) as tmp:
    tmp.write(params["uploaded_file"].read())
    tmp_path = tmp.name

try:
    with st.spinner("正在解析 RINEX 文件..."):
        df = parse_rinex(tmp_path)

    with st.spinner("正在检测周跳..."):
        slips = detect_cycle_slips(
            df,
            gf_threshold=params["gf_threshold"],
            mw_window=params["mw_window"],
            mw_threshold=params["mw_threshold"],
        )

    tab1, tab2 = st.tabs(["📋 周跳结果", "📈 可视化分析"])

    with tab1:
        render_results(slips)

    with tab2:
        if not df.empty:
            render_charts(df, slips, params)
        else:
            st.warning("无法加载观测数据。")

finally:
    os.unlink(tmp_path)
