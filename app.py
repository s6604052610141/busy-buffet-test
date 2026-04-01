import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Busy Buffet Dashboard", layout="wide")
st.title("🍳 Busy Buffet: Data Analytics Dashboard")
st.markdown("วิเคราะห์ปัญหาคิวและพฤติกรรมลูกค้า เพื่อหาทางออกที่ดีที่สุดให้ห้องอาหาร")

@st.cache_data
def load_data():
    file_name = '2026 Data Test1 Final - Busy Buffet Dataset.xlsx'
    all_sheets = pd.read_excel(file_name, sheet_name=None)
    
    df_list = []
    for sheet_name, data in all_sheets.items():
        data['Date_Sheet'] = sheet_name
        df_list.append(data)
        
    df = pd.concat(df_list, ignore_index=True)
    
    time_cols = ['queue_start', 'queue_end', 'meal_start', 'meal_end']
    for col in time_cols:
        df[col] = pd.to_datetime(df[col], format='%H:%M:%S', errors='coerce')
        
    df['Wait_Time_Minutes'] = (df['queue_end'] - df['queue_start']).dt.total_seconds() / 60
    df['Meal_Time_Minutes'] = (df['meal_end'] - df['meal_start']).dt.total_seconds() / 60
    df['Is_Walkaway'] = df['queue_start'].notna() & df['meal_start'].isna()
    
    return df

df = load_data()

st.divider()

st.header("Task 1: พิสูจน์ 3 คำบ่นของพนักงาน")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. ลูกค้ารอนาน & ทิ้งคิว?")
    waiting_guests = df[df['Wait_Time_Minutes'] > 0]
    fig1 = px.bar(waiting_guests.groupby('Guest_type')['Wait_Time_Minutes'].mean().reset_index(), 
                  x='Guest_type', y='Wait_Time_Minutes', color='Guest_type', 
                  title="เวลารอคิวเฉลี่ย (นาที)")
    st.plotly_chart(fig1, use_container_width=True)
    
    walkaway_count = df['Is_Walkaway'].sum()
    st.error(f"สรุป: จริง! รอนานเฉลี่ย 12-17 นาที และมีคนทิ้งคิวถึง {walkaway_count} กลุ่ม")

with col2:
    st.subheader("2. ร้านยุ่งทุกวันจริงไหม?")
    daily_traffic = df.groupby(['Date_Sheet', 'Guest_type'])['pax'].sum().reset_index()
    fig2 = px.bar(daily_traffic, x='Date_Sheet', y='pax', color='Guest_type', 
                  title="จำนวนลูกค้า (คน) ในแต่ละวัน", barmode='group')
    st.plotly_chart(fig2, use_container_width=True)
    
    st.warning("สรุป: ไม่จริง! ร้านไม่ได้ยุ่งทุกวัน แต่ลูกค้า Walk-in ทะลักมาเฉพาะบางวัน (คาดว่าเป็นวันหยุด)")

with col3:
    st.subheader("3. ลูกค้านั่งแช่ทั้งวัน?")
    diners = df[df['Meal_Time_Minutes'] > 0]
    fig3 = px.box(diners, x='Guest_type', y='Meal_Time_Minutes', color='Guest_type', 
                  title="การกระจายตัวของเวลานั่งทาน (นาที)")
    st.plotly_chart(fig3, use_container_width=True)
    
    long_diners = len(diners[(diners['Guest_type'] == 'Walk in') & (diners['Meal_Time_Minutes'] > 120)])
    st.error(f"สรุป: จริง! มีลูกค้า Walk-in นั่งแช่เกิน 2 ชม. ถึง {long_diners} กลุ่ม")

st.divider()

st.header("Task 2: บทสรุปและข้อเสนอแนะ")
st.success("""
**เห็นด้วยกับข้อเสนอของฝ่ายบริหาร: "ควรลดเวลาโปรโมชั่นจาก 5 ชั่วโมง เหลือ 2 ชั่วโมง"**

**เหตุผลสนับสนุนจากข้อมูล:**
1. ลูกค้า Walk-in ส่วนใหญ่ใช้เวลานั่งทานเฉลี่ยเพียงประมาณ 67 นาที การจำกัดเวลาที่ 2 ชั่วโมง (120 นาที) **จะไม่กระทบความพึงพอใจของลูกค้าส่วนใหญ่**
2. ปัญหาที่แท้จริงเกิดจากลูกค้า Walk-in จำนวน 22 กลุ่มที่ใช้เวลานั่งทานเกิน 2 ชั่วโมง (บางกลุ่มลากยาวเกือบ 5 ชั่วโมง) ซึ่งทำให้โต๊ะไม่ถูกหมุนเวียน
3. หากลดเวลาเหลือ 2 ชั่วโมง จะเป็นการบังคับกลุ่มที่นั่งแช่ให้ลุกเร็วขึ้น ทำให้มีโต๊ะว่างรองรับลูกค้า In-house และช่วยลดอัตราการรอนานจนทิ้งคิว (Walk-away) ได้โดยตรง
""")