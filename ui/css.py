"""自定义 CSS 注入模块，用于深度定制 Streamlit 视觉样式。

深色科技风配色方案:
  背景 #0D1117  卡片 #161B22  边框 #30363D
  主强调 #00D4AA（霓虹青）  次强调 #58A6FF（科技蓝）
  警告 #F78166（暖橙）  文字 #E6EDF3 / #8B949E
"""

import streamlit as st

COLORS = {
    "bg": "#0D1117",
    "card": "#161B22",
    "border": "#30363D",
    "primary": "#00D4AA",
    "secondary": "#58A6FF",
    "warning": "#F78166",
    "text": "#E6EDF3",
    "text_muted": "#8B949E",
}


def inject():
    """注入全局自定义 CSS。"""
    css = f"""
    <style>
    /* 全局字体 */
    html, body, [class*="st-"] {{
        font-family: 'SF Mono', 'JetBrains Mono', 'Cascadia Code', ui-monospace, monospace;
    }}

    /* 卡片容器 */
    .custom-card {{
        background: {COLORS["card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 16px;
    }}

    /* 主标题 */
    .hero-title {{
        font-size: 3rem;
        font-weight: 700;
        color: {COLORS["text"]};
        text-align: center;
        margin-bottom: 0;
    }}
    .hero-subtitle {{
        font-size: 1.2rem;
        color: {COLORS["primary"]};
        text-align: center;
        margin-bottom: 32px;
    }}

    /* 步骤卡片 */
    .step-card {{
        background: {COLORS["card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }}
    .step-number {{
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS["primary"]};
    }}

    /* 底部说明卡片 */
    .info-card {{
        background: {COLORS["card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        height: 100%;
    }}
    .info-card-icon {{
        font-size: 1.5rem;
        margin-bottom: 8px;
    }}
    .info-card-title {{
        color: {COLORS["text"]};
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 4px;
    }}
    .info-card-desc {{
        color: {COLORS["text_muted"]};
        font-size: 0.85rem;
    }}

    /* 侧边栏样式 */
    [data-testid="stSidebar"] {{
        background-color: {COLORS["bg"]};
    }}
    .sidebar-section-title {{
        color: {COLORS["text_muted"]};
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 20px;
        margin-bottom: 8px;
        padding-bottom: 4px;
        border-bottom: 1px solid {COLORS["border"]};
    }}

    /* 按钮 */
    .stDownloadButton > button {{
        border: 1px solid {COLORS["primary"]} !important;
        color: {COLORS["primary"]} !important;
        background: transparent !important;
        border-radius: 6px !important;
    }}
    .stDownloadButton > button:hover {{
        background: {COLORS["primary"]} !important;
        color: {COLORS["bg"]} !important;
    }}

    /* 滑块轨道色 */
    [data-testid="stSlider"] [role="slider"] {{
        background: {COLORS["primary"]} !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
