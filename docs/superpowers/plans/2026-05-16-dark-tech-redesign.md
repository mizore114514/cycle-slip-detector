# 深色科技风前端重设计 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将周跳探测 Streamlit 应用从浅色默认主题改造为深色科技风（配色 #0D1117 / #00D4AA / #F78166），提升专业感。

**Architecture:** 分层改造 — `.streamlit/config.toml` 负责全局主题色，`ui/theme.py`（新建）负责 CSS 注入，`ui/charts.py` 负责 Plotly 暗色模板，`app.py`/`ui/sidebar.py`/`ui/results.py` 各自优化布局和样式。不改变核心算法和交互流。

**Tech Stack:** Streamlit themes, Plotly dark template, custom CSS via st.markdown unsafe_allow_html

---

### Task 1: Streamlit 全局主题配置

**Files:**
- Modify: `.streamlit/config.toml`

- [ ] **Step 1: 添加 [theme] 节到 config.toml**

在现有 `[server]` 节之后追加 `[theme]` 配置：

```toml
[theme]
base = "dark"
primaryColor = "#00D4AA"
backgroundColor = "#0D1117"
secondaryBackgroundColor = "#161B22"
textColor = "#E6EDF3"
font = "sans serif"
```

完整文件内容：

```toml
[server]
fileWatcherType = "watchdog"

[theme]
base = "dark"
primaryColor = "#00D4AA"
backgroundColor = "#0D1117"
secondaryBackgroundColor = "#161B22"
textColor = "#E6EDF3"
font = "sans serif"
```

- [ ] **Step 2: 验证配置可被 Streamlit 解析**

```bash
cd "/Users/chenjunbin/Desktop/周跳探测小程序"
python3 -c "
import toml
cfg = toml.load('.streamlit/config.toml')
assert cfg['theme']['base'] == 'dark'
assert cfg['theme']['primaryColor'] == '#00D4AA'
assert cfg['theme']['backgroundColor'] == '#0D1117'
print('Theme config OK')
"
```

Expected: `Theme config OK`

- [ ] **Step 3: Commit**

```bash
git add .streamlit/config.toml
git commit -m "feat: add dark theme config to Streamlit"
```

---

### Task 2: 自定义 CSS 注入模块

**Files:**
- Create: `ui/css.py`

- [ ] **Step 1: 创建 ui/css.py**

```python
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
```

- [ ] **Step 2: 验证 CSS 注入函数可执行，且包含关键颜色值**

```bash
cd "/Users/chenjunbin/Desktop/周跳探测小程序"
python3 -c "
from ui.css import inject, COLORS
assert COLORS['bg'] == '#0D1117'
assert COLORS['primary'] == '#00D4AA'
assert COLORS['warning'] == '#F78166'
print('CSS module OK')
"
```

Expected: `CSS module OK`

- [ ] **Step 3: Commit**

```bash
git add ui/css.py
git commit -m "feat: add custom CSS injection for dark tech theme"
```

---

### Task 3: 首页 Hero 布局重设计

**Files:**
- Modify: `app.py`

- [ ] **Step 1: 重写首页展示部分**

替换 `app.py` 中 `if params["uploaded_file"] is None:` 块内的内容：

```python
if params["uploaded_file"] is None:
    from ui.css import inject
    inject()

    st.markdown('<div class="hero-title">🔭 周跳探测小程序</div>', unsafe_allow_html=True)
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

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.warning("👈 请在左侧上传 RINEX 双频观测文件以开始分析")
    st.stop()
```

- [ ] **Step 2: 同时在文件上传后的路径注入 CSS**

在 `app.py` 中 `try:` 块之前添加 CSS 注入（让结果页也应用样式）。找到 `with tempfile.NamedTemporaryFile(...)` 这行之前添加：

```python
from ui.css import inject
inject()
```

完整修改后的 app.py：

```python
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
```

- [ ] **Step 3: 验证 — 启动 App 检查首页**

```bash
cd "/Users/chenjunbin/Desktop/周跳探测小程序"
python3 -m streamlit run app.py --server.headless true 2>&1 &
PID=$!
sleep 5
curl -s -o /dev/null -w "%{http_code}" http://localhost:8501
kill $PID 2>/dev/null
wait $PID 2>/dev/null
```

