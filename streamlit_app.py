from datetime import datetime
from pathlib import Path
import pandas as pd
import plotly.express as px
from PIL import Image, ImageDraw, ImageOps
import streamlit as st
import streamlit.components.v1 as components


def make_circular_favicon(path: str, size: int = 256):
    """ครอปรูปให้เป็นวงกลมโปร่งใส ใช้เฉพาะสำหรับ favicon เท่านั้น

    (ไม่กระทบโลโก้ที่แสดงในหน้าเว็บ)
    """
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
    make_circular_favicon(str(_FAVICON_PATH))
    if _FAVICON_PATH.exists()
    else "🏢"
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
# THEME STATE
# ==================================================
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

THEMES = {
    "Light": {
        "bg": "#f8fafc",
        "card_bg": "rgba(255,255,255,0.75)",
        "card_border": "#dbe4f0",
        "text": "#1e293b",
        "subtitle": "#475569",
        "primary": "#002D72",
        "accent": "#D4AF37",
        "sidebar_grad": "linear-gradient(180deg,#002D72 0%,#001a41 100%)",
        "chart_bg": "rgba(0,0,0,0)",
        "chart_grid": "#dbe4f0",
        "chart_font": "#1e293b",
        "plotly_template": "plotly_white",
        "line_color": "#002D72",
        "marker_color": "#D4AF37",
        "area_color": "#1d4ed8",
        "bar_scale": "Blues",
        "expander_bg": "#ffffff",
        "table_bg": "#ffffff",
        "footer_bg": "#ffffff",
        "border": "#dbe4f0",
    },
    "Dark": {
        "bg": "#0b1120",
        "card_bg": "rgba(255,255,255,0.06)",
        "card_border": "rgba(255,255,255,0.12)",
        "text": "#e2e8f0",
        "subtitle": "#94a3b8",
        "primary": "#7fa8ff",
        "accent": "#f5cf6b",
        "sidebar_grad": "linear-gradient(180deg,#0b1120 0%,#000000 100%)",
        "chart_bg": "rgba(0,0,0,0)",
        "chart_grid": "#1e293b",
        "chart_font": "#e2e8f0",
        "plotly_template": "plotly_dark",
        "line_color": "#7fa8ff",
        "marker_color": "#f5cf6b",
        "area_color": "#3b82f6",
        "bar_scale": "Blues",
        "expander_bg": "#111827",
        "table_bg": "#111827",
        "footer_bg": "#111827",
        "border": "#1e293b",
    },
}


