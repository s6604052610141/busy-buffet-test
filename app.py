import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Busy Buffet Dashboard", layout="wide")
st.title("Busy Buffet: Data Analytics Dashboard")
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
    
    st.warning("สรุป: ไม่จริง! ร้านไม่ได้ยุ่งทุกวัน แต่ลูกค้า Walk-in ทะลักมาเฉพาะบางวัน")

with col3:
    st.subheader("3. ลูกค้านั่งแช่ทั้งวัน?")
    diners = df[df['Meal_Time_Minutes'] > 0]
    fig3 = px.box(diners, x='Guest_type', y='Meal_Time_Minutes', color='Guest_type', 
                  title="การกระจายตัวของเวลานั่งทาน (นาที)")
    st.plotly_chart(fig3, use_container_width=True)
    
    long_diners = len(diners[(diners['Guest_type'] == 'Walk in') & (diners['Meal_Time_Minutes'] > 120)])
    st.error(f"สรุป: จริง! มีลูกค้า Walk-in นั่งแช่เกิน 2 ชม. ถึง {long_diners} กลุ่ม")

st.divider()

st.header("Task 2: วิเคราะห์ข้อเสียของทั้ง 3 ข้อเสนอ (Disprove)")

tab1, tab2, tab3 = st.tabs(["1. ลดเวลานั่ง (Reduce Time)", "2. ขึ้นราคา 259 ทุกวัน (Increase Price)", "3. ให้ In-house ลัดคิว (Queue Skipping)"])

with tab1:
    st.subheader("ข้อเสนอที่ 1: ลดเวลานั่งทาน (5 ชม. ให้น้อยลง)")
    st.write("**ทำไมถึงอาจจะไม่เวิร์ค:** หากเราลดเวลาลงมากเกินไป (เช่น เหลือเพียง 1 ชั่วโมง) จะส่งผลกระทบโดยตรงต่อแขก In-house ของโรงแรมที่ต้องการพักผ่อนรับประทานอาหาร จากข้อมูลพบว่ามีแขก In-house บางกลุ่มใช้เวลานั่งนานสูงสุดถึง 321 นาที (กว่า 5 ชั่วโมง) การบังคับเวลาที่ตึงเกินไปอาจทำให้กลุ่มลูกค้า VIP ของโรงแรมเกิดความไม่พอใจได้")

with tab2:
    st.subheader("ข้อเสนอที่ 2: ขึ้นราคาเป็น 259 บาท ทุกวัน")
    fig_price = px.bar(daily_traffic, x='Date_Sheet', y='pax', 
                       title="จำนวนลูกค้าในแต่ละวัน (สังเกตวันที่ลูกค้าหลักสิบ)", text_auto=True)
    st.plotly_chart(fig_price, use_container_width=True)
    st.write("**ทำไมถึงจะไม่เวิร์ค:** จากกราฟจะเห็นชัดเจนว่าในวันธรรมดา (เช่น Date 133) มีลูกค้าน้อยมาก (เพียงหลักสิบคน) ปัญหาคนล้นร้านเกิดแค่เฉพาะบางวันเท่านั้น การขึ้นราคาเป็น 259 บาท **ทุกวัน** จะเป็นการไล่ลูกค้าวันธรรมดาออกไป และทำให้ร้านสูญเสียรายได้ฐานเพื่อพยุงธุรกิจในช่วงที่คนน้อย")

with tab3:
    st.subheader("ข้อเสนอที่ 3: ให้ลูกค้า In-house ลัดคิวได้เลย")
    walkaway_data = df[df['Is_Walkaway'] == True].groupby('Guest_type').size().reset_index(name='Count')
    fig_skip = px.pie(walkaway_data, values='Count', names='Guest_type', 
                      title="สัดส่วนของลูกค้าที่ทิ้งคิว (Walkaway)")
    st.plotly_chart(fig_skip, use_container_width=True)
    st.write("**ทำไมถึงจะไม่เวิร์ค:** การให้ In-house ลัดคิว จะทำให้ลูกค้า Walk-in ต้องรอกระแสคิวที่นานขึ้นไปอีก ปัจจุบัน Walk-in ก็มีปัญหาการทิ้งคิว (Walkaway) สูงอยู่แล้ว และ Walk-in คือกลุ่มลูกค้าที่สร้างรายได้จำนวนมากในวันที่ร้านยุ่ง การสร้างความไม่เท่าเทียมจนลูกค้า Walk-in ทิ้งคิวหนีไป จะทำให้ยอดขายหดหายอย่างหนัก")

st.divider()

st.header("Task 3: ข้อเสนอที่ดีที่สุด (Best Solution) และมุมมองจากประสบการณ์ส่วนตัว")
st.success("""
**ผมขอเลือกปรับแก้ข้อเสนอที่ 1: "ลดเวลานั่งทานโปรโมชั่นจาก 5 ชั่วโมง เหลือ 2 ชั่วโมง"**

**เหตุผลสนับสนุนจากข้อมูล (Data Insights):**
1. **ไม่กระทบคนส่วนใหญ่:** ข้อมูลชี้ชัดว่าลูกค้า Walk-in นั่งทานเฉลี่ย 66.8 นาที และ In-house นั่งเฉลี่ยเพียง 45.8 นาที การจำกัดเวลาไว้ที่ 120 นาที (2 ชั่วโมง) จึงครอบคลุมและเพียงพอสำหรับลูกค้ากว่า 90%
2. **แก้ปัญหาโต๊ะเต็มได้ตรงจุด:** ปัญหาหลักเกิดจากกลุ่ม Walk-in 22 กลุ่มที่นั่งแช่เกิน 2 ชั่วโมง กฎใหม่นี้จะเข้าไปควบคุมพฤติกรรมนี้โดยตรง ทำให้มีโต๊ะว่างหมุนเวียน (Table Turnover) เร็วขึ้น
3. **ลดปัญหาการทิ้งคิว:** เมื่อโต๊ะหมุนเวียนเร็วขึ้น เวลารอคิวเฉลี่ยจะลดลง ซึ่งช่วยรักษาฐานลูกค้า Walk-in ไม่ให้ Walk-away ทิ้งคิวไปร้านอื่น

**เหตุผลสนับสนุนจากประสบการณ์ส่วนตัว (Personal Experience):**
จากประสบการณ์ส่วนตัวในฐานะผู้บริโภคที่ชื่นชอบการทานบุฟเฟต์ ระยะเวลา 1.5 - 2 ชั่วโมงคือ "มาตรฐาน" (Standard) ที่ลูกค้ารู้สึกว่าคุ้มค่า อิ่มกำลังดี และไม่กดดันจนเกินไปครับ การให้เวลาลากยาวถึง 5 ชั่วโมงมักจะทำให้เกิดพฤติกรรม "ทานเสร็จแล้วนั่งแช่คุยกัน" หรือ "นั่งเล่นมือถือยาวๆ" 

ในมุมมองของลูกค้าที่ต้องรอคิวอยู่หน้าร้าน การมองเข้ามาเห็นโต๊ะอื่นนั่งแช่ทั้งที่ทานเสร็จแล้ว เป็นสิ่งที่สร้างความหงุดหงิดและส่งผลเสียต่อภาพลักษณ์ของร้านมากที่สุดครับ การลดเวลาเหลือ 2 ชั่วโมง นอกจากจะเพิ่มรายได้จากรอบหมุนเวียนโต๊ะแล้ว ยังช่วยสร้างประสบการณ์ที่ยุติธรรมให้กับลูกค้าทุกคนที่ตั้งใจมารอทานอาหารของทางโรงแรมด้วยครับ
""")
