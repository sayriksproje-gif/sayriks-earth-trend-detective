#!/usr/bin/env python3
"""
NASA POWER ham verilerini çekip veritabanına işler (SQLite varsayılan, MySQL opsiyonel).

Kullanım örnekleri:
  python3 database/ingest_nasa_to_db.py --db sqlite --sqlite-path database/nasa_earth_trend_detective.sqlite
  python3 database/ingest_nasa_to_db.py --db mysql --env .env
  python3 database/ingest_nasa_to_db.py --db mysql --host 172.25.240.1 --port 3306 --user USER --password PASS --database sayriks_earth_trend_detective

Not: Ağ erişimi ve NASA POWER API erişimi gerekir. Büyük veri çekimleri zaman alabilir.
"""
import argparse
import os
import sqlite3
import time
from datetime import date

import requests

LOCATIONS = [
    ("Adana, Türkiye", "Türkiye", "province", 37.0, 35.3213),
    ("Adıyaman, Türkiye", "Türkiye", "province", 37.7648, 38.2786),
    ("Afyonkarahisar, Türkiye", "Türkiye", "province", 38.7507, 30.5567),
    ("Ağrı, Türkiye", "Türkiye", "province", 39.7191, 43.0503),
    ("Amasya, Türkiye", "Türkiye", "province", 40.6499, 35.8353),
    ("Ankara, Türkiye", "Türkiye", "capital", 39.9334, 32.8597),
    ("Antalya, Türkiye", "Türkiye", "province", 36.8969, 30.7133),
    ("Artvin, Türkiye", "Türkiye", "province", 41.1828, 41.8183),
    ("Aydın, Türkiye", "Türkiye", "province", 37.856, 27.8416),
    ("Balıkesir, Türkiye", "Türkiye", "province", 39.6484, 27.8826),
    ("Bilecik, Türkiye", "Türkiye", "province", 40.0567, 30.0665),
    ("Bingöl, Türkiye", "Türkiye", "province", 38.8854, 40.4966),
    ("Bitlis, Türkiye", "Türkiye", "province", 38.4006, 42.1095),
    ("Bolu, Türkiye", "Türkiye", "province", 40.735, 31.6061),
    ("Burdur, Türkiye", "Türkiye", "province", 37.7204, 30.2908),
    ("Bursa, Türkiye", "Türkiye", "province", 40.1826, 29.0665),
    ("Çanakkale, Türkiye", "Türkiye", "province", 40.1553, 26.4142),
    ("Çankırı, Türkiye", "Türkiye", "province", 40.6013, 33.6134),
    ("Çorum, Türkiye", "Türkiye", "province", 40.5506, 34.9556),
    ("Denizli, Türkiye", "Türkiye", "province", 37.7765, 29.0864),
    ("Diyarbakır, Türkiye", "Türkiye", "province", 37.9144, 40.2306),
    ("Edirne, Türkiye", "Türkiye", "province", 41.6818, 26.5623),
    ("Elazığ, Türkiye", "Türkiye", "province", 38.681, 39.2264),
    ("Erzincan, Türkiye", "Türkiye", "province", 39.75, 39.5),
    ("Erzurum, Türkiye", "Türkiye", "province", 39.9055, 41.2658),
    ("Eskişehir, Türkiye", "Türkiye", "province", 39.7767, 30.5206),
    ("Gaziantep, Türkiye", "Türkiye", "province", 37.0662, 37.3833),
    ("Giresun, Türkiye", "Türkiye", "province", 40.9128, 38.3895),
    ("Gümüşhane, Türkiye", "Türkiye", "province", 40.4386, 39.5086),
    ("Hakkari, Türkiye", "Türkiye", "province", 37.5833, 43.7333),
    ("Hatay, Türkiye", "Türkiye", "province", 36.4018, 36.3498),
    ("Isparta, Türkiye", "Türkiye", "province", 37.7648, 30.5566),
    ("Mersin, Türkiye", "Türkiye", "province", 36.8121, 34.6415),
    ("İstanbul, Türkiye", "Türkiye", "province", 41.0082, 28.9784),
    ("İzmir, Türkiye", "Türkiye", "province", 38.4237, 27.1428),
    ("Kars, Türkiye", "Türkiye", "province", 40.6167, 43.1),
    ("Kastamonu, Türkiye", "Türkiye", "province", 41.3887, 33.7827),
    ("Kayseri, Türkiye", "Türkiye", "province", 38.7312, 35.4787),
    ("Kırklareli, Türkiye", "Türkiye", "province", 41.7333, 27.2167),
    ("Kırşehir, Türkiye", "Türkiye", "province", 39.1425, 34.1709),
    ("Kocaeli, Türkiye", "Türkiye", "province", 40.8533, 29.8815),
    ("Konya, Türkiye", "Türkiye", "province", 37.8746, 32.4932),
    ("Kütahya, Türkiye", "Türkiye", "province", 39.4167, 29.9833),
    ("Malatya, Türkiye", "Türkiye", "province", 38.3552, 38.3095),
    ("Manisa, Türkiye", "Türkiye", "province", 38.6191, 27.4289),
    ("Kahramanmaraş, Türkiye", "Türkiye", "province", 37.5858, 36.9371),
    ("Mardin, Türkiye", "Türkiye", "province", 37.3212, 40.7245),
    ("Muğla, Türkiye", "Türkiye", "province", 37.2153, 28.3636),
    ("Muş, Türkiye", "Türkiye", "province", 38.9462, 41.7539),
    ("Nevşehir, Türkiye", "Türkiye", "province", 38.6939, 34.6857),
    ("Niğde, Türkiye", "Türkiye", "province", 37.9667, 34.6833),
    ("Ordu, Türkiye", "Türkiye", "province", 40.9839, 37.8764),
    ("Rize, Türkiye", "Türkiye", "province", 41.0201, 40.5234),
    ("Sakarya, Türkiye", "Türkiye", "province", 40.694, 30.4358),
    ("Samsun, Türkiye", "Türkiye", "province", 41.2867, 36.33),
    ("Siirt, Türkiye", "Türkiye", "province", 37.9333, 41.95),
    ("Sinop, Türkiye", "Türkiye", "province", 42.0231, 35.1531),
    ("Sivas, Türkiye", "Türkiye", "province", 39.7477, 37.0179),
    ("Tekirdağ, Türkiye", "Türkiye", "province", 40.9833, 27.5167),
    ("Tokat, Türkiye", "Türkiye", "province", 40.3167, 36.55),
    ("Trabzon, Türkiye", "Türkiye", "province", 41.0015, 39.7178),
    ("Tunceli, Türkiye", "Türkiye", "province", 39.1079, 39.5401),
    ("Şanlıurfa, Türkiye", "Türkiye", "province", 37.1591, 38.7969),
    ("Uşak, Türkiye", "Türkiye", "province", 38.6823, 29.4082),
    ("Van, Türkiye", "Türkiye", "province", 38.4891, 43.4089),
    ("Yozgat, Türkiye", "Türkiye", "province", 39.8181, 34.8147),
    ("Zonguldak, Türkiye", "Türkiye", "province", 41.4564, 31.7987),
    ("Aksaray, Türkiye", "Türkiye", "province", 38.3687, 34.037),
    ("Bayburt, Türkiye", "Türkiye", "province", 40.2552, 40.2249),
    ("Karaman, Türkiye", "Türkiye", "province", 37.1759, 33.2287),
    ("Kırıkkale, Türkiye", "Türkiye", "province", 39.8468, 33.5153),
    ("Batman, Türkiye", "Türkiye", "province", 37.8812, 41.1351),
    ("Şırnak, Türkiye", "Türkiye", "province", 37.4187, 42.4918),
    ("Bartın, Türkiye", "Türkiye", "province", 41.6344, 32.3375),
    ("Ardahan, Türkiye", "Türkiye", "province", 41.1105, 42.7022),
    ("Iğdır, Türkiye", "Türkiye", "province", 39.9167, 44.0333),
    ("Yalova, Türkiye", "Türkiye", "province", 40.65, 29.2667),
    ("Karabük, Türkiye", "Türkiye", "province", 41.2061, 32.6204),
    ("Kilis, Türkiye", "Türkiye", "province", 36.7184, 37.1212),
    ("Osmaniye, Türkiye", "Türkiye", "province", 37.0742, 36.2478),
    ("Düzce, Türkiye", "Türkiye", "province", 40.8438, 31.1565),
    ("Tiran, Arnavutluk", "Arnavutluk", "capital", 41.3275, 19.8187),
    ("Cezayir, Cezayir", "Cezayir", "capital", 36.7538, 3.0588),
    ("Andorra la Vella, Andorra", "Andorra", "capital", 42.5063, 1.5218),
    ("Luanda, Angola", "Angola", "capital", -8.839, 13.2894),
    ("Buenos Aires, Arjantin", "Arjantin", "capital", -34.6037, -58.3816),
    ("Erivan, Ermenistan", "Ermenistan", "capital", 40.1792, 44.4991),
    ("Viyana, Avusturya", "Avusturya", "capital", 48.2082, 16.3738),
    ("Bakü, Azerbaycan", "Azerbaycan", "capital", 40.4093, 49.8671),
    ("Manama, Bahreyn", "Bahreyn", "capital", 26.2235, 50.5876),
    ("Dakka, Bangladeş", "Bangladeş", "capital", 23.8103, 90.4125),
    ("Minsk, Belarus", "Belarus", "capital", 53.9006, 27.559),
    ("Brüksel, Belçika", "Belçika", "capital", 50.8503, 4.3517),
    ("Saraybosna, Bosna-Hersek", "Bosna-Hersek", "capital", 43.8563, 18.4131),
    ("Gaborone, Botsvana", "Botsvana", "capital", -24.6282, 25.9231),
    ("Sofya, Bulgaristan", "Bulgaristan", "capital", 42.6977, 23.3219),
    ("Ouagadougou, Burkina Faso", "Burkina Faso", "capital", 12.3714, -1.5197),
    ("Phnom Penh, Kamboçya", "Kamboçya", "capital", 11.5564, 104.9282),
    ("Yaoundé, Kamerun", "Kamerun", "capital", 3.848, 11.5021),
    ("Ottawa, Kanada", "Kanada", "capital", 45.4215, -75.6972),
    ("Santiago, Şili", "Şili", "capital", -33.4489, -70.6693),
    ("Pekin, Çin", "Çin", "capital", 39.9042, 116.4074),
    ("Bogotá, Kolombiya", "Kolombiya", "capital", 4.711, -74.0721),
    ("San José, Kosta Rika", "Kosta Rika", "capital", 9.9281, -84.0907),
    ("Zagreb, Hırvatistan", "Hırvatistan", "capital", 45.815, 15.9819),
    ("Havana, Küba", "Küba", "capital", 23.1136, -82.3666),
    ("Lefkoşa, Kıbrıs", "Kıbrıs", "capital", 35.1856, 33.3823),
    ("Prag, Çekya", "Çekya", "capital", 50.0755, 14.4378),
    ("Kopenhag, Danimarka", "Danimarka", "capital", 55.6761, 12.5683),
    ("Santo Domingo, Dominik Cumhuriyeti", "Dominik Cumhuriyeti", "capital", 18.4861, -69.9312),
    ("Quito, Ekvador", "Ekvador", "capital", -0.1807, -78.4678),
    ("Kahire, Mısır", "Mısır", "capital", 30.0444, 31.2357),
    ("San Salvador, El Salvador", "El Salvador", "capital", 13.6929, -89.2182),
    ("Tallinn, Estonya", "Estonya", "capital", 59.437, 24.7536),
    ("Addis Ababa, Etiyopya", "Etiyopya", "capital", 9.03, 38.74),
    ("Helsinki, Finlandiya", "Finlandiya", "capital", 60.1699, 24.9384),
    ("Paris, Fransa", "Fransa", "capital", 48.8566, 2.3522),
    ("Tiflis, Gürcistan", "Gürcistan", "capital", 41.7151, 44.8271),
    ("Berlin, Almanya", "Almanya", "capital", 52.52, 13.405),
    ("Akra, Gana", "Gana", "capital", 5.6037, -0.187),
    ("Atina, Yunanistan", "Yunanistan", "capital", 37.9838, 23.7275),
    ("Guatemala City, Guatemala", "Guatemala", "capital", 14.6349, -90.5069),
    ("Budapeşte, Macaristan", "Macaristan", "capital", 47.4979, 19.0402),
    ("Reykjavik, İzlanda", "İzlanda", "capital", 64.1466, -21.9426),
    ("Yeni Delhi, Hindistan", "Hindistan", "capital", 28.6139, 77.209),
    ("Cakarta, Endonezya", "Endonezya", "capital", -6.2088, 106.8456),
    ("Tahran, İran", "İran", "capital", 35.6892, 51.389),
    ("Bağdat, Irak", "Irak", "capital", 33.3152, 44.3661),
    ("Dublin, İrlanda", "İrlanda", "capital", 53.3498, -6.2603),
    ("Kudüs, İsrail", "İsrail", "capital", 31.7683, 35.2137),
    ("Roma, İtalya", "İtalya", "capital", 41.9028, 12.4964),
    ("Tokyo, Japonya", "Japonya", "capital", 35.6762, 139.6503),
    ("Amman, Ürdün", "Ürdün", "capital", 31.9454, 35.9284),
    ("Astana, Kazakistan", "Kazakistan", "capital", 51.1605, 71.4704),
    ("Nairobi, Kenya", "Kenya", "capital", -1.2921, 36.8219),
    ("Kuveyt, Kuveyt", "Kuveyt", "capital", 29.3759, 47.9774),
    ("Bişkek, Kırgızistan", "Kırgızistan", "capital", 42.8746, 74.5698),
    ("Riga, Letonya", "Letonya", "capital", 56.9496, 24.1052),
    ("Beyrut, Lübnan", "Lübnan", "capital", 33.8938, 35.5018),
    ("Trablus, Libya", "Libya", "capital", 32.8872, 13.1913),
    ("Vilnius, Litvanya", "Litvanya", "capital", 54.6872, 25.2797),
    ("Lüksemburg, Lüksemburg", "Lüksemburg", "capital", 49.6116, 6.1319),
    ("Üsküp, Kuzey Makedonya", "Kuzey Makedonya", "capital", 41.9981, 21.4254),
    ("Antananarivo, Madagaskar", "Madagaskar", "capital", -18.8792, 47.5079),
    ("Kuala Lumpur, Malezya", "Malezya", "capital", 3.139, 101.6869),
    ("Bamako, Mali", "Mali", "capital", 12.6392, -8.0029),
    ("Valletta, Malta", "Malta", "capital", 35.8989, 14.5146),
    ("Mexico City, Meksika", "Meksika", "capital", 19.4326, -99.1332),
    ("Kişinev, Moldova", "Moldova", "capital", 47.0105, 28.8638),
    ("Ulan Batur, Moğolistan", "Moğolistan", "capital", 47.8864, 106.9057),
    ("Podgorica, Karadağ", "Karadağ", "capital", 42.4304, 19.2594),
    ("Rabat, Fas", "Fas", "capital", 34.0209, -6.8416),
    ("Maputo, Mozambik", "Mozambik", "capital", -25.9692, 32.5732),
    ("Katmandu, Nepal", "Nepal", "capital", 27.7172, 85.324),
    ("Amsterdam, Hollanda", "Hollanda", "capital", 52.3676, 4.9041),
    ("Wellington, Yeni Zelanda", "Yeni Zelanda", "capital", -41.2865, 174.7762),
    ("Abuja, Nijerya", "Nijerya", "capital", 9.0765, 7.3986),
    ("Oslo, Norveç", "Norveç", "capital", 59.9139, 10.7522),
    ("Maskat, Umman", "Umman", "capital", 23.588, 58.3829),
    ("İslamabad, Pakistan", "Pakistan", "capital", 33.6844, 73.0479),
    ("Panama City, Panama", "Panama", "capital", 8.9824, -79.5199),
    ("Asunción, Paraguay", "Paraguay", "capital", -25.2637, -57.5759),
    ("Lima, Peru", "Peru", "capital", -12.0464, -77.0428),
    ("Manila, Filipinler", "Filipinler", "capital", 14.5995, 120.9842),
    ("Varşova, Polonya", "Polonya", "capital", 52.2297, 21.0122),
    ("Lizbon, Portekiz", "Portekiz", "capital", 38.7223, -9.1393),
    ("Doha, Katar", "Katar", "capital", 25.2854, 51.531),
    ("Bükreş, Romanya", "Romanya", "capital", 44.4268, 26.1025),
    ("Moskova, Rusya", "Rusya", "capital", 55.7558, 37.6173),
    ("Riyad, Suudi Arabistan", "Suudi Arabistan", "capital", 24.7136, 46.6753),
    ("Dakar, Senegal", "Senegal", "capital", 14.7167, -17.4677),
    ("Belgrad, Sırbistan", "Sırbistan", "capital", 44.7866, 20.4489),
    ("Singapur, Singapur", "Singapur", "capital", 1.3521, 103.8198),
    ("Bratislava, Slovakya", "Slovakya", "capital", 48.1486, 17.1077),
    ("Ljubljana, Slovenya", "Slovenya", "capital", 46.0569, 14.5058),
    ("Pretoria, Güney Afrika", "Güney Afrika", "capital", -25.7479, 28.2293),
    ("Seul, Güney Kore", "Güney Kore", "capital", 37.5665, 126.978),
    ("Madrid, İspanya", "İspanya", "capital", 40.4168, -3.7038),
    ("Kolombo, Sri Lanka", "Sri Lanka", "capital", 6.9271, 79.8612),
    ("Stockholm, İsveç", "İsveç", "capital", 59.3293, 18.0686),
    ("Bern, İsviçre", "İsviçre", "capital", 46.948, 7.4474),
    ("Şam, Suriye", "Suriye", "capital", 33.5138, 36.2765),
    ("Taipei, Tayvan", "Tayvan", "capital", 25.033, 121.5654),
    ("Duşanbe, Tacikistan", "Tacikistan", "capital", 38.5598, 68.787),
    ("Dar es Salaam, Tanzanya", "Tanzanya", "capital", -6.7924, 39.2083),
    ("Bangkok, Tayland", "Tayland", "capital", 13.7563, 100.5018),
    ("Tunus, Tunus", "Tunus", "capital", 36.8065, 10.1815),
    ("Kampala, Uganda", "Uganda", "capital", 0.3476, 32.5825),
    ("Kiev, Ukrayna", "Ukrayna", "capital", 50.4501, 30.5234),
    ("Abu Dabi, BAE", "BAE", "capital", 24.4539, 54.3773),
    ("Londra, Birleşik Krallık", "Birleşik Krallık", "capital", 51.5074, -0.1278),
    ("Washington DC, ABD", "ABD", "capital", 38.8951, -77.0364),
    ("Montevideo, Uruguay", "Uruguay", "capital", -34.9011, -56.1645),
    ("Taşkent, Özbekistan", "Özbekistan", "capital", 41.2995, 69.2401),
    ("Caracas, Venezuela", "Venezuela", "capital", 10.4806, -66.9036),
    ("Hanoi, Vietnam", "Vietnam", "capital", 21.0278, 105.8342),
    ("Sana, Yemen", "Yemen", "capital", 15.3694, 44.191),
    ("Lusaka, Zambiya", "Zambiya", "capital", -15.3875, 28.3228),
    ("Harare, Zimbabve", "Zimbabve", "capital", -17.8252, 31.0335),
    ("Brasilia, Brezilya", "Brezilya", "capital", -15.8267, -47.9218),
    ("Canberra, Avustralya", "Avustralya", "capital", -35.2809, 149.13),
]
# Geniş kapsamlı NASA POWER parametre seti (fiziksel iklim göstergeleri)
PARAMETERS = [
    "T2M", "T2M_MAX", "T2M_MIN", "T2MDEW", "T2MWET", "TS",
    "RH2M", "QV2M",
    "PRECTOTCORR", "PRECSNO", "EVLAND", "GWETTOP", "GWETROOT",
    "ALLSKY_SFC_SW_DWN", "CLRSKY_SFC_SW_DWN", "ALLSKY_SFC_SW_DNI", "ALLSKY_SFC_SW_DIFF",
    "ALLSKY_SFC_LW_DWN", "ALLSKY_SFC_LW_UP", "CLRSKY_SFC_LW_DWN", "TOA_SW_DWN",
    "ALLSKY_SFC_UV_INDEX", "ALLSKY_SFC_PAR_TOT", "CLRSKY_SFC_PAR_TOT",
    "WS2M", "WS10M", "WS2M_MAX", "WS2M_MIN", "WD2M", "WD10M",
    "PS", "CLOUD_AMT", "CLOUD_AMT_DAY", "TQV", "AOD_55", "FROST_DAYS",
]