def apply_theme_css(t: dict):
    components.html(
        """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    """,
        height=0,
    )

    st.markdown(
        f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* เปลี่ยนสีแถบ Header ด้านบนสุดให้เปลี่ยนตามธีม */
    header[data-testid="stHeader"] {{
        background-color: {t['bg']} !important;
    }}

    html, body, [class*="css"] {{
    font-family: 'Kanit', sans-serif !important;
    }}

    .stApp {{
        background-color: {t['bg']};
        color: {t['text']};
    }}

    .title-main{{
        font-size:38px;
        font-weight:700;
        color:{t['primary']};
        line-height:1.2;
    }}

    .subtitle-main{{
        font-size:17px;
        color:{t['subtitle']};
        font-weight:500;
    }}

    /* Glassmorphism KPI cards */
    .kpi-card {{
        background: {t['card_bg']};
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid {t['card_border']};
        border-radius: 18px;
        padding: 22px 24px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        height: 100%;
    }}
    .kpi-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 14px 28px rgba(0,0,0,0.14);
    }}
    .kpi-label {{
        font-size: 15px;
        font-weight: 600;
        color: {t['text']};
        opacity: .85;
        margin-bottom: 8px;
    }}
    .kpi-value {{
        font-size: 32px;
        font-weight: 700;
        color: {t['primary']};
    }}
    .kpi-delta {{
        color: {t['accent']};
        font-weight:600;
    }}

    /* Chart container */
    div[data-testid="stPlotlyChart"] {{
        color:{t['text']};
        background: {t['card_bg']};
        backdrop-filter: blur(10px);
        padding: 18px;
        border-radius: 18px;
        border: 1px solid {t['card_border']};
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: {t['sidebar_grad']};
        border-right: 1px solid rgba(255,255,255,0.08);
    }}
    section[data-testid="stSidebar"] * {{
        color: #f1f5f9 !important;
    }}
    section[data-testid="stSidebar"] .stTextInput input,
    section[data-testid="stSidebar"] .stDateInput input {{
        background-color: rgba(255, 255, 255, 0.1);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
    }}

    /* Status badge */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
    }}
    .status-online {{
        background: rgba(34, 197, 94, 0.15);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.35);
    }}
    .status-offline {{
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.35);
    }}
    .status-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: currentColor;
        box-shadow: 0 0 6px currentColor;
    }}

    /* Footer */
    .footer-card {{
        text-align:center;
        background:{t['footer_bg']};
        color:{t['text']};
        border:1px solid {t['border']};
        }}

    .footer-card b {{
        color: {t['text']};
    }}

    /* Expander fix */
    div[data-testid="stExpander"] {{
        background: {t['expander_bg']};
        border-radius: 14px;
        border: 1px solid {t['border']};
    }}
    
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary * {{
        color: {t['text']} !important;
        fill: {t['text']} !important;
    }}

    div[data-testid="stExpander"] [data-testid="stMarkdownContainer"] p,
    div[data-testid="stExpander"] span,
    div[data-testid="stExpander"] label {{
        color: {t['text']} !important;
    }}

    @media (max-width: 768px) {{
        .title-main {{ font-size: 26px; }}
        .kpi-value {{ font-size: 24px; }}
    }}

    h1,h2,h3,h4,h5,h6{{
    color:{t['text']} !important;
    }}

    label,p,span,div{{
        color:{t['text']};
    }}

    .stMarkdown{{
        color:{t['text']};
    }}

    .stDataFrame{{
        color:{t['text']};
    }}

    .stDownloadButton button{{
        font-family:'Kanit',sans-serif;
        background-color: {t['table_bg']} !important;
        color: {t['text']} !important;
        border: 1px solid {t['border']} !important;
    }}

    .stButton button{{
        font-family:'Kanit',sans-serif;
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
        font=dict(color=t["chart_font"]),
        xaxis=dict(showgrid=True, gridcolor=t["chart_grid"]),
        yaxis=dict(showgrid=True, gridcolor=t["chart_grid"]),
        margin=dict(t=20, b=20, l=20, r=20),
        height=height,
    )
    return fig


def kpi_card(label, value, delta):
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta">{delta}</div>
    </div>
    """


@st.cache_data(ttl=600)
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

    st.markdown("### ⚙️ Dashboard Controls")

    theme_choice = st.radio(
        "🎨 ธีมการแสดงผล",
        options=["Light", "Dark"],
        index=0 if st.session_state.theme == "Light" else 1,
        horizontal=True,
    )
    st.session_state.theme = theme_choice
    theme = THEMES[theme_choice]

    st.markdown("---")

    date_range = None
    search_query = st.text_input(
        "🔍 ค้นหาข้อมูลในระบบ", placeholder="พิมพ์คำค้นหา..."
    )

apply_theme_css(theme)

# ==================================================
# HEADER
# ==================================================
col_logo, col_title, col_status = st.columns([1.2, 5.8, 2])

with col_logo:
    try:
        st.image("logo_proj.png", width=150)
    except Exception:
        st.markdown("<h1>🏢</h1>", unsafe_allow_html=True)

with col_title:
    st.markdown(
        """
        <div class="title-main">Building Occupancy & Activity Monitoring Dashboard</div>
        <div class="subtitle-main">ระบบวิเคราะห์ข้อมูลการเข้า-ออกอาคารอัจฉริยะแบบเรียลไทม์ | Faculty of Engineering, Prince of Songkla University</div>
        """,
        unsafe_allow_html=True,
    )

status_placeholder = col_status.empty()

st.markdown("<br>", unsafe_allow_html=True)

# ==================================================
# LOAD DATA + STATUS
# ==================================================
system_online = True
try:
    df = load_data()

    with status_placeholder:
        st.markdown(
            f"""
            <div class="status-badge status-online">
                <span class="status-dot"></span> Online
            </div>
            """,
            unsafe_allow_html=True,
        )

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    with st.sidebar:
        if "Date" in df.columns and not df["Date"].isnull().all():
            min_date = df["Date"].min().date()
            max_date = df["Date"].max().date()
            date_range = st.date_input(
                "📅 เลือกช่วงวันที่ต้องการดู", [min_date, max_date]
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
        st.markdown(f"📊 **จำนวนข้อมูลสุทธิ:** `{len(df):,} รายการ`")
        st.markdown(
            f"🕒 **อัปเดตล่าสุด:** `{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}`"
        )

    if df.empty:
        st.warning("⚠️ ไม่พบข้อมูลตามเงื่อนไขที่เลือก กรุณาตรวจสอบใหม่อีกครั้ง")
        st.stop()

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
            kpi_card("📋 Total Records", f"{total_records:,}", "รายการทั้งหมด"),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            kpi_card(
                "👥 Total Occupancy / Persons", f"{total_people:,}", "ยอดสะสมรวม"
            ),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            kpi_card(
                "📈 Average per Entry", f"{average_people:,}", "ค่าเฉลี่ยต่อรอบ"
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ==================================================
    # CHARTS
    # ==================================================
    if "Date" in df.columns and "Person Count" in df.columns:
        daily = (
            df.groupby("Date")["Person Count"]
            .sum()
            .reset_index()
            .sort_values("Date")
        )

        st.subheader("📊 แนวโน้มการเข้า-ออกอาคารรายวัน (Time Series Analysis)")

        line_fig = px.line(
            daily,
            x="Date",
            y="Person Count",
            markers=True,
            color_discrete_sequence=[theme["line_color"]],
            labels={"Date": "วันที่", "Person Count": "จำนวนผู้อยู่อาศัย (คน)"},
        )
        line_fig.update_traces(
            line=dict(width=3), marker=dict(size=8, color=theme["marker_color"])
        )
        st.plotly_chart(
            style_chart(line_fig, theme, 400), use_container_width=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("##### 📉 สัดส่วนการใช้งานรายวัน (Bar Distribution)")
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
            st.markdown("##### 🌊 ความหนาแน่นสะสม (Cumulative Area Trend)")
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
    st.subheader("📂 รายละเอียดข้อมูลดิบ (Raw Data Table)")

    with st.expander("🔍 คลิกเพื่อดูหรือซ่อนตารางข้อมูลทั้งหมด", expanded=True):
        st.dataframe(df, use_container_width=True, height=400)

    csv_data = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 ดาวน์โหลดรายงานฉบับเต็ม (.CSV)",
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
            <b>Building Monitoring & Analytics Dashboard</b><br>
            Prince of Songkla University · Faculty of Engineering<br>
            <span style="font-size: 13px;">
                Academic Project 2026 • Developed with Streamlit & Python •
                Theme: {theme_choice}
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
            <div class="status-badge status-offline">
                <span class="status-dot"></span> Offline
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.error(f"⚠️ เกิดข้อผิดพลาดในการโหลดหรือประมวลผลข้อมูล: {e}")
    st.info(
        "คำแนะนำ: กรุณาตรวจสอบว่าลิงก์ Google Sheets เปิดแชร์แบบสาธารณะ "
        "(Anyone with the link) และคอลัมน์ในชีทมีชื่อถูกต้องตามที่โปรแกรมต้องการ "
        "(เช่น Date, Person Count)"
    )