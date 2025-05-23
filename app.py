import streamlit as st
import pandas as pd
import gspread

# ——————————————— пароль ————————————————
def check_password():
    pwd = st.text_input("🔒 Введите пароль", type="password")
    if pwd != st.secrets["DASHBOARD_PASSWORD"]:
        st.error("❗ Неверный пароль")
        st.stop()

check_password()

# ————————— загрузка данных —————————
@st.cache_data(ttl=300)
def load_data():
    # 1) Авторизация через Service Account из секретов
    sa_info = st.secrets["google_service_account"]
    client  = gspread.service_account_from_dict(sa_info)

    # 2) Открываем новую таблицу и объединяем все листы
    sheet_id = "1l3f4VVZjm-gman06C5uA72s6Bf6k_Rd3jzqUenzpTbM"
    sh = client.open_by_key(sheet_id)
    dfs = []
    for ws in sh.worksheets():
        recs = ws.get_all_records()
        if recs:
            df = pd.DataFrame(recs)
            df["month"] = ws.title  # сохраняем имя листа
            dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)

    # 3) Вычленяем "Баер id" по той же формуле
    df["Баер id"] = (
        df["campaign"]
          .str.extract(r'_(\d+)_', expand=False)
          .fillna(0)
          .astype(int)
    )
    # 4) Приводим типы
    df["event_time"] = pd.to_datetime(df["event_time"])
    df["cost"]       = pd.to_numeric(df["cost"], errors="coerce") / 1e6

    return df

# ——————— рендеринг дашборда ———————
def main():
    st.title("📊 Затраты Moloco (новая таблица)")

    df = load_data()

    # Селектор группировки
    period = st.selectbox("Группировать по", ["День", "Неделя", "Месяц"])
    freq = {"День":"D", "Неделя":"W", "Месяц":"M"}[period]

    ts = df.set_index("event_time").resample(freq)["cost"].sum()

    st.subheader(f"График затрат ({period.lower()})")
    st.line_chart(ts)

    st.subheader("Таблица агрегированных затрат")
    table = ts.reset_index().rename(columns={"event_time":"Дата", "cost":"Затраты, $"})
    st.dataframe(table, use_container_width=True)

if __name__ == "__main__":
    main()
