import streamlit as st
import pandas as pd
import gspread

# ————————————— пароль-гейт —————————————
def check_password():
    pwd = st.text_input("🔒 Введите пароль", type="password")
    if pwd != st.secrets["DASHBOARD_PASSWORD"]:
        st.error("❗ Неверный пароль")
        st.stop()
check_password()

# ———————— загрузка и предобработка ————————
@st.cache_data(ttl=600)
def load_data():
    # 1) Авторизация через сервисный аккаунт
    sa_info = st.secrets["google_service_account"]
    client  = gspread.service_account_from_dict(sa_info)

    # 2) Открываем таблицу и объединяем все листы
    sheet_id = "1l3f4VVZjm-gman06C5uA72s6Bf6k_Rd3jzqUenzpTbM"
    sh       = client.open_by_key(sheet_id)
    dfs = []
    for ws in sh.worksheets():
        records = ws.get_all_records()
        if not records:
            continue
        df = pd.DataFrame(records)
        df["month"] = ws.title
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)

    # 3) Приводим типы:
    # — event_time в datetime
    df["event_time"] = pd.to_datetime(df["event_time"])
    # — cost может быть строкой с запятой, нормализуем → float
    df["cost"] = (
        df["cost"]
          .astype(str)
          .str.replace(",", ".")
          .astype(float) 
    ) / 1e6

    # 4) Баер id
    df["Баер id"] = (
        df["campaign"]
          .str.extract(r'_(\d+)_', expand=False)
          .fillna(0)
          .astype(int)
    )
    return df

# ———————— интерфейс ————————
def main():
    st.title("🔎 Moloco: фильтрация по датам")

    df = load_data()

    # Выбор диапазона дат
    min_date = df["event_time"].dt.date.min()
    max_date = df["event_time"].dt.date.max()
    start, end = st.date_input(
        "Период",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    # Применяем фильтр
    mask = (df["event_time"].dt.date >= start) & (df["event_time"].dt.date <= end)
    filtered = df.loc[mask]

    st.write(f"Показано записей: {filtered.shape[0]}")
    st.dataframe(filtered, use_container_width=True)

if __name__ == "__main__":
    main()
