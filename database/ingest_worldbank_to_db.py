#!/usr/bin/env python3
import os
import time
import argparse
import requests
import pymysql

DEFAULT_INDICATORS = [
    ("EN.GHG.CO2.MT.CE.AR5", "CO2 emissions (Mt CO2e)"),
    ("EN.ATM.CO2E.PC", "CO2 emissions (metric tons per capita)"),
    ("EG.USE.PCAP.KG.OE", "Energy use (kg of oil equivalent per capita)"),
    ("EG.FEC.RNEW.ZS", "Renewable energy consumption (% of total final energy consumption)"),
    ("EN.ATM.PM25.MC.M3", "PM2.5 air pollution, mean annual exposure (micrograms per cubic meter)"),
    ("EG.ELC.ACCS.ZS", "Access to electricity (% of population)"),
    ("AG.LND.FRST.ZS", "Forest area (% of land area)"),
]

# ISO3 codes for countries in project scope (broad coverage)
DEFAULT_COUNTRIES = [
    "TUR","USA","GBR","DEU","FRA","ITA","ESP","NLD","BEL","CHE","SWE","NOR","DNK","FIN","POL","CZE","AUT","HUN","ROU","BGR","GRC","PRT","IRL","UKR","RUS",
    "CHN","JPN","KOR","IND","PAK","IDN","VNM","THA","MYS","SGP","PHL","BGD","IRN","IRQ","SAU","ARE","QAT","KWT","ISR","JOR","LBN","SYR","YEM","EGY","MAR","DZA","TUN","LBY","ZAF","NGA","KEN","ETH","GHA",
    "CAN","MEX","BRA","ARG","CHL","COL","PER","AUS","NZL"
]

def load_env(path):
    env = {}
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

def get_conn(env):
    return pymysql.connect(
        host=env.get("MYSQL_HOST"), port=int(env.get("MYSQL_PORT", 3306)),
        user=env.get("MYSQL_USER"), password=env.get("MYSQL_PASSWORD"),
        database=env.get("MYSQL_DATABASE", "sayriks_earth_trend_detective"),
        connect_timeout=10, autocommit=False,
    )

def fetch_indicator(country, indicator, start, end):
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
    params = {"format": "json", "date": f"{start}:{end}", "per_page": 2000}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    js = r.json()
    if not isinstance(js, list) or len(js) < 2 or not js[1]:
        return []
    out = []
    for it in js[1]:
        val = it.get("value")
        if val is None:
            continue
        try:
            year = int(it.get("date"))
            value = float(val)
        except Exception:
            continue
        out.append({
            "country_code": it.get("countryiso3code") or country,
            "country_name": (it.get("country") or {}).get("value"),
            "indicator_code": (it.get("indicator") or {}).get("id") or indicator,
            "indicator_name": (it.get("indicator") or {}).get("value"),
            "year": year,
            "value": value,
        })
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", default=".env")
    ap.add_argument("--start", type=int, default=1981)
    ap.add_argument("--end", type=int, default=2025)
    ap.add_argument("--sleep", type=float, default=0.2)
    ap.add_argument("--countries", default="", help="Comma-separated ISO3 codes (default: preset list)")
    ap.add_argument("--indicators", default="", help="Comma-separated indicator codes (default: preset list)")
    args = ap.parse_args()

    env = load_env(args.env)
    countries = [c.strip().upper() for c in args.countries.split(",") if c.strip()] or DEFAULT_COUNTRIES
    if args.indicators:
        indicators = [(c.strip(), c.strip()) for c in args.indicators.split(",") if c.strip()]
    else:
        indicators = DEFAULT_INDICATORS

    conn = get_conn(env)
    cur = conn.cursor()
    sql = """
        INSERT INTO worldbank_indicator_raw
        (country_code, country_name, indicator_code, indicator_name, year, value, source)
        VALUES (%s,%s,%s,%s,%s,%s,'WorldBank')
        ON DUPLICATE KEY UPDATE
          country_name=VALUES(country_name),
          indicator_name=VALUES(indicator_name),
          value=VALUES(value),
          fetched_at=CURRENT_TIMESTAMP
    """
    total = 0
    try:
        for c in countries:
            for ind_code, ind_name in indicators:
                try:
                    rows = fetch_indicator(c, ind_code, args.start, args.end)
                    if rows:
                        cur.executemany(sql, [(r["country_code"], r["country_name"], r["indicator_code"], r["indicator_name"], r["year"], r["value"]) for r in rows])
                        conn.commit()
                        total += len(rows)
                        print(f"[OK] {c} {ind_code}: {len(rows)} rows (total {total})", flush=True)
                    else:
                        print(f"[SKIP] {c} {ind_code}: 0 rows", flush=True)
                except Exception as e:
                    conn.rollback()
                    print(f"[ERR] {c} {ind_code}: {e}", flush=True)
                time.sleep(args.sleep)
        print(f"[DONE] total_rows_upserted={total}", flush=True)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