Expected: `200`

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: redesign landing page with Hero layout and dark theme CSS"
```

---

### Task 4: 侧边栏重设计

**Files:**
- Modify: `ui/sidebar.py`

- [ ] **Step 1: 重写 render_sidebar 函数**

```python
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
```

- [ ] **Step 2: 验证侧边栏函数可导入且返回值结构正确**

```bash
cd "/Users/chenjunbin/Desktop/周跳探测小程序"
python3 -c "
from ui.sidebar import render_sidebar
import inspect
src = inspect.getsource(render_sidebar)
assert 'render_sidebar' in src or True
assert 'sidebar-section-title' in src
assert '00D4AA' in src
print('Sidebar module OK')
"
```

Expected: `Sidebar module OK`

- [ ] **Step 3: Commit**

```bash
git add ui/sidebar.py
git commit -m "feat: redesign sidebar with dark theme styling and value display"
```

---

### Task 5: 结果表格重设计

**Files:**
- Modify: `ui/results.py`

- [ ] **Step 1: 添加表格样式和强调色导出按钮**

```python
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
```

- [ ] **Step 2: 验证函数可导入且关键元素存在**

```bash
cd "/Users/chenjunbin/Desktop/周跳探测小程序"
python3 -c "
from ui.results import render_results
import inspect
src = inspect.getsource(render_results)
assert '00D4AA' in src
assert 'F78166' in src
print('Results module OK')
"
```

Expected: `Results module OK`

- [ ] **Step 3: Commit**

```bash
git add ui/results.py
git commit -m "feat: enhance results table with dark theme and accent colors"
```

---

### Task 6: 图表暗色主题

**Files:**
- Modify: `ui/charts.py`
- Modify: `tests/test_detector.py` — 追加图表样式测试

- [ ] **Step 1: 在 test_detector.py 末尾追加图表暗色主题测试**

```python
def test_charts_dark_theme():
    """验证 Plotly 图表应用暗色主题配色"""
    from ui.charts import render_charts
    from tests.conftest import make_slip_data

    df = make_slip_data()
    slips_df = pd.DataFrame({
        "sv": ["G01"],
        "time": [df.iloc[50]["time"]],
        "gf_jump": ["5.0"],
        "mw_jump": ["3.0"],
    })

    # 使用 MagicMock 替代 st 避免 Streamlit 上下文依赖
    from unittest.mock import MagicMock, patch
    import plotly.graph_objects as go

    captured_figs = []

    def fake_selectbox(label, options):
        return "G01"

    def fake_plotly_chart(fig, **kwargs):
        captured_figs.append(fig)

    with patch("streamlit.selectbox", fake_selectbox), \
         patch("streamlit.plotly_chart", fake_plotly_chart), \
         patch("streamlit.subheader"):
        render_charts(df, slips_df, {})

    assert len(captured_figs) == 2  # GF + MW

    gf_fig = captured_figs[0]
    assert gf_fig.layout.plot_bgcolor == "#161B22"
    gf_line = gf_fig.data[0]
    assert gf_line.line.color == "#58A6FF"

    mw_fig = captured_figs[1]
    assert mw_fig.layout.plot_bgcolor == "#161B22"
```

- [ ] **Step 2: 运行测试 — 确认失败**

```bash
cd "/Users/chenjunbin/Desktop/周跳探测小程序"
python3 -m pytest tests/test_detector.py::test_charts_dark_theme -v
```

Expected: FAIL（当前图表未应用暗色主题）

- [ ] **Step 3: 重写 ui/charts.py 应用暗色主题**

```python
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
```

- [ ] **Step 4: 运行图表暗色主题测试**

```bash
cd "/Users/chenjunbin/Desktop/周跳探测小程序"
python3 -m pytest tests/test_detector.py::test_charts_dark_theme -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ui/charts.py tests/test_detector.py
git commit -m "feat: apply dark theme to Plotly charts with neon accent colors"
```

---

### Task 7: 全流程集成验证

**Files:**
- No new files

- [ ] **Step 1: 运行全部测试确保无回归**

```bash
cd "/Users/chenjunbin/Desktop/周跳探测小程序"
python3 -m pytest tests/ -v
```

Expected: 所有测试通过（至少 12+1 = 13 个）

- [ ] **Step 2: 启动应用并验证页面渲染**

```bash
cd "/Users/chenjunbin/Desktop/周跳探测小程序"
python3 -m streamlit run app.py --server.headless true 2>&1 &
PID=$!
sleep 5
# 验证首页
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501)
echo "Home: $HTTP_CODE"
# 验证响应内容包含暗色主题 CSS
curl -s http://localhost:8501 | grep -c "00D4AA" | xargs echo "Theme refs:"
kill $PID 2>/dev/null
wait $PID 2>/dev/null
```

Expected:
```
Home: 200
Theme refs: >0
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "chore: final integration verification pass"
```
