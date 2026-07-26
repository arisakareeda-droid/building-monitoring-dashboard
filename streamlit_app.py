import pandas as pd
import plotly.express as px
import streamlit as st

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="Building Monitoring & Analytics Dashboard",
    page_icon="🏢",
    layout="wide",
)

# ==================================================
# CUSTOM CSS (ดีไซน์แบบพรีเมียม ทันสมัย โทน PSU & Engineering)
# ==================================================
st.markdown(
    """
<style>
/* ซ่อน Menu และ Footer เริ่มต้นของ Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Global Styles */
.main {
    background-color: #f8fafc;
}

/* Header Titles */
.title-main {
    font-size: 38px;
    font-weight: 800;
    color: #002D72;
    margin-bottom: 0px;
    letter-spacing: -0.5px;
}

.subtitle-main {
    font-size: 17px;
    color: #64748b;
    font-weight: 500;
}

/* KPI Card Customization */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 16px;
    padding: 20px 24px;
    border: 1px solid #e2e8f0;
    border-top: 5px solid #002D72;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    transition: all 0.3s ease;
}

div[data-testid="metric-container"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    border-top-color: #D4AF37;
}

/* Chart Container Styling */
div[data-testid="stPlotlyChart"] {
    background: white;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

/* Sidebar Customization */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #002D72 0%, #001a41 100%);
    border-right: 1px solid #001a41;
}

section[data-testid="stSidebar"] * {
    color: #f1f5f9 !important;
}

section[data-testid="stSidebar"] .stTextInput input, 
section[data-testid="stSidebar"] .stDateInput input {
    background-color: rgba(255, 255, 255, 0.1);
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
}

/* Footer Design */
.footer-card {
    text-align: center;
    background: white;
    padding: 24px;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    color: #475569;
    margin-top: 40px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
</style>
""",
    unsafe_allow_html=True,
)


# ==================================================
# HEADER SECTION
# ==================================================
col_logo, col_title = st.columns([1, 8])

with col_logo:
    try:
        st.image("Logo-Songkla-251x300.png", width=100)
    except:
        st.markdown("<h1>🏢</h1>", unsafe_allow_html=True)

with col_title:
    st.markdown(
        """
        <div class="title-main">Building Occupancy & Activity Monitoring Dashboard</div>
        <div class="subtitle-main">ระบบวิเคราะห์ข้อมูลการเข้า-ออกอาคารอัจฉริยะแบบเรียลไทม์ | Faculty of Engineering, Prince of Songkla University</div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# ==================================================
# LOAD DATA (เชื่อมตรงกับ Google Sheets)
# ==================================================
SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "14FJt332r41O2JvookMlfzIqljBPSJ1wdt08XnnkTl-8/"
    "export?format=csv"
)


@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    return df


try:
    df = load_data()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # ==================================================
    # SIDEBAR CONTROLS
    # ==================================================
    with st.sidebar:
        try:
            st.image("Logo-Songkla-251x300.png", width=80)
        except:
            pass

        st.markdown("### ⚙️ Dashboard Controls")
        st.markdown("---")

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

        search_query = st.text_input(
            "🔍 ค้นหาข้อมูลในระบบ", placeholder="พิมพ์คำค้นหา..."
        )
        if search_query:
            df = df[
                df.astype(str)
                .apply(lambda x: x.str.contains(search_query, case=False))
                .any(axis=1)
            ]

        st.markdown("---")
        st.markdown(f"📊 **จำนวนข้อมูลสุทธิ:** `{len(df):,} รายการ`")
        st.markdown("📌 **สถานะระบบ:** Connected to Google Sheets")

    if df.empty:
        st.warning("⚠️ ไม่พบข้อมูลตามเงื่อนไขที่เลือก กรุณาตรวจสอบใหม่อีกครั้ง")
        st.stop()

    # ==================================================
    # KPI METRICS SECTION
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
        st.metric(
            label="📋 Total Records",
            value=f"{total_records:,}",
            delta="รายการทั้งหมด",
        )
    with col2:
        st.metric(
            label="👥 Total Occupancy / Persons",
            value=f"{total_people:,}",
            delta="ยอดสะสมรวม",
        )
    with col3:
        st.metric(
            label="📈 Average per Entry",
            value=f"{average_people:,}",
            delta="ค่าเฉลี่ยต่อรอบ",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ==================================================
    # VISUALIZATIONS SECTION (GRAPHS)
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
            color_discrete_sequence=["#002D72"],
            labels={"Date": "วันที่", "Person Count": "จำนวนผู้อยู่อาศัย (คน)"},
        )
        line_fig.update_traces(
            line=dict(width=3), marker=dict(size=8, color="#D4AF37")
        )
        line_fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
            margin=dict(t=20, b=20, l=20, r=20),
            height=400,
        )
        st.plotly_chart(line_fig, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("##### 📉 สัดส่วนการใช้งานรายวัน (Bar Distribution)")
            bar_fig = px.bar(
                daily,
                x="Date",
                y="Person Count",
                color="Person Count",
                color_continuous_scale="Blues",
                labels={"Date": "วันที่", "Person Count": "จำนวนคน"},
            )
            bar_fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=20, l=20, r=20),
                height=350,
                coloraxis_showscale=False,
            )
            st.plotly_chart(bar_fig, use_container_width=True)

        with col_b:
            st.markdown("##### 🌊 ความหนาแน่นสะสม (Cumulative Area Trend)")
            area_fig = px.area(
                daily,
                x="Date",
                y="Person Count",
                color_discrete_sequence=["#004b99"],
                labels={"Date": "วันที่", "Person Count": "จำนวนคน"},
            )
            area_fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=20, l=20, r=20),
                height=350,
            )
            st.plotly_chart(area_fig, use_container_width=True)

    # ==================================================
    # DATA TABLE & EXPORT SECTION
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
    # FOOTER SECTION
    # ==================================================
    st.markdown(
        """
        <div class="footer-card">
            <b>Building Monitoring & Analytics Dashboard</b><br>
            Prince of Songkla University | Faculty of Engineering<br>
            <span style="color: #64748b; font-size: 14px;">Academic Project 2026 • Developed with Streamlit & Python</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาดในการโหลดหรือประมวลผลข้อมูล: {e}")
    st.info(
        "คำแนะนำ: กรุณาตรวจสอบว่าลิงก์ Google Sheets เปิดแชร์แบบสาธารณะ (Anyone with the link) และคอลัมน์ในชีทมีชื่อถูกต้องตามที่โปรแกรมต้องการ (เช่น Date, Person Count)"
    )
