import streamlit as st
import pandas as pd
import gspread

# ———— 1) Пароль-гейт ————
def check_password():
    pwd = st.text_input("🔒 Введите пароль", type="password")
    if pwd != st.secrets["DASHBOARD_PASSWORD"]:
        st.error("❗ Неверный пароль")
        st.stop()

check_password()

# ———— 2) Загрузка и объединение листов ————
@st.cache_data(ttl=300)
def load_moloco():
    sa_info = st.secrets["google_service_account"]
    client  = gspread.service_account_from_dict(sa_info)

    sheet_id = "1l3f4VVZjm-gman06C5uA72s6Bf6k_Rd3jzqUenzpTbM"
    sh       = client.open_by_key(sheet_id)

    dfs = []
    for ws in sh.worksheets():
        recs = ws.get_all_records()
        if recs:
            df = pd.DataFrame(recs)
            df["month"] = ws.title
            dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)
    df["event_time"] = pd.to_datetime(df["event_time"])
    return df

# ———— 3) Интерфейс фильтрации и вывода ————
def main():
    st.title("🔎 Moloco: фильтрация по датам")

    df = load_moloco()

    # диапазон дат
    min_date = df["event_time"].dt.date.min()
    max_date = df["event_time"].dt.date.max()
    start, end = st.date_input(
        "Выберите период", [min_date, max_date], min_value=min_date, max_value=max_date
    )

    # фильтр
    mask = (df["event_time"].dt.date >= start) & (df["event_time"].dt.date <= end)
    filtered = df.loc[mask]

    st.write(f"Показаны записи с **{start}** по **{end}** (всего: {filtered.shape[0]})")
    st.dataframe(filtered, use_container_width=True)

if __name__ == "__main__":
    main()
