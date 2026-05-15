"""Streamlit 侧边栏组件：文件上传和参数配置。"""

import streamlit as st


def render_sidebar():
    """渲染侧边栏，返回上传的文件对象和参数配置。"""
    st.sidebar.markdown(
        """
        <div style="font-size:1.3rem;font-weight:700;color:#00D4AA;margin-bottom:0;">
            🔭 周跳探测小程序
        </div>
        <div style="font-size:0.8rem;color:#8B949E;margin-bottom:16px;">
            TurboEdit 实时探测
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        '<div class="sidebar-section-title">📁 数据输入</div>', unsafe_allow_html=True
    )
    uploaded_file = st.sidebar.file_uploader(
        "上传 RINEX 观测文件",
        type=["obs", "rnx", "o", "rnx.gz", "crx", "crx.gz"],
        help="支持 RINEX 2.x 和 3.x 观测文件",
    )

    st.sidebar.markdown(
        '<div class="sidebar-section-title">⚙️ 检测参数</div>', unsafe_allow_html=True
    )

    gf_threshold = st.sidebar.slider(
        "GF 检测阈值（米）",
        min_value=0.01,
        max_value=1.0,
        value=0.05,
        step=0.01,
        help="历元间 GF 差分的阈值，值越小越敏感",
    )
    st.sidebar.caption(f"当前值：**{gf_threshold:.2f}** 米")

    mw_window = st.sidebar.slider(
        "MW 滑动窗口（历元数）",
        min_value=5,
        max_value=100,
        value=30,
        step=5,
        help="MW 滑动平均的窗口大小",
    )
    st.sidebar.caption(f"当前值：**{mw_window}** 历元")

    mw_threshold = st.sidebar.slider(
        "MW 检测阈值（周）",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.1,
        help="MW 值与滑动均值的偏差阈值",
    )
    st.sidebar.caption(f"当前值：**{mw_threshold:.1f}** 周")

    st.sidebar.markdown(
        '<div class="sidebar-section-title">ℹ️ 关于</div>', unsafe_allow_html=True
    )
    st.sidebar.markdown(
        """
        <div style="background:#161B22;border:1px solid #30363D;border-radius:8px;
        padding:12px;font-size:0.85rem;color:#E6EDF3;margin-top:8px;">
        <div style="color:#00D4AA;font-weight:600;margin-bottom:6px;">TurboEdit 算法</div>
        <span style="color:#58A6FF;">GF</span> = λ₁·L₁ − λ₂·L₂（米）<br>
        <span style="color:#8B949E;">小周跳敏感，消除几何项和钟差</span><br><br>
        <span style="color:#58A6FF;">MW</span> = 宽巷相位 − 窄巷伪距（周）<br>
        <span style="color:#8B949E;">消除几何项、电离层和钟差，探测大周跳</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return {
        "uploaded_file": uploaded_file,
        "gf_threshold": gf_threshold,
        "mw_window": mw_window,
        "mw_threshold": mw_threshold,
    }
