import os
import requests
import pandas as pd
import streamlit as st


def _load_mysql_env():
    # Proje kökünde .env varsa oku
    candidates = []
    try:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates.append(os.path.join(base, ".env"))
    except Exception:
        pass
    candidates.append(os.path.join(os.getcwd(), ".env"))
    env = {}
    for p in candidates:
        if not p or not os.path.exists(p):
            continue
        try:
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip().strip("\r")
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
            if env:
                break
        except Exception:
            continue
    return env


@st.cache_data(show_spinner=False)
def fetch_nasa_power_data(lat, lon, start, end, parameter="T2M", start_month=1, end_month=12, start_day=1, end_day=None):
    """
    NASA POWER API üzerinden günlük zaman serisi verisi çeker.
    start/end: yıl; start_month/end_month: 1-12. İsteğe bağlı gün seçimi desteklenir.
    """
    parameter = (parameter or "T2M").strip().upper()
    try:
        import calendar
        if end_day is None:
            end_day = calendar.monthrange(int(end), int(end_month))[1]
        start_date = f"{int(start)}{int(start_month):02d}{int(start_day):02d}"
        end_date = f"{int(end)}{int(end_month):02d}{int(end_day):02d}"
    except Exception:
        start_date = f"{int(start)}0101"
        end_date = f"{int(end)}1231"

    url = (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters={parameter}&community=RE&longitude={lon}&latitude={lat}"
        f"&start={start_date}&end={end_date}&format=JSON"
    )

    try:
        response = requests.get(url, timeout=25)
        if response.status_code != 200:
            return None, f"NASA POWER API hata kodu: {response.status_code}"

        data = response.json()
        parameters = data.get("properties", {}).get("parameter", {})
        series = parameters.get(parameter, {})
        if not series:
            return None, f"Parametre verisi bulunamadı: {parameter}"

        df = pd.DataFrame(list(series.items()), columns=["Date", "Value"])
        df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d", errors="coerce")
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
        # NASA POWER eksik verileri genelde -999 ile döndürür
        df = df.replace(-999, pd.NA).dropna(subset=["Date", "Value"])
        df = df.sort_values("Date").reset_index(drop=True)

        if df.empty:
            return None, "Seçilen aralık için geçerli veri bulunamadı."

        # Analiz modülüyle uyum için Temperature sütunu da sağlanır
        df["Temperature"] = df["Value"].astype(float)
        df["Parameter"] = parameter
        return df, None
    except Exception as e:
        return None, f"API bağlantı/işleme hatası: {e}"


@st.cache_data(show_spinner=False)
def fetch_mysql_series(lat, lon, start, end, parameter="T2M", start_month=1, end_month=12):
    """MySQL (sayriks_earth_trend_detective.nasa_power_raw) üzerinden işlenmiş ham veriyi okur."""
    parameter = (parameter or "T2M").strip().upper()
    try:
        import pymysql
        import calendar
        env = _load_mysql_env()
        host = env.get("MYSQL_HOST")
        user = env.get("MYSQL_USER")
        password = env.get("MYSQL_PASSWORD")
        database = env.get("MYSQL_DATABASE", "sayriks_earth_trend_detective")
        port = int(env.get("MYSQL_PORT", 3306))
        if not (host and user):
            return None, "MySQL .env yapılandırması bulunamadı."
        end_day = calendar.monthrange(int(end), int(end_month))[1]
        start_date = f"{int(start)}-{int(start_month):02d}-01"
        end_date = f"{int(end)}-{int(end_month):02d}-{int(end_day):02d}"
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, connect_timeout=10)
        try:
            # Koordinat toleransı ile eşleştir (yakın nokta)
            q = """
                SELECT date, value
                FROM nasa_power_raw
                WHERE parameter=%s
                  AND date BETWEEN %s AND %s
                  AND ABS(lat - %s) < 0.11 AND ABS(lon - %s) < 0.11
                ORDER BY date
            """
            df = pd.read_sql(q, conn, params=(parameter, start_date, end_date, float(lat), float(lon)))
        finally:
            conn.close()
        if df is None or df.empty:
            return None, "MySQL'de seçili kriterlere uygun işlenmiş veri bulunamadı."
        df = df.rename(columns={"date": "Date", "value": "Value"})
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
        df = df.dropna(subset=["Date", "Value"]).sort_values("Date").reset_index(drop=True)
        df["Temperature"] = df["Value"].astype(float)
        df["Parameter"] = parameter
        return df, None
    except Exception as e:
        return None, f"MySQL okuma hatası: {e}"