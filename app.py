import streamlit as st
import pandas as pd
import gspread, google.auth
import re

# ———————————————— пароль-гейт ————————————————
def check_password():
    pwd = st.text_input("🔒 Введите пароль", type="password")
    if pwd != st.secrets["DASHBOARD_PASSWORD"]:
        st.error("❗ Неверный пароль")
        st.stop()

check_password()

# ————————————— загрузка и предобработка —————————————
@st.cache_data(ttl=300)
def load_data():
    # Авторизация в Google Sheets
    creds, _ = google.auth.default(
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(creds)

    # 1) Moloco: объединяем все месяцы в один DF
    moloco_id = "1sHB72j5o4SJ-42WTHrK6XZz9EML930s1EcTX4BlohGU"
    sh = client.open_by_key(moloco_id)
    dfs = []
    for ws in sh.worksheets():
        recs = ws.get_all_records()
        if recs:
            df = pd.DataFrame(recs)
            df["month"] = ws.title
            dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)

    # 2) Вычленяем Баер id
    df["Баер id"] = (
        df["campaign"]
          .str.extract(r'_(\d+)_', expand=False)
          .fillna(0)
          .astype(int)
    )

    # 3) Приводим типы
    df["event_time"] = pd.to_datetime(df["event_time"])
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce") / 1e6

    return df

# ———————————————— рендеринг ————————————————
def main():
    st.title("📊 Затраты Moloco по времени")

    df = load_data()

    # Выбор группировки
    period = st.selectbox("Группировать по", ["День", "Неделя", "Месяц"])
    freq_map = {"День":"D", "Неделя":"W", "Месяц":"M"}
    freq = freq_map[period]

    # Агрегация
    ts = df.set_index("event_time").resample(freq)["cost"].sum()

    # График
    st.subheader(f"График затрат ({period.lower()})")
    st.line_chart(ts)

    # Таблица
    st.subheader("Таблица агрегированных затрат")
    table = ts.reset_index().rename(columns={"event_time":"Дата", "cost":"Затраты, $"})
    st.dataframe(table, use_container_width=True)

if __name__ == "__main__":
    main()
