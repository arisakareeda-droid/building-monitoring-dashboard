from datetime import datetime
from pathlib import Path
import pandas as pd
import plotly.express as px
from PIL import Image, ImageDraw, ImageOps
import streamlit as st
from streamlit_autorefresh import st_autorefresh


# ==================================================
# ICON SET (เส้นบาง แบบ minimal, ไม่ใช้ emoji)
# ==================================================
ICONS = {
    "records": """<path d="M7 3h7l4 4v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/>
        <path d="M14 3v4h4"/><path d="M9 12h6M9 15.5h6M9 8.5h3"/>""",
    "users": """<circle cx="8.5" cy="8" r="3"/>
        <path d="M2.5 19.5c0-3.3 2.7-6 6-6s6 2.7 6 6"/>
        <circle cx="17" cy="9" r="2.4"/><path d="M15.2 13.3c2.5.4 4.3 2.5 4.3 5.2"/>""",
    "trending": """<path d="M3 17l6-6 4 4 8-8"/><path d="M15 6h6v6"/>""",
    "signal": """<path d="M2 8.5a15 15 0 0 1 20 0"/>
        <path d="M5.5 12a10 10 0 0 1 13 0"/>
        <path d="M9 15.5a5 5 0 0 1 6 0"/><circle cx="12" cy="19" r="1" fill="currentColor" stroke="none"/>""",
    "clock": """<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>""",
    "download": """<path d="M12 3v12"/><path d="M7 11l5 5 5-5"/><path d="M4 19h16"/>""",
}


def icon_svg(name: str, size: int = 18) -> str:
    body = ICONS.get(name, "")
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
        f'stroke-linejoin="round">{body}</svg>'
    )


def make_circular_favicon(path: str, size: int = 256):
    """ครอปรูปให้เป็นวงกลมโปร่งใส ใช้เฉพาะสำหรับ favicon เท่านั้น
    (ไม่กระทบโลโก้ที่แสดงในหน้าเว็บ)"""
    p = Path(path)
    if not p.exists():
        return None
    img = Image.open(p).convert("RGBA")
    img = ImageOps.fit(img, (size, size), Image.LANCZOS, centering=(0.5, 0.5))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    img.putalpha(mask)
    return img


# ==================================================
# PAGE CONFIG
# ==================================================
_FAVICON_PATH = Path(__file__).parent / "favicon.png"
_favicon = (
    make_circular_favicon(str(_FAVICON_PATH)) if _FAVICON_PATH.exists() else "▪"
)

st.set_page_config(
    page_title="Building Monitoring & Analytics Dashboard",
    page_icon=_favicon,
    layout="wide",
)

SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "14FJt332r41O2JvookMlfzIqljBPSJ1wdt08XnnkTl-8/"
    "export?format=csv"
)

# ==================================================
# THEME STATE — โทนสีปรับใหม่ให้ดูพรีเมียมขึ้น (บรอนซ์นวลแทนทองสด)
# ==================================================
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

THEMES = {
    "Light": {
    "bg": "#F7F8FA",
    "surface": "#FFFFFF",
    "border": "#E4E7EC",
    "text": "#101828",
    "subtitle": "#667085",
    "primary": "#0B2545",
    "accent": "#A6803D",
    "sidebar_grad": "linear-gradient(180deg,#0B2545 0%,#061527 100%)",
    "chart_bg": "rgba(0,0,0,0)",
    "chart_grid": "#CBD5E1",    # ปรับเส้นกริดให้เข้มขึ้น (จากเดิม #E4E7EC)
    "chart_font": "#334155",    # ปรับฟอนต์ในกราฟให้เข้มขึ้นเพื่อให้อ่านง่าย
    "plotly_template": "plotly_white",
    "line_color": "#0B2545",
    "marker_color": "#A6803D",
    "area_color": "#2451A6",
    "bar_scale": "Blues",
    "footer_bg": "#FFFFFF",
    "success": "#15803D",
    "danger": "#B42318",
    },
    "Dark": {
        "bg": "#0A0E1A",
        "surface": "#10162A",
        "border": "#212B45",
        "text": "#E7EBF3",
        "subtitle": "#8B96AC",
        "primary": "#6EA8FE",
        "accent": "#D9B871",
        "sidebar_grad": "linear-gradient(180deg,#0A0E1A 0%,#000000 100%)",
        "chart_bg": "rgba(0,0,0,0)",
        "chart_grid": "#212B45",
        "chart_font": "#E7EBF3",
        "plotly_template": "plotly_dark",
        "line_color": "#6EA8FE",
        "marker_color": "#D9B871",
        "area_color": "#3B6FD6",
        "bar_scale": "Blues",
        "footer_bg": "#10162A",
        "success": "#4ADE80",
        "danger": "#F87171",
    },
}


