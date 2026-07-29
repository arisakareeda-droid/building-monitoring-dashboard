import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps


def make_circular_favicon(path: str, size: int = 256):
    """ครอปรูปให้เป็นวงกลมโปร่งใส ใช้เฉพาะสำหรับ favicon เท่านั้น"""
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
_favicon = make_circular_favicon(str(_FAVICON_PATH)) if _FAVICON_PATH.exists() else "🏢"

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

# ... (ส่วนการตั้งค่าธีมและฟังก์ชันอื่นๆ คงเดิม) ...

# ==================================================
# HEADER
# ==================================================
col_logo, col_title, col_status = st.columns([1, 6, 2])

with col_logo:
    try:
        # ใช้ไฟล์ logo_proj.jpg แสดงผลด้านซ้ายของหัวข้อหลัก
        st.image("logo_proj.jpg", width=90)
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
            df.groupby("Date")["Person Count"].sum().reset_index().sort_values("Date")
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
        st.plotly_chart(style_chart(line_fig, theme, 400), use_container_width=True)

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
