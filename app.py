import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('budget_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS debts 
                 (id INTEGER PRIMARY KEY, name TEXT, amount REAL, status TEXT, month TEXT, year INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS budget 
                 (id INTEGER PRIMARY KEY, income REAL, expenses REAL, month TEXT, year INTEGER)''')
    conn.commit()
    conn.close()

# دالة لجلب بيانات السنة كاملة للرسم البياني
def get_yearly_data(year):
    conn = sqlite3.connect('budget_data.db')
    query = f"SELECT month, income, expenses FROM budget WHERE year={year}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # ترتيب الأشهر بشكل صحيح
    month_order = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", 
                   "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
    if not df.empty:
        df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)
        df = df.sort_values('month')
    return df

# (بقية الدوال السابقة لإضافة البيانات تبقى كما هي...)
def add_debt_to_db(name, amount, status, month, year):
    conn = sqlite3.connect('budget_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO debts (name, amount, status, month, year) VALUES (?, ?, ?, ?, ?)", (name, amount, status, month, year))
    conn.commit()
    conn.close()

def update_budget_db(income, expenses, month, year):
    conn = sqlite3.connect('budget_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM budget WHERE month=? AND year=?", (month, year))
    c.execute("INSERT INTO budget (income, expenses, month, year) VALUES (?, ?, ?, ?)", (income, expenses, month, year))
    conn.commit()
    conn.close()

def load_data(month, year):
    conn = sqlite3.connect('budget_data.db')
    debts_df = pd.read_sql_query(f"SELECT name, amount, status FROM debts WHERE month='{month}' AND year={year}", conn)
    budget_df = pd.read_sql_query(f"SELECT income, expenses FROM budget WHERE month='{month}' AND year={year}", conn)
    conn.close()
    return debts_df, budget_df

# --- واجهة التطبيق ---
init_db()
st.set_page_config(page_title="المحلل المالي الذكي", layout="wide")

st.title("📊 لوحة تحكم الميزانية والديون")

# القائمة الجانبية
st.sidebar.header("📅 الإعدادات")
current_year = datetime.now().year
selected_year = st.sidebar.selectbox("السنة", [current_year, current_year-1])
selected_month = st.sidebar.selectbox("الشهر", ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"])

# تبويبات لتنظيم الواجهة
tab1, tab2 = st.tabs(["📝 إدخال البيانات", "📈 التحليل البياني"])

with tab1:
    debts_df, budget_df = load_data(selected_month, selected_year)
    
    # قسم المديونيات
    st.subheader(f"💸 مديونيات {selected_month}")
    with st.expander("إضافة/تعديل دين"):
        col1, col2, col3 = st.columns(3)
        d_name = col1.text_input("الدائن")
        d_amount = col2.number_input("المبلغ", min_value=0.0, key="debt_amt")
        d_status = col3.selectbox("الحالة", ["غير مدفوع", "مدفوع جزئياً", "تم السداد"])
        if st.button("حفظ المديونية"):
            add_debt_to_db(d_name, d_amount, d_status, selected_month, selected_year)
            st.success("تم التحديث!")
            st.rerun()

    if not debts_df.empty:
        st.dataframe(debts_df, use_container_width=True)
    
    st.divider()
    
    # قسم الميزانية
    st.subheader(f"📉 دخل ومصاريف {selected_month}")
    default_in = budget_df['income'].iloc[0] if not budget_df.empty else 0.0
    default_ex = budget_df['expenses'].iloc[0] if not budget_df.empty else 0.0
    
    c1, c2 = st.columns(2)
    new_in = c1.number_input("الدخل الشهرى", value=default_in)
    new_ex = c2.number_input("المصاريف", value=default_ex)
    
    if st.button("تحديث ميزانية الشهر"):
        update_budget_db(new_in, new_ex, selected_month, selected_year)
        st.rerun()

with tab2:
    st.subheader(f"📊 مقارنة الأداء المالي لعام {selected_year}")
    yearly_df = get_yearly_data(selected_year)
    
    if not yearly_df.empty:
        # تجهيز البيانات للرسم البياني
        chart_data = yearly_df.set_index('month')
        st.bar_chart(chart_data[['income', 'expenses']])
        
        # نصيحة ذكية بناءً على البيانات
        avg_expenses = yearly_df['expenses'].mean()
        st.info(f"💡 متوسط مصاريفك الشهرية هذا العام هو: **{avg_expenses:.2f} ريال**")
    else:
        st.warning("لا توجد بيانات كافية لعرض الرسم البياني. قم بإدخال بيانات لعدة أشهر أولاً.")
