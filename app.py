import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# 1) Пароль-гейт
def check_password():
    if st.text_input("🔒 Введите пароль", type="password") != st.secrets["DASHBOARD_PASSWORD"]:
        st.error("Неверный пароль"); st.stop()
check_password()

@st.cache_data(ttl=3600)
def load_data_batch():
    # 2) Авторизация (service account)
    creds_dict = st.secrets["google_service_account"]
    creds = Credentials.from_service_account_info(creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    service = build("sheets", "v4", credentials=creds)

    sheet_id = "1l3f4VVZjm-gman06C5uA72s6Bf6k_Rd3jzqUenzpTbM"
    # 3) Узнаём список листов
    meta = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    titles = [s["properties"]["title"] for s in meta["sheets"]]

    # 4) Формируем batch-запрос по всем листам
    ranges = [f"{t}!A1:Z" for t in titles]  # A1:Z — захватываем до колонки Z
    resp = service.spreadsheets().values().batchGet(
        spreadsheetId=sheet_id, ranges=ranges).execute()

    dfs = []
    for vr in resp.get("valueRanges", []):
        vals = vr.get("values", [])
        if not vals: continue
        df = pd.DataFrame(vals[1:], columns=vals[0])
        df["month"] = vr["range"].split("!")[0]
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)
    df["event_time"] = pd.to_datetime(df["event_time"])
    df["cost"]       = pd.to_numeric(df["cost"], errors="coerce")/1e6
    return df

def main():
    st.title("📈 Moloco: затраты по времени (batch API)")
    df = load_data_batch()

    start, end = st.date_input(
        "Период:",
        [df["event_time"].dt.date.min(), df["event_time"].dt.date.max()]
    )
    mask = (df["event_time"].dt.date >= start) & (df["event_time"].dt.date <= end)
    filt = df.loc[mask]

    period = st.selectbox("Группировать по", ["День","Неделя","Месяц"])
    freq = {"День":"D","Неделя":"W","Месяц":"M"}[period]
    ts = filt.set_index("event_time").resample(freq)["cost"].sum()

    st.subheader("График")
    st.line_chart(ts)
    st.subheader("Таблица")
    st.dataframe(ts.reset_index().rename(columns={"event_time":"Дата","cost":"Затраты, $"}))

if __name__=="__main__":
    main()