def load_env(path):
    d = {}
    if not path or not os.path.exists(path):
        return d
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip().strip("\r")
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def connect_mysql(args):
    try:
        import pymysql
    except Exception as e:
        raise SystemExit(f"PyMySQL gerekli: {e}")
    env = load_env(getattr(args, "env", None))
    host = args.host or env.get("MYSQL_HOST", "127.0.0.1")
    port = int(args.port or env.get("MYSQL_PORT", 3306))
    user = args.user or env.get("MYSQL_USER")
    password = args.password if args.password is not None else env.get("MYSQL_PASSWORD")
    database = args.database or env.get("MYSQL_DATABASE", "sayriks_earth_trend_detective")
    if not user:
        raise SystemExit("MySQL kullanıcı bilgisi eksik (--user veya .env MYSQL_USER)")
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database,
                           charset="utf8mb4", connect_timeout=15, autocommit=False)
    return conn


def ensure_mysql(args):
    conn = connect_mysql(args)
    schema_path = os.path.join(os.path.dirname(__file__), "schema_mysql.sql")
    if os.path.exists(schema_path):
        sql = open(schema_path, "r", encoding="utf-8").read()
        # execute statement by statement (skip CREATE DATABASE/USE if connected to target)
        cur = conn.cursor()
        buff = ""
        for line in sql.splitlines():
            s = line.strip()
            if not s or s.startswith("--"):
                continue
            buff += line + "\n"
            if s.endswith(";"):
                st = buff.strip()
                # allow running; ignore errors for create/use if already in place
                try:
                    cur.execute(st)
                except Exception:
                    pass
                buff = ""
        conn.commit()
    return conn