def apply_theme_css(t: dict):
    st.markdown(
        f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet">

    <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        header {{
            background-color: {t['bg']} !important;
            background-image: none !important;
        }}
        header[data-testid="stHeader"] button {{ color: {t['text']} !important; }}

        html, body, p, span, div, label, h1, h2, h3, h4, h5, h6,
        button, input, select, textarea, a {{
            font-family: 'Kanit', sans-serif;
        }}
        
        [data-testid*="Icon"],
        [class*="material-symbols"],
        [class*="material-icon"],
        span[class*="eyeicon"] {{
            font-family: 'Material Symbols Outlined', 'Material Symbols Rounded',
                         'Material Icons', sans-serif !important;
            font-feature-settings: 'liga' !important;
            -webkit-font-feature-settings: 'liga' !important;
        }}
        .mono {{ font-family: 'IBM Plex Mono', monospace; }}

        .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}

        /* ... โค้ดส่วนอื่นๆ ของคุณ ... */

        /* ส่วนที่คุณเพิ่มใหม่ (ผมแก้ไขปีกกาให้แล้ว) */
        [data-testid="stDataFrame"] thead tr th {{
            background-color: {t['bg']} !important;
            color: {t['text']} !important;
            font-weight: 600 !important;
            border-bottom: 2px solid {t['primary']} !important;
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )


def style_chart(fig, t: dict, height=380):
    fig.update_layout(
        template=t["plotly_template"],
        plot_bgcolor=t["chart_bg"],
        paper_bgcolor=t["chart_bg"],
        font=dict(color=t["chart_font"], family="Kanit"),
        xaxis=dict(
            showgrid=True, 
            gridcolor=t["chart_grid"],
            title_font=dict(color=t["text"], size=13),     # ทำให้ชื่อแกน X ชัดขึ้น (สีเดียวกับข้อความปกติ)
            tickfont=dict(color=t["subtitle"], size=11)   # ทำให้ตัวเลข/วันที่บนแกน X ชัดขึ้น
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor=t["chart_grid"],
            title_font=dict(color=t["text"], size=13),     # ทำให้ชื่อแกน Y (เช่น จำนวนผู้อยู่อาศัย) ชัดขึ้น
            tickfont=dict(color=t["subtitle"], size=11)   # ทำให้ตัวเลขสเกลแกน Y ชัดขึ้น
        ),
        margin=dict(t=20, b=20, l=20, r=20),
        height=height,
    )
    return fig


def kpi_card(icon: str, label: str, value: str, delta: str) -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-top">
            <div class="kpi-label">{label}</div>
            <div class="kpi-icon">{icon_svg(icon, 17)}</div>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta">{delta}</div>
    </div>
    """


def section_header(text: str) -> str:
    return f"""
    <div class="section-head">
        <span class="section-bar"></span>
        <span class="section-title">{text}</span>
    </div>
    """


@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    return df


# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    try:
        st.image("Logo-Songkla.png", width=80)
    except Exception:
        pass

    st.markdown(
        "<div style='font-weight:600;font-size:16px;margin-top:10px;'>"
        "Dashboard Controls</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='sidebar-eyebrow'>Display theme</div>", unsafe_allow_html=True
    )
    theme_choice = st.radio(
        "Display theme",
        options=["Light", "Dark"],
        index=0 if st.session_state.theme == "Light" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.theme = theme_choice
    theme = THEMES[theme_choice]

    st.markdown("---")

    st.markdown(
        "<div class='sidebar-eyebrow'>Auto-refresh interval</div>",
        unsafe_allow_html=True,
    )
    refresh_seconds = st.selectbox(
        "Auto-refresh interval",
        options=[10, 30, 60, 120],
        index=1,
        format_func=lambda s: f"{s} s",
        label_visibility="collapsed",
    )

    date_range = None
    st.markdown("<div class='sidebar-eyebrow'>Search</div>", unsafe_allow_html=True)
    search_query = st.text_input(
        "Search", placeholder="Search records...", label_visibility="collapsed"
    )

st_autorefresh(interval=refresh_seconds * 1000, key="auto_refresh")

apply_theme_css(theme)

# ==================================================
# HEADER
# ==================================================
col_logo, col_title, col_status = st.columns([1.2, 5.8, 2])

with col_logo:
    try:
        st.image("logo_proj.png", width=150)
    except Exception:
        pass

with col_title:
    st.markdown(
        """
        <div class="title-main">Building Occupancy &amp; Activity Monitoring Dashboard</div>
        <div class="subtitle-main">ระบบวิเคราะห์ข้อมูลการเข้า-ออกอาคารอัจฉริยะแบบเรียลไทม์ &middot; Faculty of Engineering, Prince of Songkla University</div>
        """,
        unsafe_allow_html=True,
    )

status_placeholder = col_status.empty()

# ==================================================
# LOAD DATA + STATUS
# ==================================================
system_online = True
try:
    df = load_data()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    with st.sidebar:
        if "Date" in df.columns and not df["Date"].isnull().all():
            min_date = df["Date"].min().date()
            max_date = df["Date"].max().date()
            st.markdown(
                "<div class='sidebar-eyebrow'>Date range</div>",
                unsafe_allow_html=True,
            )
            date_range = st.date_input(
                "Date range",
                [min_date, max_date],
                label_visibility="collapsed",
            )
            if len(date_range) == 2:
                df = df[
                    (df["Date"] >= pd.to_datetime(date_range[0]))
                    & (df["Date"] <= pd.to_datetime(date_range[1]))
                ]

        if search_query:
            df = df[
                df.astype(str)
                .apply(lambda x: x.str.contains(search_query, case=False))
                .any(axis=1)
            ]

        st.markdown("---")
        st.markdown(
            f"""<div class="sidebar-meta">
            RECORDS &nbsp; {len(df):,}<br>
            SYNCED &nbsp;&nbsp;&nbsp; {datetime.now().strftime('%H:%M:%S')}
            </div>""",
            unsafe_allow_html=True,
        )

    with status_placeholder:
        st.markdown(
            f"""
            <div class="status-strip" style="justify-content:flex-end;">
                <div class="status-item">
                    <span class="status-online-dot"></span>
                    <span class="status-label">Online</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if df.empty:
        st.warning("No records match the selected filters. Adjust the date range or search term.")
        st.stop()

    # ==================================================
    # LIVE STATUS STRIP
    # ==================================================
    st.markdown(
        f"""
        <div class="status-strip">
            <div class="status-item">{icon_svg('signal', 15)}<span>Data source: Google Sheets</span></div>
            <div class="divider"></div>
            <div class="status-item">{icon_svg('clock', 15)}<span>Last sync {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</span></div>
            <div class="divider"></div>
            <div class="status-item"><span>Refresh every {refresh_seconds}s</span></div>
            <div class="divider"></div>
            <div class="status-item"><span>{len(df):,} records</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ==================================================
    # KPI CARDS
    # ==================================================
    total_records = len(df)
    total_people = (
        int(df["Person Count"].sum())
        if "Person Count" in df.columns
        and pd.api.types.is_numeric_dtype(df["Person Count"])
        else 0
    )
    average_people = (
        round(df["Person Count"].mean(), 2)
        if "Person Count" in df.columns
        and pd.api.types.is_numeric_dtype(df["Person Count"])
        else 0
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            kpi_card("records", "Total Records", f"{total_records:,}", "รายการทั้งหมด"),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            kpi_card("users", "Total Occupancy", f"{total_people:,}", "ยอดสะสมรวม"),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            kpi_card("trending", "Average / Entry", f"{average_people:,}", "ค่าเฉลี่ยต่อรอบ"),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ==================================================
    # CHARTS
    # ==================================================
    if "Date" in df.columns and "Person Count" in df.columns:
        daily = (
            df.groupby("Date")["Person Count"].sum().reset_index().sort_values("Date")
        )

        st.markdown(
            section_header("แนวโน้มการเข้า-ออกอาคารรายวัน — Time Series Analysis"),
            unsafe_allow_html=True,
        )

        line_fig = px.line(
            daily,
            x="Date",
            y="Person Count",
            markers=True,
            color_discrete_sequence=[theme["line_color"]],
            labels={"Date": "วันที่", "Person Count": "จำนวนผู้อยู่อาศัย (คน)"},
        )
        line_fig.update_traces(
            line=dict(width=2.5), marker=dict(size=7, color=theme["marker_color"])
        )
        st.plotly_chart(style_chart(line_fig, theme, 400), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown(
                section_header("สัดส่วนการใช้งานรายวัน — Bar Distribution"),
                unsafe_allow_html=True,
            )
            bar_fig = px.bar(
                daily,
                x="Date",
                y="Person Count",
                color="Person Count",
                color_continuous_scale=theme["bar_scale"],
                labels={"Date": "วันที่", "Person Count": "จำนวนคน"},
            )
            bar_fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(
                style_chart(bar_fig, theme, 350), use_container_width=True
            )

        with col_b:
            st.markdown(
                section_header("ความหนาแน่นสะสม — Cumulative Area Trend"),
                unsafe_allow_html=True,
            )
            area_fig = px.area(
                daily,
                x="Date",
                y="Person Count",
                color_discrete_sequence=[theme["area_color"]],
                labels={"Date": "วันที่", "Person Count": "จำนวนคน"},
            )
            st.plotly_chart(
                style_chart(area_fig, theme, 350), use_container_width=True
            )

    # ==================================================
    # DATA TABLE & EXPORT
    # ==================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        section_header("รายละเอียดข้อมูลดิบ — Raw Data Table"),
        unsafe_allow_html=True,
    )

    with st.expander("Show / hide full data table", expanded=True):
        st.dataframe(df, use_container_width=True, height=400)

    csv_data = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Download full report (.CSV)",
        data=csv_data,
        file_name="Building_Monitoring_Report.csv",
        mime="text/csv",
    )

    # ==================================================
    # FOOTER
    # ==================================================
    st.markdown(
        f"""
        <div class="footer-card">
            <b>Building Monitoring &amp; Analytics Dashboard</b><br>
            Prince of Songkla University &middot; Faculty of Engineering<br>
            <span style="font-size: 12px;">
                Academic Project 2026 &middot; Streamlit &amp; Python &middot; Theme: {theme_choice}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

except Exception as e:
    system_online = False
    with status_placeholder:
        st.markdown(
            f"""
            <div class="status-strip" style="justify-content:flex-end;">
                <div class="status-item">
                    <span class="status-offline-dot"></span>
                    <span class="status-label">Offline</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.error(f"เกิดข้อผิดพลาดในการโหลดหรือประมวลผลข้อมูล: {e}")
    st.info(
        "คำแนะนำ: กรุณาตรวจสอบว่าลิงก์ Google Sheets เปิดแชร์แบบสาธารณะ "
        "(Anyone with the link) และคอลัมน์ในชีทมีชื่อถูกต้องตามที่โปรแกรมต้องการ "
        "(เช่น Date, Person Count)"
    )