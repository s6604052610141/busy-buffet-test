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

st.header("Task 1: พิสูจน์คำติชมที่เราได้รับจากเจ้าหน้าที่ฝ่ายบริการว่าเป็นความจริงหรือไม่")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. ลูกค้ารอนาน และทิ้งคิวจริงไหม?")
    waiting_guests = df[df['Wait_Time_Minutes'] > 0]
    fig1 = px.bar(waiting_guests.groupby('Guest_type')['Wait_Time_Minutes'].mean().reset_index(), 
                  x='Guest_type', y='Wait_Time_Minutes', color='Guest_type', 
                  title="เวลารอคิวเฉลี่ย (นาที)")
    st.plotly_chart(fig1, use_container_width=True)
    
    walkaway_count = df['Is_Walkaway'].sum()
    st.error(f"สรุป: เป็นความจริง ลูกค้าต้องรอนานเฉลี่ย 28-38 นาที และเกิดการทิ้งคิว {walkaway_count} กลุ่ม")

with col2:
    st.subheader("2. ร้านยุ่งทุกวันจริงไหม?")
    daily_traffic = df.groupby(['Date_Sheet', 'Guest_type'])['pax'].sum().reset_index()
    fig2 = px.bar(daily_traffic, x='Date_Sheet', y='pax', color='Guest_type', 
                  title="จำนวนลูกค้า (คน) ในแต่ละวัน", barmode='group')
    st.plotly_chart(fig2, use_container_width=True)
    
    st.warning("สรุป: ไม่เป็นความจริงทั้งหมด ร้านไม่ได้ยุ่งทุกวัน แต่ลูกค้า Walk-in ทะลักมาเฉพาะบางวัน")

with col3:
    st.subheader("3. ลูกค้านั่งเป็นเวลานานจริงไหม?")
    diners = df[df['Meal_Time_Minutes'] > 0]
    fig3 = px.box(diners, x='Guest_type', y='Meal_Time_Minutes', color='Guest_type', 
                  title="การกระจายตัวของเวลานั่งทาน (นาที)")
    st.plotly_chart(fig3, use_container_width=True)
    
    long_diners = len(diners[(diners['Guest_type'] == 'Walk in') & (diners['Meal_Time_Minutes'] > 120)])
    st.error(f"สรุป: เป็นความจริง มีลูกค้า Walk-in ถึง {long_diners} กลุ่มที่นั่งทานเกิน 2 ชั่วโมง ส่งผลให้การหมุนเวียนรอบโต๊ะลดลง")

st.divider()

st.header("Task 2: วิเคราะห์ข้อเสียของทั้ง 3 ข้อเสนอ (Disprove)")

tab1, tab2, tab3 = st.tabs(["1. ลดเวลานั่งรับประทานอาหาร (Reduce Time)", "2. ขึ้นราคาเป็น 259 บาททุกวัน (Increase Price)", "3. การยกเว้นคิวสำหรับแขก In-house (Queue Skipping)"])

with tab1:
    st.subheader("ข้อเสนอที่ 1: ลดเวลานั่งรับประทานอาหาร")
    st.write("**อาจจะไม่ได้ผล:** หากลดเวลาลงมากเกินไปเช่น จำกัดเหลือเพียง 1 ชั่วโมง หรือ 1 ชั่วโมง 30 นาที จะส่งผลกระทบต่อประสบการณ์ของแขก In-house ที่ต้องการพักผ่อน จากข้อมูลพบว่าแขก In-house บางกลุ่มใช้เวลานานสูงสุดถึง 321 นาที การตั้งกฎที่ตึงเกินไปอาจสร้างความไม่พอใจให้ลูกค้าระดับ VIP ของโรงแรมได้")

with tab2:
    st.subheader("ข้อเสนอที่ 2: ขึ้นราคาเป็น 259 บาท ทุกวัน")
    fig_price = px.bar(daily_traffic, x='Date_Sheet', y='pax', 
                       title="จำนวนลูกค้าในแต่ละวัน (สังเกตวันที่ลูกค้าหลักสิบ)", text_auto=True)
    st.plotly_chart(fig_price, use_container_width=True)
    st.write("**ไม่ได้ผล:** จากกราฟจะเห็นชัดเจนว่าในวันธรรมดา (เช่น Date 133) มีลูกค้าน้อยมาก ปัญหาคนล้นร้านเกิดแค่เฉพาะบางวันเท่านั้น การขึ้นราคาเป็น 259 บาท **ทุกวัน** จะเป็นการไล่ลูกค้าวันธรรมดาออกไป และทำให้ร้านสูญเสียรายได้เพื่อพยุงธุรกิจในช่วงที่คนน้อย")