class DB:
    def __init__(self, conn, kind):
        self.conn = conn
        self.kind = kind  # sqlite|mysql

    def execute(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur

    def executemany(self, sql, seq):
        cur = self.conn.cursor()
        cur.executemany(sql, seq)
        return cur

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()



def ensure_sqlite(db_path):
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(open(os.path.join(os.path.dirname(__file__), "schema_sqlite.sql"), "r", encoding="utf-8").read())
    conn.commit()
    return conn


def upsert_location(db, name, country, ltype, lat, lon):
    if db.kind == "sqlite":
        db.execute("INSERT OR IGNORE INTO locations(name,country,location_type,lat,lon) VALUES (?,?,?,?,?)", (name, country, ltype, lat, lon))
        cur = db.execute("SELECT id FROM locations WHERE name=? AND lat=? AND lon=?", (name, lat, lon))
    else:
        db.execute("INSERT IGNORE INTO locations(name,country,location_type,lat,lon) VALUES (%s,%s,%s,%s,%s)", (name, country, ltype, lat, lon))
        cur = db.execute("SELECT id FROM locations WHERE name=%s AND lat=%s AND lon=%s", (name, lat, lon))
    row = cur.fetchone()
    db.commit()
    return row[0] if row else None


def fetch_power(lat, lon, start, end, parameter):
    url = (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters={parameter}&community=RE&longitude={lon}&latitude={lat}"
        f"&start={start}0101&end={end}1231&format=JSON"
    )
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}"
    data = r.json()
    series = data.get("properties", {}).get("parameter", {}).get(parameter, {})
    if not series:
        return None, "no_data"
    return series, None


