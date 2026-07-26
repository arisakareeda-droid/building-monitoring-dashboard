import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Building & Data Monitoring Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Building & Data Monitoring Dashboard")
st.markdown("ระบบแสดงผลข้อมูลและติดตามสถานะจาก Google Sheets แบบเรียลไทม์")

st.sidebar.header("⚙️ ตั้งค่าการเชื่อมต่อ")
sheet_url = st.sidebar.text_input(
    "วางลิงก์ Google Sheets (แชร์แบบสาธารณะ)",
    placeholder="https://docs.google.com/spreadsheets/d/..."
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
        with st.spinner("กำลังโหลดข้อมูลจาก Google Sheets..."):
            df = load_data(csv_url)
        
        st.success("โหลดข้อมูลสำเร็จ!")
        
        st.subheader("📋 ข้อมูลทั้งหมดในตาราง")
        st.dataframe(df, use_container_width=True)
        
        st.subheader("📈 สรุปข้อมูลเบื้องต้น")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("จำนวนแถวทั้งหมด", len(df))
        with col2:
            st.metric("จำนวนคอลัมน์", len(df.columns))
        with col3:
            st.metric("สถานะ", "เชื่อมต่อแล้ว ✅")
            
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        if numeric_cols:
            st.subheader("📊 แผนภูมิแสดงข้อมูลเชิงตัวเลข")
            selected_col = st.selectbox("เลือกคอลัมน์เพื่อแสดงกราฟ", numeric_cols)
            st.line_chart(df[selected_col])
        else:
            st.info("ไม่พบคอลัมน์ที่เป็นตัวเลขสำหรับสร้างกราฟอัตโนมัติ")
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
        st.info("💡 คำแนะนำ: ตรวจสอบให้แน่ใจว่าลิงก์ถูกต้อง และตั้งค่าการแชร์ใน Google Sheets เป็น 'ทุกคนที่มีลิงก์สามารถดูได้'")
else:
    st.info("👈 กรุณากรอกลิงก์ Google Sheets ของคุณที่แถบด้านซ้ายมือเพื่อเริ่มต้นใช้งาน")