with tab3:
    st.subheader("ข้อเสนอที่ 3: การยกเว้นคิวสำหรับแขก In-house")
    walkaway_data = df[df['Is_Walkaway'] == True].groupby('Guest_type').size().reset_index(name='Count')
    fig_skip = px.pie(walkaway_data, values='Count', names='Guest_type', 
                      title="สัดส่วนของลูกค้าที่ทิ้งคิว (Walkaway)")
    st.plotly_chart(fig_skip, use_container_width=True)
    st.write("**ไม่ได้ผล:** การยกเว้นคิวสำหรับแขก In-house จะยิ่งทำให้ลูกค้า Walk-in ต้องรอคิวที่นานขึ้นไปอีก ปัจจุบัน Walk-in ก็มีปัญหาการทิ้งคิว (Walkaway) สูงอยู่แล้ว และลูกค้า Walk-in คือกลุ่มลูกค้าที่สร้างรายได้จำนวนมากในวันที่ร้านยุ่ง หากทำแบบนี้อาจทำให้โรงแรมสูญเสียรายได้ก้อนใหญ่จากลูกค้า Walk-in ไปอย่างถาวร")

st.divider()

st.header("Task 3: ข้อเสนอที่ดีที่สุด (Best Solution) และมุมมองจากประสบการณ์ส่วนตัว")

diners_all = df[df['Meal_Time_Minutes'] > 0]
fig_task3 = px.histogram(diners_all, x='Meal_Time_Minutes', color='Guest_type',
                         title="ระยะเวลาการทานอาหาร (ส่วนใหญ่ใช้เวลาไม่เกิน 120 นาที)",
                         labels={'Meal_Time_Minutes': 'เวลาทานอาหาร (นาที)', 'count': 'จำนวนกลุ่มลูกค้า'},
                         barmode='overlay')
fig_task3.add_vline(x=120, line_width=3, line_dash="dash", line_color="red", 
                    annotation_text=" ตัดรอบที่ 2 ชั่วโมง (120 นาที) ", annotation_position="top right")

st.plotly_chart(fig_task3, use_container_width=True)
st.success("""
**ผมขอเลือกปรับแก้ข้อเสนอที่ 1: "ลดเวลานั่งทานโปรโมชั่นจาก 5 ชั่วโมง เหลือ 2 ชั่วโมง"**

**เหตุผลสนับสนุนจากข้อมูล (Data Insights):**
1. **ครอบคลุมลูกค้าส่วนใหญ่:** จากกราฟด้านบน เมื่อตีเส้นแบ่งที่ 2 ชั่วโมงจะเห็นว่าลูกค้าทั้ง In-house และ Walk-in กว่า 90% ใช้เวลาทานเสร็จก่อน 2 ชั่วโมง การจำกัดเวลานี้จึงครอบคลุมลูกค้าส่วนใหญ่แล้ว
2. **แก้ปัญหาโต๊ะเต็มได้ตรงจุด:** ปัญหาหลักเกิดจากกลุ่มลูกค้าฝั่งขวาของเส้นแดง (กลุ่มที่นั่งเกิน 2 ชั่วโมง) กฎใหม่นี้จะเข้าไปควบคุมพฤติกรรมนี้โดยตรง และทำให้เกิดการหมุนเวียนรอบโต๊ะที่เร็วขึ้น
3. **ลดปัญหาการทิ้งคิว:** เมื่อรอบโต๊ะหมุนเวียนเร็วขึ้น เวลารอคิวเฉลี่ยจะลดลง ซึ่งช่วยรักษาฐานลูกค้า Walk-in ไม่ให้ Walk-away ทิ้งคิวไปร้านอื่น

**เหตุผลสนับสนุนจากประสบการณ์ส่วนตัว (Personal Experience):**
จากประสบการณ์ส่วนตัวในฐานะผู้บริโภค ระยะเวลา 1.5 - 2 ชั่วโมงในการทานบุฟเฟต์คือ "มาตรฐาน" ที่ลูกค้ารู้สึกว่าคุ้มค่า อิ่มกำลังดี และไม่กดดันจนเกินไปครับ การเปิดโอกาสให้นั่งได้ถึง 5 ชั่วโมงมักจะทำให้เกิดพฤติกรรม "ทานเสร็จแล้วนั่งแช่คุยกัน" หรือ "นั่งเล่นมือถือยาวๆ" 

ในมุมมองของลูกค้าที่ต้องรอคิวอยู่หน้าร้าน การมองเข้ามาเห็นโต๊ะอื่นนั่งแช่ทั้งที่ทานเสร็จแล้ว ถือเป็นสิ่งที่สร้างความหงุดหงิดและส่งผลเสียต่อภาพลักษณ์ของร้านมากที่สุดครับ การลดเวลาเหลือ 2 ชั่วโมง นอกจากจะเพิ่มยอดขายจากการหมุนเวียนรอบโต๊ะได้มากขึ้นแล้ว ยังช่วยสร้างประสบการณ์ที่ยุติธรรมให้กับลูกค้าทุกคนที่ตั้งใจมาใช้บริการของโรงแรมด้วยครับ
""")
