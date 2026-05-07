"""Streamlit 侧边栏组件：文件上传和参数配置。"""

import streamlit as st


def render_sidebar():
    """渲染侧边栏，返回上传的文件对象和参数配置。"""
    st.sidebar.title("🔭 周跳探测小程序")

    st.sidebar.header("📁 数据输入")
    uploaded_file = st.sidebar.file_uploader(
        "上传 RINEX 观测文件",
        type=["obs", "rnx", "o", "rnx.gz", "crx", "crx.gz"],
        help="支持 RINEX 2.x 和 3.x 观测文件",
    )

    st.sidebar.header("⚙️ 检测参数")
    gf_threshold = st.sidebar.slider(
        "GF 检测阈值（米）",
        min_value=0.01,
        max_value=1.0,
        value=0.05,
        step=0.01,
        help="历元间 GF 差分的阈值，值越小越敏感",
    )
    mw_window = st.sidebar.slider(
        "MW 滑动窗口（历元数）",
        min_value=5,
        max_value=100,
        value=30,
        step=5,
        help="MW 滑动平均的窗口大小",
    )
    mw_threshold = st.sidebar.slider(
        "MW 检测阈值（周）",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.1,
        help="MW 值与滑动均值的偏差阈值",
    )

    st.sidebar.header("ℹ️ 关于")
    st.sidebar.markdown(
        """
        **TurboEdit 算法**
        - **GF 组合**: λ₁·Φ₁ − λ₂·Φ₂（米），对小周跳敏感
        - **MW 组合**: 宽巷相位减窄巷伪距（周），探测大周跳
        - 两种方法互补，取并集输出结果
        """
    )

    return {
        "uploaded_file": uploaded_file,
        "gf_threshold": gf_threshold,
        "mw_window": mw_window,
        "mw_threshold": mw_threshold,
    }
