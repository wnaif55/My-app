import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="مراقب الميزانية والديون", layout="wide")

st.title("📊 نظام إدارة الميزانية والمديونيات")

# --- القائمة الجانبية (الزمان) ---
st.sidebar.header("📅 إعدادات الوقت")
current_year = datetime.now().year
years = [current_year, current_year - 1, current_year + 1]
months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", 
          "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

selected_year = st.sidebar.selectbox("اختر السنة", years)
selected_month = st.sidebar.selectbox("اختر الشهر", months)

st.info(f"عرض البيانات لعام {selected_year} - شهر {selected_month}")

# --- قسم المديونيات (Debts) ---
st.header("💸 قسم المديونيات")
col1, col2, col3 = st.columns(3)

with col1:
    debt_name = st.text_input("اسم الدائن (الجهة)")
with col2:
    debt_amount = st.number_input("مبلغ الدين", min_value=0.0, step=10.0)
with col3:
    debt_status = st.selectbox("الحالة", ["غير مدفوع", "مدفوع جزئياً", "تم السداد"])

if st.button("إضافة دين جديد"):
    st.success(f"تم تسجيل دين لـ {debt_name} بمبلغ {debt_amount}")
    # هنا يمكن ربطها بقاعدة بيانات مستقبلاً

# --- قسم المصاريف الشهرية ---
st.divider()
st.header("📉 المصاريف والدخل لشهر " + selected_month)

col_in, col_out = st.columns(2)
with col_in:
    income = st.number_input("الدخل لهذا الشهر", min_value=0.0)
with col_out:
    expenses = st.number_input("إجمالي المصاريف المخطط لها", min_value=0.0)

# --- ملخص مالي سريع ---
st.subheader("📝 ملخص الحالة المالية")
balance = income - expenses
st.metric(label="الرصيد المتبقي", value=f"{balance} ريال")

if balance < 0:
    st.warning("تنبيه: مصاريفك تتجاوز دخلك لهذا الشهر!")
