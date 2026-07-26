import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Real-Time Building Occupancy Monitoring and Alert System",
    page_icon="🏢",
    layout="wide",
)

st.title("🏢 Real-Time Building Occupancy Monitoring and Alert System")
st.markdown("ระบบติดตามจำนวนผู้อยู่อาศัยในอาคารและการแจ้งเตือนแบบเรียลไทม์จาก Google Sheets")

st.sidebar.header("⚙️ ตั้งค่าการเชื่อมต่อ")
sheet_url = st.sidebar.text_input(
    "วางลิงก์ Google Sheets (แชร์แบบสาธารณะ)",
    placeholder="https://docs.google.com/spreadsheets/d/14FJt332r41O2JvookMlfzIqljBPSJ1wdt08XnnkTl-8/edit?usp=sharing",
)


def convert_sheet_url(url):
  if not url:
    return None
  if "/edit" in url:
    base_url = url.split("/edit")[0]
    return f"{base_url}/export?format=csv"
  return url


if sheet_url:
  csv_url = convert_sheet_url(sheet_url)


  @st.cache_data(ttl=60)
  def load_data(url):
    return pd.read_csv(url)


  try:
    with st.spinner("กำลังดึงข้อมูลจาก Google Sheets..."):
      df = load_data(csv_url)

    st.success("เชื่อมต่อและโหลดข้อมูลสำเร็จ!")

    st.subheader("📋 ข้อมูลการใช้งานอาคารทั้งหมด")
    st.dataframe(df, use_container_width=True)

    st.subheader("📊 สรุปภาพรวมระบบ (Overview)")
    col1, col2, col3 = st.columns(3)
    with col1:
      st.metric("จำนวนรายการทั้งหมด", len(df))
    with col2:
      st.metric("จำนวนพารามิเตอร์/คอลัมน์", len(df.columns))
    with col3:
      st.metric("สถานะระบบ", "Online / Active 🟢")

    numeric_cols = df.select_dtypes(
        include=["float64", "int64"]
    ).columns.tolist()
    if numeric_cols:
      st.subheader("📈 แผนภูมิแสดงแนวโน้มอัตราการเข้าใช้งาน")
      selected_col = st.selectbox(
          "เลือกตัวแปรที่ต้องการวิเคราะห์กราฟ", numeric_cols
      )
      st.line_chart(df[selected_col])
    else:
      st.info("ไม่พบคอลัมน์ที่เป็นตัวเลขสำหรับสร้างกราฟวิเคราะห์อัตโนมัติ")

  except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
    st.info(
        "💡 คำแนะนำ: ตรวจสอบลิงก์ Google Sheets และตั้งค่าการแชร์เป็น 'ทุกคนที่มีลิงก์สามารถดูได้'"
    )
else:
  st.info(
      "👈 กรุณาวางลิงก์ Google Sheets ของคุณที่แถบด้านซ้ายมือเพื่อเริ่มใช้งานระบบ"
  )