def store_series(db, loc_id, lat, lon, parameter, series, start_y, end_y):
    rows = []
    for k, v in series.items():
        try:
            if v is None:
                continue
            fv = float(v)
            if fv == -999:
                continue
            dt = f"{k[0:4]}-{k[4:6]}-{k[6:8]}"
            rows.append((loc_id, "NASA_POWER", parameter, "RE", "daily", dt, fv, None, lat, lon, f"{start_y}-01-01", f"{end_y}-12-31", None))
        except Exception:
            continue
    if not rows:
        return 0
    if db.kind == "sqlite":
        q = """INSERT INTO nasa_power_raw
               (location_id,source,parameter,community,temporal,date,value,unit,lat,lon,start_date,end_date,quality_flag)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    else:
        q = """INSERT INTO nasa_power_raw
               (location_id,source,parameter,community,temporal,date,value,unit,lat,lon,start_date,end_date,quality_flag)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    # chunk to avoid huge packets
    chunk = 2000
    for i in range(0, len(rows), chunk):
        db.executemany(q, rows[i:i+chunk])
    db.commit()
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", choices=["sqlite", "mysql"], default="sqlite")
    ap.add_argument("--sqlite-path", default="database/nasa_earth_trend_detective.sqlite")
    ap.add_argument("--env", default=".env", help="MySQL için .env dosyası yolu")
    ap.add_argument("--host", default=None)
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--user", default=None)
    ap.add_argument("--password", default=None)
    ap.add_argument("--database", default=None)
    ap.add_argument("--start-year", type=int, default=1981)
    ap.add_argument("--end-year", type=int, default=date.today().year)
    ap.add_argument("--parameters", default="", help="Virgülle ayrılmış parametre listesi (boşsa varsayılan geniş set)")
    ap.add_argument("--locations-limit", type=int, default=0, help="0 = tüm preset lokasyonlar")
    ap.add_argument("--sleep", type=float, default=0.2, help="API istekleri arası bekleme (sn)")
    ap.add_argument("--force", action="store_true", help="Mevcut verisi olsa bile lokasyonu yeniden çek")
    args = ap.parse_args()

    params = [p.strip().upper() for p in args.parameters.split(",") if p.strip()] if args.parameters else PARAMETERS
    locs = LOCATIONS[: args.locations_limit] if args.locations_limit and args.locations_limit > 0 else LOCATIONS

    if args.db == "mysql":
        conn = ensure_mysql(args)
        db = DB(conn, "mysql")
        print(f"DB: MySQL -> {args.database or '(.env)'} @ {args.host or '(.env)'}")
    else:
        conn = ensure_sqlite(args.sqlite_path)
        db = DB(conn, "sqlite")
        print(f"DB: SQLite -> {args.sqlite_path}")

    total = 0
    for (name, country, ltype, lat, lon) in locs:
        loc_id = upsert_location(db, name, country, ltype, lat, lon)
        # skip if this location already has data (avoid duplicate bulk inserts)
        try:
            if db.kind == "sqlite":
                curc = db.execute("SELECT COUNT(*) FROM nasa_power_raw WHERE ABS(lat-?)<0.11 AND ABS(lon-?)<0.11", (lat, lon))
            else:
                curc = db.execute("SELECT COUNT(*) FROM nasa_power_raw WHERE ABS(lat-%s)<0.11 AND ABS(lon-%s)<0.11", (lat, lon))
            existing = curc.fetchone()[0] or 0
        except Exception:
            existing = 0
        if existing > 0 and not args.force:
            print(f"[SKIP-LOC] {name}: mevcut kayıt var ({existing}), atlanıyor (--force ile yeniden)")
            continue
        for p in params:
            try:
                series, err = fetch_power(lat, lon, args.start_year, args.end_year, p)
                if err:
                    print(f"[SKIP] {name} {p}: {err}")
                else:
                    n = store_series(db, loc_id, lat, lon, p, series, args.start_year, args.end_year)
                    total += n
                    print(f"[OK] {name} {p}: {n} kayıt")
            except Exception as e:
                print(f"[ERR] {name} {p}: {e}")
            time.sleep(args.sleep)
    db.close()
    print(f"Toplam eklenen kayıt: {total}")


if __name__ == "__main__":
    main()
