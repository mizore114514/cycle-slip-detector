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
    from ui.css import inject

    inject()

    st.markdown(
        '<div class="hero-title">🔭 周跳探测小程序</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="hero-subtitle">GNSS Cycle Slip Detection · TurboEdit</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div class="step-card">'
            '<div class="step-number">①</div>'
            '<div style="color:#E6EDF3;font-weight:600;">上传文件</div>'
            '<div style="color:#8B949E;font-size:0.85rem;">RINEX 双频观测数据</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="step-card">'
            '<div class="step-number">②</div>'
            '<div style="color:#E6EDF3;font-weight:600;">调整参数</div>'
            '<div style="color:#8B949E;font-size:0.85rem;">GF/MW 检测阈值</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<div class="step-card">'
            '<div class="step-number">③</div>'
            '<div style="color:#E6EDF3;font-weight:600;">查看结果</div>'
            '<div style="color:#8B949E;font-size:0.85rem;">表格 + 可视化 + CSV导出</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(
            '<div class="info-card">'
            '<div class="info-card-icon">🛰️</div>'
            '<div class="info-card-title">多系统支持</div>'
            '<div class="info-card-desc">GPS · BDS · Galileo · GLONASS</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            '<div class="info-card">'
            '<div class="info-card-icon">📄</div>'
            '<div class="info-card-title">RINEX 兼容</div>'
            '<div class="info-card-desc">2.x / 3.x · .obs · .rnx · .crx</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with col_c:
        st.markdown(
            '<div class="info-card">'
            '<div class="info-card-icon">📊</div>'
            '<div class="info-card-title">TurboEdit 算法</div>'
            '<div class="info-card-desc">GF + MW 组合 · 周跳并集检测</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.warning("👈 请在左侧上传 RINEX 双频观测文件以开始分析")
    st.stop()

from ui.css import inject

inject()

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
