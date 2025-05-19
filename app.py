import streamlit as st

# 1) Простой пароль-гейт
def check_password():
    """
    Запрашивает пароль из st.secrets["DASHBOARD_PASSWORD"].
    Если введён неверный — прерывает выполнение.
    """
    pwd = st.text_input("🔒 Введите пароль", type="password")
    if "DASHBOARD_PASSWORD" not in st.secrets:
        st.error("Скройте секрет DASHBOARD_PASSWORD в настройках Streamlit Cloud.")
        st.stop()
    if pwd != st.secrets["DASHBOARD_PASSWORD"]:
        st.error("❗ Неверный пароль")
        st.stop()

check_password()

# 2) Основной код дашборда
import pandas as pd
import gspread
import google.auth

@st.cache_data(ttl=300)
def load_data():
    # TODO: вставьте ваш код загрузки из Google Sheets
    return pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=300)
def preprocess(df1, df2):
    # TODO: вставьте ваш код предобработки
    return df1, df2

def main():
    st.title("Live Dashboard из Google Sheets")
    df1, df2 = load_data()
    df1, df2 = preprocess(df1, df2)

    st.subheader("Таблица 1")
    st.dataframe(df1)

    st.subheader("Таблица 2")
    st.dataframe(df2)

if __name__ == "__main__":
    main()
