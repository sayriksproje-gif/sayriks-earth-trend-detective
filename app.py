import os
import io
import json
import base64
import sqlite3
import calendar
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

from utils.analyzer import calculate_trend_and_stats
from utils.data_fetcher import fetch_nasa_power_data, fetch_mysql_series

st.set_page_config(
    page_title="Earth Trend Detective | NASA Space Apps 2026",
    page_icon="🌍",
    layout="wide",
)

I18N = {
    "tr": {
        "language": "Dil",
        "app_subtitle": "NASA açık verileriyle iklim göstergelerindeki değişimi, büyüklüğünü ve anlamlılığını keşfet.",
        "hero_source": "Ana veri: NASA POWER • Destekleyici: World Bank Open Data • Mod: Gerçek veri / MySQL / Simülasyon",
        "control_panel": "Kontrol Paneli",
        "data_source_mode": "Veri kaynağı modu",
        "mode_mysql": "MySQL (İşlenmiş Veri)",
        "mode_nasa": "NASA POWER (Gerçek Veri)",
        "mode_sim": "Simülasyon (Offline/Demo)",
        "mysql_ok": "MySQL bağlantısı/şema hazır: sayriks_earth_trend_detective",
        "mysql_note": "Veritabanı: sayriks_earth_trend_detective (nasa_power_raw)",
        "mysql_missing": "MySQL .env veya bağlantı bulunamadı; NASA/Simülasyon kullanılabilir.",
        "time_resolution": "Zaman çözünürlüğü (analiz)",
        "daily": "Günlük",
        "monthly_avg": "Aylık ortalama",
        "parameter": "Parametre",
        "custom_param": "ÖZEL (NASA POWER kodu gir)",
        "custom_param_code": "NASA POWER parametre kodu",
        "location_preset": "Lokasyon (hazır)",
        "custom_location": "Özel konum (lat/lon)",
        "latitude": "Enlem (lat)",
        "longitude": "Boylam (lon)",
        "location_name": "Lokasyon adı",
        "start_year": "Başlangıç Yılı",
        "start_month": "Başlangıç Ayı",
        "end_year": "Bitiş Yılı",
        "end_month": "Bitiş Ayı",
        "months_filter": "Analizde gösterilecek aylar (boş = tümü)",
        "compare_scan": "Hazır lokasyonlarda hızlı karşılaştırma (trend taraması)",
        "scan_group": "Tarama grubu",
        "scan_count": "Taranacak lokasyon sayısı",
        "scan_help": "MySQL modunda işlenmiş veriler hızlı taranır; tarama grubundaki lokasyonlar seçilebilir.",
        "wide_mode": "Geniş dönem demo (1981–2025)",
        "fetching_data": "Veri alınıyor ve analiz ediliyor...",
        "scanning": "Hazır lokasyonlar taranıyor...",
        "tab_map": "🗺️ Harita & Genel Bakış",
        "tab_trends": "📈 Trend & İstatistik",
        "tab_data": "📋 Veri Tablosu",
        "tab_methods": "🧪 Metodoloji & Kaynaklar",
        "tab_presentation": "🎤 Sunum",
        "selected_location": "Seçili Lokasyon",
        "coordinate": "Koordinat",
        "period": "Dönem",
        "source": "Kaynak",
        "average": "Ortalama",
        "maximum": "Maksimum",
        "minimum": "Minimum",
        "trend_10y": "Trend (10 yıl)",
        "point_analysis": "Nokta Analizi (Seçili/karşılaştırma)",
        "global_heatmap": "Dünya Geneli Isı Haritası (Yıl/Ay)",
        "globe": "Dünya (küre)",
        "worldbank_shortcut": "Karbon & Enerji Bağlamı (World Bank) — Kısayol",
        "wb_info": "Seçili gösterge ve ülke için World Bank verisi canlı çekilir ve özetlenir.",
        "wb_fetch": "World Bank verisini çek ve işle",
        "wb_fetching": "World Bank verisi çekiliyor...",
        "download_csv": "Veriyi CSV olarak indir",
        "save_sqlite": "Bu seriyi SQLite veritabanına kaydet",
        "saved_sqlite": "SQLite veritabanına kaydedildi.",
        "presentation_title": "Veri Destekli Sunum",
        "presentation_download": "Sunumu indir (HTML, yazdırılabilir/PDF)",
        "print_pdf_hint": "PDF almak için tarayıcıda Yazdır (Ctrl+P) seçeneğini kullanın ve hedef olarak PDF olarak kaydet seçin.",
        "no_data": "Seçilen kriterlere uygun veri bulunamadı.",
        "sim_note": "Simülasyon modu: Bu veriler demo amaçlıdır, bilimsel gözlem değildir.",
        "ocean_note": "Not: Küre görünümlerinde okyanuslar mavi tonlarda gösterilir; 3B/gerçek uydu dokusu kullanılmadığı için koyu görünebilir. Bu bir görselleştirme katmanıdır.",
        "significance": "Anlamlılık",
        "p_value": "p-değeri",
        "mk": "Mann-Kendall",
        "ci95": "%95 Güven Aralığı (10 yıl)",
        "methodology_title": "Metodoloji",
        "sources_title": "Kaynaklar",
        "limitations_title": "Sınırlılıklar ve Veri Kalitesi",
        "radiation_title": "Radyasyon ve Ekosistem Etkileri",
        "data_table_title": "Veri Tablosu",
        "chart_time_series": "Zaman Serisi",
        "chart_anomaly": "Yıllık Anomali",
        "chart_trend": "Trend Çizgisi",
        "records": "Kayıt",
        "group_tr": "Türkiye",
        "group_world": "Dünya",
        "group_capitals": "Dünya Başkentleri",
        "group_all": "Tümü",
        "nasa_data_used": "Kullanılan NASA Verileri",
        "data_volume": "Analiz Veri Hacmi",
        "problematic_data": "Sorunlu/Eksik Veri ve Etkileri",
        "country_avg": "Ülke Bazlı Ortalamalar ve Isı Değişimi",
        "radiation_section": "Radyasyon Verileri: Ekosisteme Faydalar ve Zararlar",
    },
    "en": {
        "language": "Language",
        "app_subtitle": "Explore change, magnitude, and significance in climate indicators with NASA open data.",
        "hero_source": "Primary data: NASA POWER • Supporting: World Bank Open Data • Mode: Real data / MySQL / Simulation",
        "control_panel": "Control Panel",
        "data_source_mode": "Data source mode",
        "mode_mysql": "MySQL (Processed Data)",
        "mode_nasa": "NASA POWER (Real Data)",
        "mode_sim": "Simulation (Offline/Demo)",
        "mysql_ok": "MySQL connection/schema ready: sayriks_earth_trend_detective",
        "mysql_note": "Database: sayriks_earth_trend_detective (nasa_power_raw)",
        "mysql_missing": "MySQL .env or connection not found; NASA/Simulation can be used.",
        "time_resolution": "Time resolution (analysis)",
        "daily": "Daily",
        "monthly_avg": "Monthly average",
        "parameter": "Parameter",
        "custom_param": "CUSTOM (enter NASA POWER code)",
        "custom_param_code": "NASA POWER parameter code",
        "location_preset": "Location (preset)",
        "custom_location": "Custom location (lat/lon)",
        "latitude": "Latitude (lat)",
        "longitude": "Longitude (lon)",
        "location_name": "Location name",
        "start_year": "Start year",
        "start_month": "Start month",
        "end_year": "End year",
        "end_month": "End month",
        "months_filter": "Months to include in analysis (empty = all)",
        "compare_scan": "Quick comparison across preset locations (trend scan)",
        "scan_group": "Scan group",
        "scan_count": "Number of locations to scan",
        "scan_help": "In MySQL mode processed data is scanned quickly; locations in the selected group can be scanned.",
        "wide_mode": "Wide period demo (1981–2025)",
        "fetching_data": "Fetching and analyzing data...",
        "scanning": "Scanning preset locations...",
        "tab_map": "🗺️ Map & Overview",
        "tab_trends": "📈 Trends & Statistics",
        "tab_data": "📋 Data Table",
        "tab_methods": "🧪 Methodology & Sources",
        "tab_presentation": "🎤 Presentation",
        "selected_location": "Selected location",
        "coordinate": "Coordinate",
        "period": "Period",
        "source": "Source",
        "average": "Average",
        "maximum": "Maximum",
        "minimum": "Minimum",
        "trend_10y": "Trend (10 years)",
        "point_analysis": "Point analysis (selected/comparison)",
        "global_heatmap": "Global heatmap (year/month)",
        "globe": "Globe",
        "worldbank_shortcut": "Carbon & Energy Context (World Bank) — Shortcut",
        "wb_info": "World Bank data for the selected indicator and country is fetched live and summarized.",
        "wb_fetch": "Fetch and process World Bank data",
        "wb_fetching": "Fetching World Bank data...",
        "download_csv": "Download data as CSV",
        "save_sqlite": "Save this series to SQLite database",
        "saved_sqlite": "Saved to SQLite database.",
        "presentation_title": "Data-driven Presentation",
        "presentation_download": "Download presentation (HTML, printable/PDF)",
        "print_pdf_hint": "To get a PDF, use Print (Ctrl+P) in your browser and choose Save as PDF.",
        "no_data": "No data found for the selected criteria.",
        "sim_note": "Simulation mode: This data is for demo purposes only, not a scientific observation.",
        "ocean_note": "Note: In globe views oceans are shown in blue tones; without 3D/satellite texture they may appear dark. This is a visualization layer.",
        "significance": "Significance",
        "p_value": "p-value",
        "mk": "Mann-Kendall",
        "ci95": "95% CI (10 years)",
        "methodology_title": "Methodology",
        "sources_title": "Sources",
        "limitations_title": "Limitations and Data Quality",
        "radiation_title": "Radiation and Ecosystem Impacts",
        "data_table_title": "Data Table",
        "chart_time_series": "Time Series",
        "chart_anomaly": "Yearly Anomaly",
        "chart_trend": "Trend Line",
        "records": "Records",
        "group_tr": "Turkey",
        "group_world": "World",
        "group_capitals": "World Capitals",
        "group_all": "All",
        "nasa_data_used": "NASA Data Used",
        "data_volume": "Analyzed Data Volume",
        "problematic_data": "Problematic/Missing Data and Effects",
        "country_avg": "Country Averages and Heat Change",
        "radiation_section": "Radiation Data: Ecosystem Benefits and Harms",
    },
    "de": {
        "language": "Sprache","app_subtitle":"Erkunden Sie Veränderungen, Ausmaß und Signifikanz von Klimaindikatoren mit offenen NASA-Daten.",
        "hero_source":"Primärdaten: NASA POWER • Ergänzend: World Bank Open Data • Modus: Echte Daten / MySQL / Simulation",
        "control_panel":"Steuerung","data_source_mode":"Datenquellenmodus","mode_mysql":"MySQL (Verarbeitete Daten)","mode_nasa":"NASA POWER (Echte Daten)","mode_sim":"Simulation (Offline/Demo)",
        "mysql_ok":"MySQL-Verbindung/Schema bereit: sayriks_earth_trend_detective","mysql_note":"Datenbank: sayriks_earth_trend_detective (nasa_power_raw)","mysql_missing":"MySQL .env oder Verbindung nicht gefunden; NASA/Simulation nutzbar.",
        "time_resolution":"Zeitauflösung (Analyse)","daily":"Täglich","monthly_avg":"Monatlicher Durchschnitt","parameter":"Parameter","custom_param":"BENUTZERDEFINIERT (NASA POWER-Code)","custom_param_code":"NASA POWER Parametercode",
        "location_preset":"Ort (Vorgabe)","custom_location":"Benutzerdefinierter Ort (Breite/Länge)","latitude":"Breitengrad (lat)","longitude":"Längengrad (lon)","location_name":"Ortsname",
        "start_year":"Startjahr","start_month":"Startmonat","end_year":"Endjahr","end_month":"Endmonat","months_filter":"Monate in der Analyse (leer = alle)",
        "compare_scan":"Schneller Vergleich vordefinierter Orte (Trend-Scan)","scan_group":"Scan-Gruppe","scan_count":"Anzahl der zu scannenden Orte","scan_help":"Im MySQL-Modus werden verarbeitete Daten schnell gescannt.","wide_mode":"Demo langer Zeitraum (1981–2025)",
        "fetching_data":"Daten werden abgerufen und analysiert...","scanning":"Vordefinierte Orte werden gescannt...",
        "tab_map":"🗺️ Karte & Überblick","tab_trends":"📈 Trends & Statistik","tab_data":"📋 Datentabelle","tab_methods":"🧪 Methodik & Quellen","tab_presentation":"🎤 Präsentation",
        "selected_location":"Ausgewählter Ort","coordinate":"Koordinate","period":"Zeitraum","source":"Quelle","average":"Durchschnitt","maximum":"Maximum","minimum":"Minimum","trend_10y":"Trend (10 Jahre)",
        "point_analysis":"Punktanalyse (Auswahl/Vergleich)","global_heatmap":"Globale Wärmekarte (Jahr/Monat)","globe":"Globus","worldbank_shortcut":"Kohlenstoff- & Energiekontext (Weltbank) — Schnellzugriff",
        "wb_info":"Weltbankdaten werden live abgerufen und zusammengefasst.","wb_fetch":"Weltbankdaten abrufen und verarbeiten","wb_fetching":"Weltbankdaten werden abgerufen...",
        "download_csv":"Daten als CSV herunterladen","save_sqlite":"Diese Reihe in SQLite speichern","saved_sqlite":"In SQLite gespeichert.",
        "presentation_title":"Datenbasierte Präsentation","presentation_download":"Präsentation herunterladen (HTML, druckbar/PDF)","print_pdf_hint":"Für PDF im Browser Drucken (Strg+P) und Als PDF speichern.",
        "no_data":"Keine Daten gefunden.","sim_note":"Simulationsmodus: Nur Demo, keine wissenschaftliche Beobachtung.","ocean_note":"Hinweis: Ozeane in Globusansichten sind blau dargestellt; ohne 3D-Textur können sie dunkel wirken.",
        "significance":"Signifikanz","p_value":"p-Wert","mk":"Mann-Kendall","ci95":"95%-KI (10 Jahre)","methodology_title":"Methodik","sources_title":"Quellen","limitations_title":"Einschränkungen und Datenqualität",
        "radiation_title":"Strahlung und Ökosystemauswirkungen","data_table_title":"Datentabelle","chart_time_series":"Zeitreihe","chart_anomaly":"Jährliche Anomalie","chart_trend":"Trendlinie","records":"Datensätze",
        "group_tr":"Türkei","group_world":"Welt","group_capitals":"Welthauptstädte","group_all":"Alle",
        "nasa_data_used":"Verwendete NASA-Daten","data_volume":"Analysiertes Datenvolumen","problematic_data":"Problematische/fehlende Daten und Auswirkungen","country_avg":"Länderdurchschnitte und Wärmeänderung","radiation_section":"Strahlungsdaten: Nutzen und Schäden für Ökosysteme",
    },
    "fr": {
        "language":"Langue","app_subtitle":"Explorez le changement, l'ampleur et la signification des indicateurs climatiques avec les données ouvertes de la NASA.",
        "hero_source":"Données principales : NASA POWER • Complément : World Bank Open Data • Mode : Données réelles / MySQL / Simulation",
        "control_panel":"Panneau de contrôle","data_source_mode":"Mode de source de données","mode_mysql":"MySQL (Données traitées)","mode_nasa":"NASA POWER (Données réelles)","mode_sim":"Simulation (Hors ligne/Démo)",
        "mysql_ok":"Connexion/schéma MySQL prêt : sayriks_earth_trend_detective","mysql_note":"Base de données : sayriks_earth_trend_detective (nasa_power_raw)","mysql_missing":"Fichier .env MySQL ou connexion introuvable ; NASA/Simulation utilisables.",
        "time_resolution":"Résolution temporelle (analyse)","daily":"Quotidien","monthly_avg":"Moyenne mensuelle","parameter":"Paramètre","custom_param":"PERSONNALISÉ (code NASA POWER)","custom_param_code":"Code du paramètre NASA POWER",
        "location_preset":"Lieu (prédéfini)","custom_location":"Lieu personnalisé (lat/lon)","latitude":"Latitude (lat)","longitude":"Longitude (lon)","location_name":"Nom du lieu",
        "start_year":"Année de début","start_month":"Mois de début","end_year":"Année de fin","end_month":"Mois de fin","months_filter":"Mois à inclure (vide = tous)",
        "compare_scan":"Comparaison rapide des lieux prédéfinis (scan de tendance)","scan_group":"Groupe de scan","scan_count":"Nombre de lieux à scanner","scan_help":"En mode MySQL, les données traitées sont scannées rapidement.","wide_mode":"Démo longue période (1981–2025)",
        "fetching_data":"Récupération et analyse des données...","scanning":"Analyse des lieux prédéfinis...",
        "tab_map":"🗺️ Carte & Vue d'ensemble","tab_trends":"📈 Tendances & Statistiques","tab_data":"📋 Tableau de données","tab_methods":"🧪 Méthodologie & Sources","tab_presentation":"🎤 Présentation",
        "selected_location":"Lieu sélectionné","coordinate":"Coordonnée","period":"Période","source":"Source","average":"Moyenne","maximum":"Maximum","minimum":"Minimum","trend_10y":"Tendance (10 ans)",
        "point_analysis":"Analyse ponctuelle (sélection/comparaison)","global_heatmap":"Carte thermique mondiale (année/mois)","globe":"Globe","worldbank_shortcut":"Contexte carbone & énergie (Banque mondiale) — Raccourci",
        "wb_info":"Les données de la Banque mondiale sont récupérées en direct.","wb_fetch":"Récupérer et traiter les données","wb_fetching":"Récupération des données...",
        "download_csv":"Télécharger les données en CSV","save_sqlite":"Enregistrer dans SQLite","saved_sqlite":"Enregistré dans SQLite.",
        "presentation_title":"Présentation basée sur les données","presentation_download":"Télécharger la présentation (HTML, imprimable/PDF)","print_pdf_hint":"Pour un PDF, utilisez Imprimer (Ctrl+P) et choisissez Enregistrer au format PDF.",
        "no_data":"Aucune donnée trouvée.","sim_note":"Mode simulation : démo uniquement, pas une observation scientifique.","ocean_note":"Remarque : les océans sont affichés en bleu sur le globe ; sans texture 3D ils peuvent paraître sombres.",
        "significance":"Signification","p_value":"valeur p","mk":"Mann-Kendall","ci95":"IC 95 % (10 ans)","methodology_title":"Méthodologie","sources_title":"Sources","limitations_title":"Limites et qualité des données",
        "radiation_title":"Rayonnement et impacts sur l'écosystème","data_table_title":"Tableau de données","chart_time_series":"Série temporelle","chart_anomaly":"Anomalie annuelle","chart_trend":"Ligne de tendance","records":"Enregistrements",
        "group_tr":"Turquie","group_world":"Monde","group_capitals":"Capitales mondiales","group_all":"Tous",
        "nasa_data_used":"Données NASA utilisées","data_volume":"Volume de données analysées","problematic_data":"Données problématiques/manquantes et effets","country_avg":"Moyennes par pays et changement thermique","radiation_section":"Données de rayonnement : bénéfices et nuisances pour l'écosystème",
    },
    "it": {
        "language":"Lingua","app_subtitle":"Esplora cambiamento, entità e significatività degli indicatori climatici con i dati aperti NASA.",
        "hero_source":"Dati principali: NASA POWER • Supporto: World Bank Open Data • Modalità: Dati reali / MySQL / Simulazione",
        "control_panel":"Pannello di controllo","data_source_mode":"Modalità sorgente dati","mode_mysql":"MySQL (Dati elaborati)","mode_nasa":"NASA POWER (Dati reali)","mode_sim":"Simulazione (Offline/Demo)",
        "mysql_ok":"Connessione/schema MySQL pronto: sayriks_earth_trend_detective","mysql_note":"Database: sayriks_earth_trend_detective (nasa_power_raw)","mysql_missing":"File .env MySQL o connessione non trovati; NASA/Simulazione utilizzabili.",
        "time_resolution":"Risoluzione temporale (analisi)","daily":"Giornaliero","monthly_avg":"Media mensile","parameter":"Parametro","custom_param":"PERSONALIZZATO (codice NASA POWER)","custom_param_code":"Codice parametro NASA POWER",
        "location_preset":"Località (predefinita)","custom_location":"Località personalizzata (lat/lon)","latitude":"Latitudine (lat)","longitude":"Longitudine (lon)","location_name":"Nome località",
        "start_year":"Anno iniziale","start_month":"Mese iniziale","end_year":"Anno finale","end_month":"Mese finale","months_filter":"Mesi da includere (vuoto = tutti)",
        "compare_scan":"Confronto rapido tra località predefinite (scan tendenza)","scan_group":"Gruppo di scansione","scan_count":"Numero di località da scansionare","scan_help":"In modalità MySQL i dati elaborati vengono scansionati rapidamente.","wide_mode":"Demo periodo ampio (1981–2025)",
        "fetching_data":"Recupero e analisi dei dati...","scanning":"Scansione delle località predefinite...",
        "tab_map":"🗺️ Mappa & Panoramica","tab_trends":"📈 Tendenze & Statistiche","tab_data":"📋 Tabella dati","tab_methods":"🧪 Metodologia & Fonti","tab_presentation":"🎤 Presentazione",
        "selected_location":"Località selezionata","coordinate":"Coordinate","period":"Periodo","source":"Fonte","average":"Media","maximum":"Massimo","minimum":"Minimo","trend_10y":"Tendenza (10 anni)",
        "point_analysis":"Analisi puntuale (selezione/confronto)","global_heatmap":"Mappa termica globale (anno/mese)","globe":"Globo","worldbank_shortcut":"Contesto carbonio ed energia (Banca Mondiale) — Scorciatoia",
        "wb_info":"I dati della Banca Mondiale vengono recuperati in tempo reale.","wb_fetch":"Recupera ed elabora i dati","wb_fetching":"Recupero dati...",
        "download_csv":"Scarica dati in CSV","save_sqlite":"Salva in SQLite","saved_sqlite":"Salvato in SQLite.",
        "presentation_title":"Presentazione basata sui dati","presentation_download":"Scarica presentazione (HTML, stampabile/PDF)","print_pdf_hint":"Per un PDF, usa Stampa (Ctrl+P) e scegli Salva come PDF.",
        "no_data":"Nessun dato trovato.","sim_note":"Modalità simulazione: solo demo, non un'osservazione scientifica.","ocean_note":"Nota: gli oceani sono mostrati in blu nel globo; senza texture 3D possono apparire scuri.",
        "significance":"Significatività","p_value":"valore p","mk":"Mann-Kendall","ci95":"IC 95% (10 anni)","methodology_title":"Metodologia","sources_title":"Fonti","limitations_title":"Limitazioni e qualità dei dati",
        "radiation_title":"Radiazione e impatti sull'ecosistema","data_table_title":"Tabella dati","chart_time_series":"Serie temporale","chart_anomaly":"Anomalia annuale","chart_trend":"Linea di tendenza","records":"Record",
        "group_tr":"Turchia","group_world":"Mondo","group_capitals":"Capitali mondiali","group_all":"Tutti",
        "nasa_data_used":"Dati NASA utilizzati","data_volume":"Volume di dati analizzati","problematic_data":"Dati problematici/mancanti ed effetti","country_avg":"Medie per paese e variazione termica","radiation_section":"Dati di radiazione: benefici e danni per l'ecosistema",
    },
}
LANG_LABELS = {"tr": "Türkçe", "en": "English", "de": "Deutsch", "fr": "Français", "it": "Italiano"}

PARAMETERS = {
    "T2M": {"label": "T2M — 2m Temperature (°C)", "unit": "°C"},
    "T2M_MAX": {"label": "T2M_MAX — 2m Max Temperature (°C)", "unit": "°C"},
    "T2M_MIN": {"label": "T2M_MIN — 2m Min Temperature (°C)", "unit": "°C"},
    "T2MDEW": {"label": "T2MDEW — Dew/Frost Point (°C)", "unit": "°C"},
    "TS": {"label": "TS — Earth Skin Temperature (°C)", "unit": "°C"},
    "RH2M": {"label": "RH2M — Relative Humidity (%)", "unit": "%"},
    "QV2M": {"label": "QV2M — Specific Humidity (g/kg)", "unit": "g/kg"},
    "PRECTOTCORR": {"label": "PRECTOTCORR — Precipitation (mm/day)", "unit": "mm/day"},
    "GWETTOP": {"label": "GWETTOP — Surface Soil Wetness (0-1)", "unit": "0-1"},
    "GWETROOT": {"label": "GWETROOT — Root Zone Soil Wetness (0-1)", "unit": "0-1"},
    "GWETPROF": {"label": "GWETPROF — Profile Soil Moisture (0-1)", "unit": "0-1"},
    "EVLAND": {"label": "EVLAND — Evaporation Land", "unit": "kg/m²/s"},
    "EVPTRNS": {"label": "EVPTRNS — Evapotranspiration Energy Flux", "unit": "W/m²"},
    "ALLSKY_SFC_SW_DWN": {"label": "ALLSKY_SFC_SW_DWN — All Sky Surface Shortwave Downward Irradiance", "unit": "kW-hr/m²/day"},
    "CLRSKY_SFC_SW_DWN": {"label": "CLRSKY_SFC_SW_DWN — Clear Sky Surface Shortwave Downward Irradiance", "unit": "kW-hr/m²/day"},
    "ALLSKY_SFC_LW_DWN": {"label": "ALLSKY_SFC_LW_DWN — All Sky Surface Longwave Downward Irradiance", "unit": "W/m²"},
    "TOA_SW_DWN": {"label": "TOA_SW_DWN — TOA Shortwave Downward Irradiance", "unit": "kW-hr/m²/day"},
    "ALLSKY_SFC_UV_INDEX": {"label": "ALLSKY_SFC_UV_INDEX — All Sky Surface UV Index", "unit": "index"},
    "ALLSKY_SFC_PAR_TOT": {"label": "ALLSKY_SFC_PAR_TOT — All Sky Surface PAR Total", "unit": "W/m²"},
    "WS2M": {"label": "WS2M — Wind Speed at 2m (m/s)", "unit": "m/s"},
    "WS10M": {"label": "WS10M — Wind Speed at 10m (m/s)", "unit": "m/s"},
    "WD2M": {"label": "WD2M — Wind Direction at 2m (°)", "unit": "°"},
    "WD10M": {"label": "WD10M — Wind Direction at 10m (°)", "unit": "°"},
    "WS2M_MAX": {"label": "WS2M_MAX — Max Wind Speed at 2m (m/s)", "unit": "m/s"},
    "WS2M_MIN": {"label": "WS2M_MIN — Min Wind Speed at 2m (m/s)", "unit": "m/s"},
    "PS": {"label": "PS — Surface Pressure (kPa)", "unit": "kPa"},
    "CLOUD_AMT": {"label": "CLOUD_AMT — Cloud Amount (%)", "unit": "%"},
    "CLOUD_AMT_DAY": {"label": "CLOUD_AMT_DAY — Daytime Cloud Amount (%)", "unit": "%"},
    "TQV": {"label": "TQV — Precipitable Water (cm)", "unit": "cm"},
    "AOD_55": {"label": "AOD_55 — Aerosol Optical Depth 55", "unit": "-"},
    "FROST_DAYS": {"label": "FROST_DAYS — Frost Days", "unit": "days"},
}

PRESET_LOCATIONS = [
    {"name": "Adana, Türkiye", "lat": 37.0, "lon": 35.3213, "group": "Türkiye", "type": "province"},
    {"name": "Adıyaman, Türkiye", "lat": 37.7648, "lon": 38.2786, "group": "Türkiye", "type": "province"},
    {"name": "Afyonkarahisar, Türkiye", "lat": 38.7507, "lon": 30.5567, "group": "Türkiye", "type": "province"},
    {"name": "Ağrı, Türkiye", "lat": 39.7191, "lon": 43.0503, "group": "Türkiye", "type": "province"},
    {"name": "Amasya, Türkiye", "lat": 40.6499, "lon": 35.8353, "group": "Türkiye", "type": "province"},
    {"name": "Ankara, Türkiye", "lat": 39.9334, "lon": 32.8597, "group": "Türkiye", "type": "province"},
    {"name": "Antalya, Türkiye", "lat": 36.8969, "lon": 30.7133, "group": "Türkiye", "type": "province"},
    {"name": "Artvin, Türkiye", "lat": 41.1828, "lon": 41.8183, "group": "Türkiye", "type": "province"},
    {"name": "Aydın, Türkiye", "lat": 37.856, "lon": 27.8416, "group": "Türkiye", "type": "province"},
    {"name": "Balıkesir, Türkiye", "lat": 39.6484, "lon": 27.8826, "group": "Türkiye", "type": "province"},
    {"name": "Bilecik, Türkiye", "lat": 40.0567, "lon": 30.0665, "group": "Türkiye", "type": "province"},
    {"name": "Bingöl, Türkiye", "lat": 38.8854, "lon": 40.498, "group": "Türkiye", "type": "province"},
    {"name": "Bitlis, Türkiye", "lat": 38.4006, "lon": 42.1095, "group": "Türkiye", "type": "province"},
    {"name": "Bolu, Türkiye", "lat": 40.735, "lon": 31.6061, "group": "Türkiye", "type": "province"},
    {"name": "Burdur, Türkiye", "lat": 37.7203, "lon": 30.2906, "group": "Türkiye", "type": "province"},
    {"name": "Bursa, Türkiye", "lat": 40.1885, "lon": 29.061, "group": "Türkiye", "type": "province"},
    {"name": "Çanakkale, Türkiye", "lat": 40.1553, "lon": 26.4142, "group": "Türkiye", "type": "province"},
    {"name": "Çankırı, Türkiye", "lat": 40.6013, "lon": 33.6134, "group": "Türkiye", "type": "province"},
    {"name": "Çorum, Türkiye", "lat": 40.5506, "lon": 34.9556, "group": "Türkiye", "type": "province"},
    {"name": "Denizli, Türkiye", "lat": 37.7765, "lon": 29.0864, "group": "Türkiye", "type": "province"},
    {"name": "Diyarbakır, Türkiye", "lat": 37.9144, "lon": 40.2306, "group": "Türkiye", "type": "province"},
    {"name": "Edirne, Türkiye", "lat": 41.6764, "lon": 26.5623, "group": "Türkiye", "type": "province"},
    {"name": "Elazığ, Türkiye", "lat": 38.681, "lon": 39.2264, "group": "Türkiye", "type": "province"},
    {"name": "Erzincan, Türkiye", "lat": 39.75, "lon": 39.5, "group": "Türkiye", "type": "province"},
    {"name": "Erzurum, Türkiye", "lat": 39.9055, "lon": 41.2658, "group": "Türkiye", "type": "province"},
    {"name": "Eskişehir, Türkiye", "lat": 39.7767, "lon": 30.5206, "group": "Türkiye", "type": "province"},
    {"name": "Gaziantep, Türkiye", "lat": 37.0662, "lon": 37.3833, "group": "Türkiye", "type": "province"},
    {"name": "Giresun, Türkiye", "lat": 40.9128, "lon": 38.3895, "group": "Türkiye", "type": "province"},
    {"name": "Gümüşhane, Türkiye", "lat": 40.4386, "lon": 39.5086, "group": "Türkiye", "type": "province"},
    {"name": "Hakkari, Türkiye", "lat": 37.5833, "lon": 43.7333, "group": "Türkiye", "type": "province"},
    {"name": "Hatay, Türkiye", "lat": 36.4018, "lon": 36.3498, "group": "Türkiye", "type": "province"},
    {"name": "Isparta, Türkiye", "lat": 37.7648, "lon": 30.5566, "group": "Türkiye", "type": "province"},
    {"name": "Mersin, Türkiye", "lat": 36.8121, "lon": 34.6415, "group": "Türkiye", "type": "province"},
    {"name": "İstanbul, Türkiye", "lat": 41.0082, "lon": 28.9784, "group": "Türkiye", "type": "province"},
    {"name": "İzmir, Türkiye", "lat": 38.4237, "lon": 27.1428, "group": "Türkiye", "type": "province"},
    {"name": "Kars, Türkiye", "lat": 40.6167, "lon": 43.1, "group": "Türkiye", "type": "province"},
    {"name": "Kastamonu, Türkiye", "lat": 41.3887, "lon": 33.7827, "group": "Türkiye", "type": "province"},
    {"name": "Kayseri, Türkiye", "lat": 38.7312, "lon": 35.4787, "group": "Türkiye", "type": "province"},
    {"name": "Kırklareli, Türkiye", "lat": 41.7333, "lon": 27.2167, "group": "Türkiye", "type": "province"},
    {"name": "Kırşehir, Türkiye", "lat": 39.1425, "lon": 34.1709, "group": "Türkiye", "type": "province"},
    {"name": "Kocaeli, Türkiye", "lat": 40.8533, "lon": 29.8815, "group": "Türkiye", "type": "province"},
    {"name": "Konya, Türkiye", "lat": 37.8746, "lon": 32.4932, "group": "Türkiye", "type": "province"},
    {"name": "Kütahya, Türkiye", "lat": 39.4167, "lon": 29.9833, "group": "Türkiye", "type": "province"},
    {"name": "Malatya, Türkiye", "lat": 38.3552, "lon": 38.3095, "group": "Türkiye", "type": "province"},
    {"name": "Manisa, Türkiye", "lat": 38.6191, "lon": 27.4289, "group": "Türkiye", "type": "province"},
    {"name": "Kahramanmaraş, Türkiye", "lat": 37.5858, "lon": 36.9371, "group": "Türkiye", "type": "province"},
    {"name": "Mardin, Türkiye", "lat": 37.3212, "lon": 40.7245, "group": "Türkiye", "type": "province"},
    {"name": "Muğla, Türkiye", "lat": 37.2153, "lon": 28.3636, "group": "Türkiye", "type": "province"},
    {"name": "Muş, Türkiye", "lat": 38.9462, "lon": 41.7539, "group": "Türkiye", "type": "province"},
    {"name": "Nevşehir, Türkiye", "lat": 38.6939, "lon": 34.6857, "group": "Türkiye", "type": "province"},
    {"name": "Niğde, Türkiye", "lat": 37.9667, "lon": 34.6833, "group": "Türkiye", "type": "province"},
    {"name": "Ordu, Türkiye", "lat": 40.9839, "lon": 37.8764, "group": "Türkiye", "type": "province"},
    {"name": "Rize, Türkiye", "lat": 41.0201, "lon": 40.5234, "group": "Türkiye", "type": "province"},
    {"name": "Sakarya, Türkiye", "lat": 40.694, "lon": 30.4358, "group": "Türkiye", "type": "province"},
    {"name": "Samsun, Türkiye", "lat": 41.2867, "lon": 36.33, "group": "Türkiye", "type": "province"},
    {"name": "Siirt, Türkiye", "lat": 37.9333, "lon": 41.95, "group": "Türkiye", "type": "province"},
    {"name": "Sinop, Türkiye", "lat": 42.0231, "lon": 35.1531, "group": "Türkiye", "type": "province"},
    {"name": "Sivas, Türkiye", "lat": 39.7477, "lon": 37.0179, "group": "Türkiye", "type": "province"},
    {"name": "Tekirdağ, Türkiye", "lat": 40.9833, "lon": 27.5167, "group": "Türkiye", "type": "province"},
    {"name": "Tokat, Türkiye", "lat": 40.3167, "lon": 36.55, "group": "Türkiye", "type": "province"},
    {"name": "Trabzon, Türkiye", "lat": 41.0015, "lon": 39.7178, "group": "Türkiye", "type": "province"},
    {"name": "Tunceli, Türkiye", "lat": 39.1079, "lon": 39.5401, "group": "Türkiye", "type": "province"},
    {"name": "Şanlıurfa, Türkiye", "lat": 37.1591, "lon": 38.7969, "group": "Türkiye", "type": "province"},
    {"name": "Uşak, Türkiye", "lat": 38.6823, "lon": 29.4082, "group": "Türkiye", "type": "province"},
    {"name": "Van, Türkiye", "lat": 38.4891, "lon": 43.4089, "group": "Türkiye", "type": "province"},
    {"name": "Yozgat, Türkiye", "lat": 39.8181, "lon": 34.8147, "group": "Türkiye", "type": "province"},
    {"name": "Zonguldak, Türkiye", "lat": 41.4564, "lon": 31.7987, "group": "Türkiye", "type": "province"},
    {"name": "Aksaray, Türkiye", "lat": 38.3687, "lon": 34.037, "group": "Türkiye", "type": "province"},
    {"name": "Bayburt, Türkiye", "lat": 40.2552, "lon": 40.2249, "group": "Türkiye", "type": "province"},
    {"name": "Karaman, Türkiye", "lat": 37.1759, "lon": 33.2287, "group": "Türkiye", "type": "province"},
    {"name": "Kırıkkale, Türkiye", "lat": 39.8468, "lon": 33.5153, "group": "Türkiye", "type": "province"},
    {"name": "Batman, Türkiye", "lat": 37.8812, "lon": 41.1351, "group": "Türkiye", "type": "province"},
    {"name": "Şırnak, Türkiye", "lat": 37.4187, "lon": 42.4918, "group": "Türkiye", "type": "province"},
    {"name": "Bartın, Türkiye", "lat": 41.6344, "lon": 32.3375, "group": "Türkiye", "type": "province"},
    {"name": "Ardahan, Türkiye", "lat": 41.1105, "lon": 42.7022, "group": "Türkiye", "type": "province"},
    {"name": "Iğdır, Türkiye", "lat": 39.9167, "lon": 44.0333, "group": "Türkiye", "type": "province"},
    {"name": "Yalova, Türkiye", "lat": 40.65, "lon": 29.2667, "group": "Türkiye", "type": "province"},
    {"name": "Karabük, Türkiye", "lat": 41.2061, "lon": 32.6204, "group": "Türkiye", "type": "province"},
    {"name": "Kilis, Türkiye", "lat": 36.7184, "lon": 37.1212, "group": "Türkiye", "type": "province"},
    {"name": "Osmaniye, Türkiye", "lat": 37.0742, "lon": 36.2478, "group": "Türkiye", "type": "province"},
    {"name": "Düzce, Türkiye", "lat": 40.8438, "lon": 31.1565, "group": "Türkiye", "type": "province"},
    {"name": "Kabil, Afganistan", "lat": 34.5553, "lon": 69.2075, "group": "Dünya", "type": "capital"},
    {"name": "Tiran, Arnavutluk", "lat": 41.3275, "lon": 19.8187, "group": "Dünya", "type": "capital"},
    {"name": "Cezayir, Cezayir", "lat": 36.7538, "lon": 3.0588, "group": "Dünya", "type": "capital"},
    {"name": "Buenos Aires, Arjantin", "lat": -34.6037, "lon": -58.3816, "group": "Dünya", "type": "capital"},
    {"name": "Erivan, Ermenistan", "lat": 40.1792, "lon": 44.4991, "group": "Dünya", "type": "capital"},
    {"name": "Bakü, Azerbaycan", "lat": 40.4093, "lon": 49.8671, "group": "Dünya", "type": "capital"},
    {"name": "Manama, Bahreyn", "lat": 26.2235, "lon": 50.5876, "group": "Dünya", "type": "capital"},
    {"name": "Dakka, Bangladeş", "lat": 23.8103, "lon": 90.4125, "group": "Dünya", "type": "capital"},
    {"name": "Minsk, Belarus", "lat": 53.9006, "lon": 27.559, "group": "Dünya", "type": "capital"},
    {"name": "Brüksel, Belçika", "lat": 50.8503, "lon": 4.3517, "group": "Dünya", "type": "capital"},
    {"name": "Saraybosna, Bosna-Hersek", "lat": 43.8563, "lon": 18.4131, "group": "Dünya", "type": "capital"},
    {"name": "Sofya, Bulgaristan", "lat": 42.6977, "lon": 23.3219, "group": "Dünya", "type": "capital"},
    {"name": "Ottawa, Kanada", "lat": 45.4215, "lon": -75.6972, "group": "Dünya", "type": "capital"},
    {"name": "Pekin, Çin", "lat": 39.9042, "lon": 116.4074, "group": "Dünya", "type": "capital"},
    {"name": "Zagreb, Hırvatistan", "lat": 45.815, "lon": 15.9819, "group": "Dünya", "type": "capital"},
    {"name": "Lefkoşa, Kıbrıs", "lat": 35.1856, "lon": 33.3823, "group": "Dünya", "type": "capital"},
    {"name": "Prag, Çekya", "lat": 50.0755, "lon": 14.4378, "group": "Dünya", "type": "capital"},
    {"name": "Kopenhag, Danimarka", "lat": 55.6761, "lon": 12.5683, "group": "Dünya", "type": "capital"},
    {"name": "Kahire, Mısır", "lat": 30.0444, "lon": 31.2357, "group": "Dünya", "type": "capital"},
    {"name": "Tallinn, Estonya", "lat": 59.437, "lon": 24.7536, "group": "Dünya", "type": "capital"},
    {"name": "Helsinki, Finlandiya", "lat": 60.1699, "lon": 24.9384, "group": "Dünya", "type": "capital"},
    {"name": "Paris, Fransa", "lat": 48.8566, "lon": 2.3522, "group": "Dünya", "type": "capital"},
    {"name": "Tiflis, Gürcistan", "lat": 41.7151, "lon": 44.8271, "group": "Dünya", "type": "capital"},
    {"name": "Berlin, Almanya", "lat": 52.52, "lon": 13.405, "group": "Dünya", "type": "capital"},
    {"name": "Atina, Yunanistan", "lat": 37.9838, "lon": 23.7275, "group": "Dünya", "type": "capital"},
    {"name": "Budapeşte, Macaristan", "lat": 47.4979, "lon": 19.0402, "group": "Dünya", "type": "capital"},
    {"name": "Reykjavik, İzlanda", "lat": 64.1466, "lon": -21.9426, "group": "Dünya", "type": "capital"},
    {"name": "Yeni Delhi, Hindistan", "lat": 28.6139, "lon": 77.209, "group": "Dünya", "type": "capital"},
    {"name": "Cakarta, Endonezya", "lat": -6.2088, "lon": 106.8456, "group": "Dünya", "type": "capital"},
    {"name": "Tahran, İran", "lat": 35.6892, "lon": 51.389, "group": "Dünya", "type": "capital"},
    {"name": "Bağdat, Irak", "lat": 33.3152, "lon": 44.3661, "group": "Dünya", "type": "capital"},
    {"name": "Dublin, İrlanda", "lat": 53.3498, "lon": -6.2603, "group": "Dünya", "type": "capital"},
    {"name": "Kudüs, İsrail", "lat": 31.7683, "lon": 35.2137, "group": "Dünya", "type": "capital"},
    {"name": "Roma, İtalya", "lat": 41.9028, "lon": 12.4964, "group": "Dünya", "type": "capital"},
    {"name": "Tokyo, Japonya", "lat": 35.6762, "lon": 139.6503, "group": "Dünya", "type": "capital"},
    {"name": "Amman, Ürdün", "lat": 31.9454, "lon": 35.9284, "group": "Dünya", "type": "capital"},
    {"name": "Astana, Kazakistan", "lat": 51.1694, "lon": 71.4491, "group": "Dünya", "type": "capital"},
    {"name": "Nairobi, Kenya", "lat": -1.2921, "lon": 36.8219, "group": "Dünya", "type": "capital"},
    {"name": "Kuveyt, Kuveyt", "lat": 29.3759, "lon": 47.9774, "group": "Dünya", "type": "capital"},
    {"name": "Bişkek, Kırgızistan", "lat": 42.8746, "lon": 74.5698, "group": "Dünya", "type": "capital"},
    {"name": "Riga, Letonya", "lat": 56.9496, "lon": 24.1052, "group": "Dünya", "type": "capital"},
    {"name": "Beyrut, Lübnan", "lat": 33.8938, "lon": 35.5018, "group": "Dünya", "type": "capital"},
    {"name": "Trablus, Libya", "lat": 32.8872, "lon": 13.1913, "group": "Dünya", "type": "capital"},
    {"name": "Vilnius, Litvanya", "lat": 54.6872, "lon": 25.2797, "group": "Dünya", "type": "capital"},
    {"name": "Lüksemburg, Lüksemburg", "lat": 49.6116, "lon": 6.1319, "group": "Dünya", "type": "capital"},
    {"name": "Kuala Lumpur, Malezya", "lat": 3.139, "lon": 101.6869, "group": "Dünya", "type": "capital"},
    {"name": "Mexico City, Meksika", "lat": 19.4326, "lon": -99.1332, "group": "Dünya", "type": "capital"},
    {"name": "Kişinev, Moldova", "lat": 47.0105, "lon": 28.8638, "group": "Dünya", "type": "capital"},
    {"name": "Ulan Batur, Moğolistan", "lat": 47.8864, "lon": 106.9057, "group": "Dünya", "type": "capital"},
    {"name": "Podgorica, Karadağ", "lat": 42.4304, "lon": 19.2594, "group": "Dünya", "type": "capital"},
    {"name": "Rabat, Fas", "lat": 34.0209, "lon": -6.8416, "group": "Dünya", "type": "capital"},
    {"name": "Amsterdam, Hollanda", "lat": 52.3676, "lon": 4.9041, "group": "Dünya", "type": "capital"},
    {"name": "Wellington, Yeni Zelanda", "lat": -41.2865, "lon": 174.7762, "group": "Dünya", "type": "capital"},
    {"name": "Abuja, Nijerya", "lat": 9.0765, "lon": 7.3986, "group": "Dünya", "type": "capital"},
    {"name": "Üsküp, Kuzey Makedonya", "lat": 41.9981, "lon": 21.4254, "group": "Dünya", "type": "capital"},
    {"name": "Oslo, Norveç", "lat": 59.9139, "lon": 10.7522, "group": "Dünya", "type": "capital"},
    {"name": "Maskat, Umman", "lat": 23.588, "lon": 58.3829, "group": "Dünya", "type": "capital"},
    {"name": "İslamabad, Pakistan", "lat": 33.6844, "lon": 73.0479, "group": "Dünya", "type": "capital"},
    {"name": "Lima, Peru", "lat": -12.0464, "lon": -77.0428, "group": "Dünya", "type": "capital"},
    {"name": "Manila, Filipinler", "lat": 14.5995, "lon": 120.9842, "group": "Dünya", "type": "capital"},
    {"name": "Varşova, Polonya", "lat": 52.2297, "lon": 21.0122, "group": "Dünya", "type": "capital"},
    {"name": "Lizbon, Portekiz", "lat": 38.7223, "lon": -9.1393, "group": "Dünya", "type": "capital"},
    {"name": "Doha, Katar", "lat": 25.2854, "lon": 51.531, "group": "Dünya", "type": "capital"},
    {"name": "Bükreş, Romanya", "lat": 44.4268, "lon": 26.1025, "group": "Dünya", "type": "capital"},
    {"name": "Moskova, Rusya", "lat": 55.7558, "lon": 37.6173, "group": "Dünya", "type": "capital"},
    {"name": "Riyad, Suudi Arabistan", "lat": 24.7136, "lon": 46.6753, "group": "Dünya", "type": "capital"},
    {"name": "Belgrad, Sırbistan", "lat": 44.7866, "lon": 20.4489, "group": "Dünya", "type": "capital"},
    {"name": "Singapur, Singapur", "lat": 1.3521, "lon": 103.8198, "group": "Dünya", "type": "capital"},
    {"name": "Bratislava, Slovakya", "lat": 48.1486, "lon": 17.1077, "group": "Dünya", "type": "capital"},
    {"name": "Ljubljana, Slovenya", "lat": 46.0569, "lon": 14.5058, "group": "Dünya", "type": "capital"},
    {"name": "Pretoria, Güney Afrika", "lat": -25.7479, "lon": 28.2293, "group": "Dünya", "type": "capital"},
    {"name": "Seul, Güney Kore", "lat": 37.5665, "lon": 126.978, "group": "Dünya", "type": "capital"},
    {"name": "Madrid, İspanya", "lat": 40.4168, "lon": -3.7038, "group": "Dünya", "type": "capital"},
    {"name": "Stockholm, İsveç", "lat": 59.3293, "lon": 18.0686, "group": "Dünya", "type": "capital"},
    {"name": "Bern, İsviçre", "lat": 46.948, "lon": 7.4474, "group": "Dünya", "type": "capital"},
    {"name": "Şam, Suriye", "lat": 33.5138, "lon": 36.2765, "group": "Dünya", "type": "capital"},
    {"name": "Taipei, Tayvan", "lat": 25.033, "lon": 121.5654, "group": "Dünya", "type": "capital"},
    {"name": "Bangkok, Tayland", "lat": 13.7563, "lon": 100.5018, "group": "Dünya", "type": "capital"},
    {"name": "Tunus, Tunus", "lat": 36.8065, "lon": 10.1815, "group": "Dünya", "type": "capital"},
    {"name": "Kiev, Ukrayna", "lat": 50.4501, "lon": 30.5234, "group": "Dünya", "type": "capital"},
    {"name": "Abu Dabi, BAE", "lat": 24.4539, "lon": 54.3773, "group": "Dünya", "type": "capital"},
    {"name": "Londra, Birleşik Krallık", "lat": 51.5074, "lon": -0.1278, "group": "Dünya", "type": "capital"},
    {"name": "Washington DC, ABD", "lat": 38.8951, "lon": -77.0364, "group": "Dünya", "type": "capital"},
    {"name": "Taşkent, Özbekistan", "lat": 41.2995, "lon": 69.2401, "group": "Dünya", "type": "capital"},
    {"name": "Hanoi, Vietnam", "lat": 21.0278, "lon": 105.8342, "group": "Dünya", "type": "capital"},
    {"name": "Sana, Yemen", "lat": 15.3694, "lon": 44.191, "group": "Dünya", "type": "capital"},
    {"name": "Brasilia, Brezilya", "lat": -15.8267, "lon": -47.9218, "group": "Dünya", "type": "capital"},
    {"name": "Canberra, Avustralya", "lat": -35.2809, "lon": 149.13, "group": "Dünya", "type": "capital"},
]

def tr(lang):
    return I18N.get(lang, I18N["tr"])


def _mysql_env():
    base = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base, ".env")
    env = {}
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
        except Exception:
            pass
    return env


def _mysql_ok():
    env = _mysql_env()
    return bool(env.get("MYSQL_HOST") and env.get("MYSQL_USER"))


@st.cache_data(ttl=120, show_spinner=False)
def get_mysql_overview():
    if not _mysql_ok():
        return None
    try:
        import pymysql
        env = _mysql_env()
        conn = pymysql.connect(
            host=env.get("MYSQL_HOST"), port=int(env.get("MYSQL_PORT", 3306)),
            user=env.get("MYSQL_USER"), password=env.get("MYSQL_PASSWORD"),
            database=env.get("MYSQL_DATABASE", "sayriks_earth_trend_detective"), connect_timeout=8,
        )
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM nasa_power_raw")
            total_rows = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM locations")
            locs = cur.fetchone()[0]
            cur.execute("SELECT COUNT(DISTINCT parameter) FROM nasa_power_raw")
            params = cur.fetchone()[0]
            cur.execute("SELECT MIN(date), MAX(date) FROM nasa_power_raw")
            dmin, dmax = cur.fetchone()
            cur.execute("SELECT COUNT(*) FROM analysis_results")
            analyses = cur.fetchone()[0]
            cur.execute("SELECT parameter, COUNT(*) c FROM nasa_power_raw GROUP BY parameter ORDER BY c DESC LIMIT 8")
            top_params = cur.fetchall()
            return {
                "total_rows": total_rows, "locations": locs, "params": params,
                "date_min": dmin, "date_max": dmax, "analyses": analyses,
                "top_params": top_params,
            }
        finally:
            conn.close()
    except Exception as e:
        return {"error": str(e)}


@st.cache_data(ttl=300, show_spinner=False)
def get_country_averages_t2m(limit=120):
    if not _mysql_ok():
        return pd.DataFrame()
    try:
        import pymysql
        env = _mysql_env()
        conn = pymysql.connect(
            host=env.get("MYSQL_HOST"), port=int(env.get("MYSQL_PORT", 3306)),
            user=env.get("MYSQL_USER"), password=env.get("MYSQL_PASSWORD"),
            database=env.get("MYSQL_DATABASE", "sayriks_earth_trend_detective"), connect_timeout=8,
        )
        q = """
        SELECT l.country, l.name,
               AVG(CASE WHEN YEAR(r.date) <= 2000 THEN r.value END) as avg_early,
               AVG(CASE WHEN YEAR(r.date) >= 2015 THEN r.value END) as avg_late,
               AVG(r.value) as avg_all,
               COUNT(*) as n
        FROM nasa_power_raw r
        JOIN locations l ON l.id = r.location_id
        WHERE r.parameter = 'T2M'
        GROUP BY l.id, l.country, l.name
        HAVING n > 1000
        ORDER BY (avg_late - avg_early) DESC
        LIMIT %s
        """
        df = pd.read_sql(q, conn, params=(int(limit),))
        conn.close()
        if not df.empty:
            df["delta"] = df["avg_late"] - df["avg_early"]
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def get_radiation_country_summary(limit=80):
    if not _mysql_ok():
        return pd.DataFrame()
    try:
        import pymysql
        env = _mysql_env()
        conn = pymysql.connect(
            host=env.get("MYSQL_HOST"), port=int(env.get("MYSQL_PORT", 3306)),
            user=env.get("MYSQL_USER"), password=env.get("MYSQL_PASSWORD"),
            database=env.get("MYSQL_DATABASE", "sayriks_earth_trend_detective"), connect_timeout=8,
        )
        q = """
        SELECT l.name, l.country,
               AVG(CASE WHEN r.parameter='ALLSKY_SFC_SW_DWN' THEN r.value END) as sw_dwn,
               AVG(CASE WHEN r.parameter='ALLSKY_SFC_UV_INDEX' THEN r.value END) as uv_index,
               AVG(CASE WHEN r.parameter='T2M_MAX' THEN r.value END) as t2m_max,
               COUNT(*) as n
        FROM nasa_power_raw r
        JOIN locations l ON l.id = r.location_id
        WHERE r.parameter IN ('ALLSKY_SFC_SW_DWN','ALLSKY_SFC_UV_INDEX','T2M_MAX')
        GROUP BY l.id, l.name, l.country
        HAVING n > 500
        ORDER BY sw_dwn DESC
        LIMIT %s
        """
        df = pd.read_sql(q, conn, params=(int(limit),))
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


def generate_mock_data(lat, lon, start, end, parameter="T2M", seed_hint=""):
    np.random.seed(abs(hash(f"{seed_hint}{lat}{lon}{start}{end}{parameter}")) % (2**32))
    dates = pd.date_range(f"{start}-01-01", f"{end}-12-31", freq="D")
    idx = np.arange(len(dates))
    seasonal = np.sin(idx / 365.25 * 2 * np.pi)
    base = 15 - abs(lat) * 0.22
    slope = 0.00003 if "T2M" in parameter or parameter == "TS" else 0.00001
    noise = np.random.normal(0, 1.1, len(dates))
    values = base + seasonal * 8 + slope * idx + noise
    if parameter in ("RH2M", "CLOUD_AMT", "CLOUD_AMT_DAY"):
        values = np.clip(55 + seasonal * 10 + noise, 5, 100)
    if "PREC" in parameter:
        values = np.clip(np.random.gamma(1.5, 2.0, len(dates)), 0, None)
    if "WS" in parameter:
        values = np.clip(3 + np.abs(noise), 0, None)
    if "UV" in parameter:
        values = np.clip(5 + seasonal * 3 + noise * 0.3, 0, 15)
    if "SW_DWN" in parameter or "PAR" in parameter or "TOA" in parameter:
        values = np.clip(4 + seasonal * 2 + noise * 0.2, 0, None)
    df = pd.DataFrame({"Date": dates, "Value": values})
    df["Temperature"] = df["Value"].astype(float)
    df["Parameter"] = parameter
    return df


def to_analysis_df(df, agg_mode, selected_months):
    if df is None or df.empty:
        return None
    d = df.copy()
    d["Date"] = pd.to_datetime(d["Date"], errors="coerce")
    d = d.dropna(subset=["Date", "Value"])
    if selected_months:
        d = d[d["Date"].dt.month.isin(selected_months)]
    if d.empty:
        return None
    if agg_mode == "monthly":
        d["YearMonth"] = d["Date"].dt.to_period("M").dt.to_timestamp()
        d = d.groupby("YearMonth", as_index=False)["Value"].mean().rename(columns={"YearMonth": "Date"})
    d["Temperature"] = d["Value"].astype(float)
    return d.sort_values("Date").reset_index(drop=True)


def fetch_data(lat, lon, start, end, parameter, start_month, end_month, mode, T, loc_name):
    label = f"{T['fetching_data']} ({parameter}, {loc_name}, {start}-{end})"
    with st.spinner(label):
        if mode == "mysql":
            df, err = fetch_mysql_series(lat, lon, start, end, parameter=parameter, start_month=start_month, end_month=end_month)
            if df is not None and not df.empty:
                return df, "MySQL (nasa_power_raw)", None
            df2, err2 = fetch_nasa_power_data(lat, lon, start, end, parameter=parameter, start_month=start_month, end_month=end_month)
            if df2 is not None and not df2.empty:
                return df2, "NASA POWER API (fallback)", err
            return generate_mock_data(lat, lon, start, end, parameter), "Simulation (fallback)", err or err2
        elif mode == "nasa":
            df, err = fetch_nasa_power_data(lat, lon, start, end, parameter=parameter, start_month=start_month, end_month=end_month)
            if df is not None and not df.empty:
                return df, "NASA POWER API", None
            return generate_mock_data(lat, lon, start, end, parameter), "Simulation (fallback)", err
        else:
            return generate_mock_data(lat, lon, start, end, parameter), "Simulation", None


def scan_locations(cands, start, end, parameter, start_month, end_month, mode, T):
    rows = []
    prog = st.progress(0, text=f"📡 {T['scanning']}")
    total = max(1, len(cands))
    for i, loc in enumerate(cands, start=1):
        prog.progress(i / total, text=f"📡 {T['scanning']} {i}/{total} — {loc['name']}")
        if mode == "mysql":
            df, _ = fetch_mysql_series(loc["lat"], loc["lon"], start, end, parameter=parameter, start_month=start_month, end_month=end_month)
            if df is None or df.empty:
                df, _ = fetch_nasa_power_data(loc["lat"], loc["lon"], start, end, parameter=parameter, start_month=start_month, end_month=end_month)
        elif mode == "nasa":
            df, _ = fetch_nasa_power_data(loc["lat"], loc["lon"], start, end, parameter=parameter, start_month=start_month, end_month=end_month)
        else:
            df = generate_mock_data(loc["lat"], loc["lon"], start, end, parameter, seed_hint=loc["name"])
        adf = to_analysis_df(df, "monthly", [])
        stats_res = calculate_trend_and_stats(adf)
        if stats_res:
            rows.append({"name": loc["name"], "lat": loc["lat"], "lon": loc["lon"], "group": loc.get("group", ""), "trend_10y": stats_res.get("slope_per_decade"), "p_value": stats_res.get("p_value"), "mean": stats_res.get("mean"), "mk_trend": stats_res.get("mk_trend")})
    prog.empty()
    return pd.DataFrame(rows)


def build_globe(scan_df, lat, lon, loc_name, value_col, title, colorbar_title):
    if scan_df is not None and not scan_df.empty and value_col in scan_df.columns:
        plot_df = scan_df.copy()
    else:
        plot_df = pd.DataFrame([{"name": loc_name, "lat": lat, "lon": lon, value_col: 0.0}])
    fig = px.scatter_geo(plot_df, lat="lat", lon="lon", hover_name="name", color=value_col, color_continuous_scale="RdYlBu_r", projection="orthographic", title=title)
    fig.update_geos(showland=True, landcolor="#2f3e34", showocean=True, oceancolor="#1e3a5f", showlakes=True, lakecolor="#2b5d8a", showcountries=True, countrycolor="#6b7280", bgcolor="rgba(0,0,0,0)", lataxis_showgrid=True, lonaxis_showgrid=True)
    fig.update_layout(height=520, margin=dict(l=0, r=0, t=36, b=0), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#1f2937"), coloraxis_colorbar=dict(title=colorbar_title, thickness=12, len=0.72, x=1.01))
    fig.update_traces(marker=dict(size=7, line=dict(width=0.4, color="#111827"), opacity=0.9))
    fig.update_geos(projection_rotation=dict(lon=float(lon), lat=max(min(float(lat), 55), -55), roll=0))
    return fig


def fig_to_b64(fig):
    try:
        return base64.b64encode(fig.to_image(format="png", width=900, height=450, scale=1)).decode("ascii")
    except Exception:
        return ""


def fetch_world_bank(country_code, indicator, start, end):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json&date={start}:{end}&per_page=2000"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    js = r.json()
    if not isinstance(js, list) or len(js) < 2 or not js[1]:
        return pd.DataFrame()
    rows = []
    for it in js[1]:
        if it.get("value") is None:
            continue
        rows.append({"year": int(it.get("date")), "value": float(it.get("value")), "country": it.get("country", {}).get("value", country_code)})
    return pd.DataFrame(rows).sort_values("year")


def save_series_sqlite(df, param, loc_name, lat, lon, source):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "earth_database.db")
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS saved_series (id INTEGER PRIMARY KEY AUTOINCREMENT, saved_at TEXT, param TEXT, loc_name TEXT, lat REAL, lon REAL, source TEXT, date TEXT, value REAL)")
        now = datetime.utcnow().isoformat()
        rows = [(now, param, loc_name, lat, lon, source, str(pd.to_datetime(d).date()), float(v)) for d, v in zip(df["Date"], df["Value"])]
        cur.executemany("INSERT INTO saved_series (saved_at,param,loc_name,lat,lon,source,date,value) VALUES (?,?,?,?,?,?,?,?)", rows)
        conn.commit()
        return len(rows)
    finally:
        conn.close()



def build_presentation_html(T, lang, parameter, unit, loc_name, period_label, source, stats_res, analysis_df, scan_df, db_overview, country_avg_df, rad_df, figs_b64):
    def esc(x):
        return str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    current_n = int(len(analysis_df)) if analysis_df is not None else 0
    db_rows = db_overview.get("total_rows") if isinstance(db_overview, dict) else None
    db_locs = db_overview.get("locations") if isinstance(db_overview, dict) else None
    db_params = db_overview.get("params") if isinstance(db_overview, dict) else None
    db_min = db_overview.get("date_min") if isinstance(db_overview, dict) else None
    db_max = db_overview.get("date_max") if isinstance(db_overview, dict) else None
    db_analyses = db_overview.get("analyses") if isinstance(db_overview, dict) else None
    trend = stats_res.get("slope_per_decade") if stats_res else None
    pval = stats_res.get("p_value") if stats_res else None
    mk = stats_res.get("mk_trend") if stats_res else "-"
    sig = stats_res.get("significance") if stats_res else "-"
    ci = stats_res.get("slope_ci95_decade") if stats_res else None
    r2 = stats_res.get("r_squared") if stats_res else None

    country_rows = ""
    if country_avg_df is not None and not country_avg_df.empty:
        for _, r in country_avg_df.head(20).iterrows():
            ae = r.get("avg_early"); al = r.get("avg_late"); de = r.get("delta")
            country_rows += f"<tr><td>{esc(r.get('name',''))}</td><td>{esc(r.get('country',''))}</td><td>{'' if pd.isna(ae) else f'{ae:.2f}'}</td><td>{'' if pd.isna(al) else f'{al:.2f}'}</td><td>{'' if pd.isna(de) else f'{de:.2f}'}</td></tr>"
    rad_rows = ""
    if rad_df is not None and not rad_df.empty:
        for _, r in rad_df.head(15).iterrows():
            sw=r.get('sw_dwn'); uv=r.get('uv_index'); tm=r.get('t2m_max')
            rad_rows += f"<tr><td>{esc(r.get('name',''))}</td><td>{'' if pd.isna(sw) else f'{sw:.2f}'}</td><td>{'' if pd.isna(uv) else f'{uv:.2f}'}</td><td>{'' if pd.isna(tm) else f'{tm:.2f}'}</td></tr>"

    scan_rows = ""
    if scan_df is not None and not scan_df.empty:
        cols = [c for c in ["name","group","trend_10y","p_value","mean","mk_trend"] if c in scan_df.columns]
        for _, r in scan_df.sort_values("trend_10y", ascending=False, na_position="last").head(20).iterrows():
            scan_rows += "<tr>" + "".join(f"<td>{esc(r.get(c,''))}</td>" for c in cols) + "</tr>"
        scan_head = "".join(f"<th>{esc(c)}</th>" for c in cols)
    else:
        scan_head = "<th>name</th><th>trend_10y</th><th>p_value</th>"

    nasa_params = ", ".join(list(PARAMETERS.keys()))
    img_tags = [f'<div class="imgbox"><img src="data:image/png;base64,{b}"/></div>' for b in figs_b64 if b]
    while len(img_tags) < 3:
        img_tags.append('<div class="imgbox note">Grafik secili analizden uretildiginde burada gosterilir.</div>')

    pages = []
    pages.append('<section class="page"><div class="hero"><h1>Earth Trend Detective - ' + esc(T["presentation_title"]) + '</h1>'
    + '<p><b>' + esc(parameter) + '</b> (' + esc(unit) + ') | ' + esc(loc_name) + ' | ' + esc(period_label) + '</p>'
    + '<p>' + esc(T["source"]) + ': ' + esc(source) + ' | NASA Space Apps 2026</p></div>'
    + '<div class="card"><h2>1. Amac ve Problem Tanimi</h2><ul>'
    + '<li>NASA acik verileriyle iklim/cevre gostergelerinde <b>ne degisti, nerede, ne kadar ve ne kadar anlamli</b> sorularini yanitlamak.</li>'
    + '<li>Trend (egim), p-degeri, %95 guven araligi ve Mann-Kendall ile bilimsel dayanak sunmak.</li>'
    + '<li>MySQL islenmis veri katmani, coklu dil arayuz, harita/kure gorselleri ve yazdirilabilir sunum/rapor ciktilari saglamak.</li></ul></div></section>')

    pages.append('<section class="page"><div class="card"><h2>2. ' + esc(T["nasa_data_used"]) + '</h2><ul>'
    + '<li><b>Ana kaynak:</b> NASA POWER Daily Point API (<code>community=RE</code>, gunluk nokta zaman serileri).</li>'
    + '<li><b>Kullanilan parametre seti (36):</b> ' + esc(nasa_params) + '.</li>'
    + '<li><b>Veritabani donemi:</b> ' + esc(db_min) + ' - ' + esc(db_max) + ' (<code>nasa_power_raw</code>).</li>'
    + '<li><b>Lokasyon kapsami:</b> Turkiye 81 il + ek dunya ulkeleri/baskentleri (201 preset lokasyon hedefi).</li>'
    + '<li><b>Ek baglam verisi:</b> World Bank Open Data (CO2, enerji kullanimi, yenilenebilir enerji, PM2.5) canli cekim ve ozet.</li></ul></div></section>')

    pages.append('<section class="page"><div class="card"><h2>3. ' + esc(T["data_volume"]) + '</h2>'
    + '<div class="grid">'
    + '<div class="metric"><b>DB toplam kayit</b><br>' + ('' if db_rows is None else f'{int(db_rows):,}') + '</div>'
    + '<div class="metric"><b>DB lokasyon</b><br>' + ('' if db_locs is None else f'{int(db_locs):,}') + '</div>'
    + '<div class="metric"><b>DB parametre</b><br>' + ('' if db_params is None else f'{int(db_params):,}') + '</div>'
    + '<div class="metric"><b>analysis_results</b><br>' + ('' if db_analyses is None else f'{int(db_analyses):,}') + '</div>'
    + '<div class="metric"><b>Secili seri kaydi</b><br>' + f'{current_n:,}' + '</div>'
    + '<div class="metric"><b>Taranan lokasyon</b><br>' + str(0 if scan_df is None else len(scan_df)) + '</div></div>'
    + '<p class="note">Ilk kapsamda 31 lokasyon x 36 parametre icin 17.136.161 gunluk kayit islenmistir. 81 il + ek ulkeler icin genisletilmis ingest arka planda surmektedir; toplamlar zamanla artabilir.</p></div></section>')

    pages.append('<section class="page"><div class="card"><h2>3A. Yapilan Calismalar ve Suren Islem Ozeti</h2><ul><li><b>Kapsam genisletme:</b> Turkiye 81 il + ek dunya ulkeleri/baskentleri icin toplam 201 lokasyon hedeflenmistir.</li><li><b>Veri cekimi ve isleme (suruyor):</b> Her lokasyon icin 36 NASA POWER parametresi (1981-gunumuz, gunluk) API uzerinden cekilmekte; -999/sentinel ve eksik degerler ayiklanmakta, gecerli kayitlar MySQL <code>nasa_power_raw</code> tablosuna yazilmaktadir.</li><li><b>Guncel durum:</b> ' + str(db_locs or 0) + ' lokasyon, ' + (f"{int(db_rows):,}" if db_rows else "0") + ' ham kayit islenmis durumdadir; ingest arka planda devam eder.</li><li><b>Izleme ve sureklilik:</b> Islem 10 dk araliklarla kontrol edilmekte, durma olursa otomatik yeniden baslatilmaktadir.</li><li><b>Analiz uretimi:</b> Ingest tamamlandiginda (ve surec boyunca mevcut veriler uzerinden) lokasyon/parametre bazli trend (10 yil), p-degeri, %95 GA, Mann-Kendall ve ozet istatistikler <code>analysis_results</code> tablosuna hesaplanip kaydedilmektedir.</li><li><b>Yansima:</b> Uygulama, mevcut islenmis veriyi harita, grafik, karsilastirma ve bu sunum/rapor ciktilarina anlik olarak yansitir.</li></ul></div></section>')
    pages.append('<section class="page"><div class="card"><h2>4. ' + esc(T["problematic_data"]) + '</h2><ul>'
    + '<li><b>-999 / sentinel eksik degerler:</b> NASA POWER tarafinda gecerli olcum/model degeri olmadigini belirtir; ingest ve analiz oncesi filtrelenir, veritabanina yazilmaz.</li>'
    + '<li><b>Parametre kapsama farki:</b> Bazi parametreler belirli lokasyon/zaman araliklarinda sunulmayabilir (uydu/model erisilebilirligi, kalite kontrol).</li>'
    + '<li><b>Ag/API ve zaman uyumsuzluklari:</b> Zaman asimi, gecici erisim hatalari, ay/gun sinirlari ve koordinat toleransi eksik gozleme yol acabilir.</li>'
    + '<li><b>Analize etkiler:</b> Orneklem (n) azalir; standart hata ve %95 guven araligi genisleyebilir, p-degeri ve Mann-Kendall test gucu/duyarliligi dusabilir. Bu nedenle trend ve anlamlilik veri yogunlugu ve donemle birlikte yorumlanir.</li></ul></div></section>')

    pages.append('<section class="page"><div class="card"><h2>5. Secili Lokasyon Analiz Sonuclari</h2>'
    + '<div class="grid">'
    + '<div class="metric"><b>' + esc(T["average"]) + '</b><br>' + ('' if not stats_res else f"{stats_res.get('mean'):.3f} {esc(unit)}") + '</div>'
    + '<div class="metric"><b>' + esc(T["trend_10y"]) + '</b><br>' + ('' if trend is None else f"{trend:.4f} {esc(unit)}/10y") + '</div>'
    + '<div class="metric"><b>' + esc(T["p_value"]) + '</b><br>' + ('' if pval is None else f"{pval:.4g}") + '</div>'
    + '<div class="metric"><b>R2</b><br>' + ('' if r2 is None else f"{r2:.4f}") + '</div>'
    + '<div class="metric"><b>' + esc(T["ci95"]) + '</b><br>' + ('' if ci is None else f"±{ci:.4f}") + '</div>'
    + '<div class="metric"><b>' + esc(T["mk"]) + '</b><br>' + esc(mk) + '</div></div>'
    + '<p><b>' + esc(T["significance"]) + ':</b> ' + esc(sig) + '</p>' + img_tags[0] + img_tags[1] + '</div></section>')

    pages.append('<section class="page"><div class="card"><h2>6. ' + esc(T["country_avg"]) + '</h2>'
    + '<p class="note">T2M icin erken donem (&lt;=2000) ve gec donem (&gt;=2015) ortalamalari ile fark (Delta). Pozitif Delta, gec donemde daha yuksek ortalama sicakliga isaret eder.</p>'
    + '<table><thead><tr><th>Lokasyon</th><th>Ulke/Grup</th><th>Ort. &lt;=2000 (C)</th><th>Ort. &gt;=2015 (C)</th><th>Delta (C)</th></tr></thead><tbody>'
    + (country_rows or '<tr><td colspan="5">Yeterli MySQL verisi hazirlaniyor (ingest devam ediyor olabilir).</td></tr>') + '</tbody></table></div></section>')

    pages.append('<section class="page"><div class="card"><h2>7. ' + esc(T["radiation_section"]) + '</h2>'
    + '<p class="note">Radyasyon ve isi gostergeleri: ALLSKY_SFC_SW_DWN, ALLSKY_SFC_UV_INDEX, T2M_MAX vb.</p>'
    + '<table><thead><tr><th>Lokasyon</th><th>Gunes Rad. Ort. (kW-hr/m2/gun)</th><th>UV Indeks Ort.</th><th>T2M_MAX Ort. (C)</th></tr></thead><tbody>'
    + (rad_rows or '<tr><td colspan="4">Yeterli MySQL verisi hazirlaniyor.</td></tr>') + '</tbody></table>'
    + '<h3>Ekosisteme faydalar</h3><ul><li><b>Gunes radyasyonu (SW) ve PAR:</b> Fotosentez, birincil uretim, besin zinciri ve yenilenebilir enerji potansiyeli icin temel girdidir.</li>'
    + '<li><b>Mevsimsel enerji dengesi:</b> Biyolojik donguler ve habitat uygunlugunu destekleyebilir.</li></ul>'
    + '<h3>Zararlar / riskler</h3><ul><li><b>Yuksek UV:</b> Biyolojik stres, doku hasari riski, insan sagliginda deri/goz riskleri.</li>'
    + '<li><b>Asiri sicaklik (T2M_MAX) ve isi dalgalari:</b> Kuraklik stresi, su kitligi, verim kaybi, orman yangini riski, biyoceitlilik azalmasi.</li>'
    + '<li><b>Bilesik etkiler:</b> Enerji talebi artisi ve dolayli emisyon baskisi; adaptasyon/mitigasyon ihtiyacini artirir.</li></ul></div></section>')

    pages.append('<section class="page"><div class="card"><h2>8. Karsilastirma, Yontem ve Sinirliliklar</h2>'
    + img_tags[2]
    + '<h3>Karsilastirmali tarama (ornek)</h3><table><thead><tr>' + scan_head + '</tr></thead><tbody>' + (scan_rows or '<tr><td colspan="6">Tarama verisi secime bagli olarak uretilir.</td></tr>') + '</tbody></table>'
    + '<h3>Yontem</h3><ul><li>Lineer regresyon trendi, R2, p-degeri, %95 GA, Mann-Kendall.</li><li>Gunluk/aylik toplulastirma, ay filtresi, nokta ve coklu lokasyon analizi.</li></ul>'
    + '<h3>Sinirliliklar</h3><ul><li>Tek nokta/parametre tum sistemi temsil etmez; uydu/model-yer gozlemi farklari olabilir.</li><li>Eksik veri ve otokorelasyon test duyarliligini etkileyebilir.</li><li>Sonuclar karar destek amaclidir; nedensellik icin ek veri/modeller gerekir.</li></ul>'
    + '<p class="small">' + esc(T["print_pdf_hint"]) + '</p></div></section>')

    content = "\n".join(pages)
    css = (
        "<style>"
        "body{font-family:Arial,sans-serif;margin:0;color:#111827;background:#e5e7eb}"
        ".page{width:210mm;min-height:297mm;margin:10mm auto;background:#fff;padding:14mm;box-sizing:border-box;box-shadow:0 2px 8px rgba(0,0,0,.15);page-break-after:always}"
        ".hero{background:linear-gradient(135deg,#0b3d91,#1d4ed8,#0ea5e9);color:#fff;padding:16px;border-radius:12px}"
        ".card{border:1px solid #dbeafe;border-radius:12px;padding:12px;margin:10px 0}"
        ".grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}"
        ".metric{background:#f1f5f9;border-radius:10px;padding:8px;font-size:14px}"
        "table{width:100%;border-collapse:collapse;font-size:12px} th,td{border:1px solid #e5e7eb;padding:5px;text-align:left;vertical-align:top}"
        "img{max-width:100%;height:auto;border:1px solid #e5e7eb;border-radius:8px}"
        ".imgbox{margin:8px 0} .note{color:#374151;font-size:13px} .small{color:#374151;font-size:12px}"
        "h2{margin-top:0;color:#0b3d91} h3{color:#1e3a8a}"
        "@page{size:A4;margin:10mm}"
        "@media print{body{background:#fff} .page{margin:0;box-shadow:none;width:auto;min-height:0;padding:0}}"
        "</style>"
    )
    return ('<!doctype html><html lang="' + esc(lang) + '"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>'
            '<title>Earth Trend Detective Presentation</title>' + css + '</head><body>' + content + '</body></html>')


def build_report_html(T, lang, parameter, unit, loc_name, period_label, source, stats_res, analysis_df, scan_df, db_overview, country_avg_df, rad_df, figs_b64):
    pres = build_presentation_html(T, lang, parameter, unit, loc_name, period_label, source, stats_res, analysis_df, scan_df, db_overview, country_avg_df, rad_df, figs_b64)
    extra = []
    extra.append('<section class="page"><div class="card"><h2>9. Yapilan Calismalar ve Suren Veri Isleme Ozeti</h2><ul><li><b>Kapsam:</b> Turkiye 81 il + ek dunya ulkeleri/baskentleri (201 lokasyon hedefi) icin NASA POWER gunluk verileri islenmektedir.</li><li><b>Isleme adimlari:</b> 36 parametre x lokasyon bazinda API cekimi, -999/eksik deger ayiklama, MySQL <code>nasa_power_raw</code> yazimi.</li><li><b>Izleme/sureklilik:</b> 10 dk araliklarla kontrol, otomatik yeniden baslatma; uygulama mevcut veriyi anlik analiz eder.</li><li><b>Analiz tamamlama:</b> Ingest sonrasi/ surecinde trend, p-degeri, %95 GA, Mann-Kendall ve ozet metrikler <code>analysis_results</code> tablosuna uretilir.</li><li><b>Guncel ilerleme:</b> DBdeki lokasyon ve ham kayit sayilari arttikca sunum/rapor ciktilari guncel kapsamı yansitir.</li></ul></div></section>')
    extra.append('<section class="page"><div class="card"><h2>10. Detayli Metodoloji ve Istatistiksel Yorum</h2>'
                '<ul><li><b>Lineer regresyon:</b> Zaman serisinde egim (gunluk/yillik/10 yillik) hesaplanir; R2 aciklanan varyansi gosterir.</li>'
                '<li><b>p-degeri ve %95 GA:</b> Egimin istatistiksel gucunu ve belirsizligini degerlendirir; orneklem buyuklugu (n) yorumda kritiktir.</li>'
                '<li><b>Mann-Kendall:</b> Dagilim varsayimindan bagimsiz monoton trend testi; aykiri degerlere daha dayaniklidir.</li>'
                '<li><b>On isleme:</b> Tarih/sayisal donusum, -999 ayiklama, aylik ortalama ve ay filtresi.</li></ul>'
                '<p class="note">Anlamlilik tek basina etki buyuklugunu gostermez; egim, GA ve baglam birlikte degerlendirilmelidir.</p></div></section>')
    extra.append('<section class="page"><div class="card"><h2>11. Veri Kalitesi, Eksiklik Nedenleri ve Analize Etkiler</h2>'
                '<ul><li><b>Sentinel (-999):</b> Gecerli deger yok; dahil edilirse sapma olusur, bu nedenle cikarilir.</li>'
                '<li><b>Kapsama farklari:</b> Parametre/lokasyon/zaman bazinda erisilebilirlik degisebilir.</li>'
                '<li><b>Operasyonel etkenler:</b> API zaman asimi, ag kesintileri; retry/fallback ve islenmis MySQL katmani ile sureklilik saglanir.</li>'
                '<li><b>Istatistiksel etki:</b> Dusuk n daha genis GA, daha yuksek p-degeri olasiligi ve MK gucunde azalmaya yol acabilir; kisa donemlerde yanlis negatif/pozitif riski artabilir.</li></ul></div></section>')
    extra.append('<section class="page"><div class="card"><h2>12. Ulke/Il Bazli Isi Degisimi Yorumu</h2>'
                '<p>T2M erken (&lt;=2000) ve gec (&gt;=2015) donem ortalamalari karsilastirildiginda bircok lokasyonda pozitif Delta gozlenebilir; bu durum bolgesel iklim, yukseklik, kara-deniz etkisi ve veri yogunluguna baglidir.</p>'
                '<p>Tek parametre yeterli degildir; nem, yagis, radyasyon ve ruzgar ile birlikte degerlendirme yapilmalidir. Kentsel isi adasi, arazi kullanimi ve su kaynaklari baskisi ek risk faktorleridir.</p>'
                '<h3>Onerilen aksiyonlar</h3><ul><li>Isi dalgasi erken uyarilari ve saglik koruma planlari.</li><li>Su yonetimi ve tarimsal adaptasyon.</li><li>Kentsel yesil altyapi ve isi adasi azaltimi.</li></ul></div></section>')
    extra.append('<section class="page"><div class="card"><h2>13. Radyasyonun Ekosistem ve Toplum Uzerindeki Etkileri</h2>'
                '<h3>Faydalar</h3><ul><li>Fotosentez ve birincil uretim (PAR/SW).</li><li>Gunes enerjisi uretimi ve dusuk karbonlu gecis potansiyeli.</li></ul>'
                '<h3>Zararlar/Riskler</h3><ul><li>Yuksek UV: biyolojik stres ve saglik riskleri (deri/goz).</li><li>Yuksek T2M_MAX: isi dalgasi, kuraklik, yangin riski, habitat baskisi.</li><li>Bilesik etkiler: enerji talebi ve dolayli emisyon baskisi.</li></ul>'
                '<h3>Izleme onerileri</h3><ul><li>UV ve sicaklik uc degerlerinin birlikte izlenmesi.</li><li>Radyasyon-bulutluluk-aerosol (AOD) birlikte analizi.</li><li>Yerel gozlem ile dogrulama ve adaptasyon planlari.</li></ul></div></section>')
    extra.append('<section class="page"><div class="card"><h2>14. Sonuc ve Oneriler</h2>'
                '<ul><li>NASA POWER tabanli cok parametreli analiz, trend ve anlamlilik degerlendirmesi icin olceklenebilir bir altyapi sunar.</li>'
                '<li>Islenmis MySQL katmani hizli erisim ve tekrar analiz imkani saglar; genisletilmis lokasyon kapsami (81 il + ulkeler) surdurulmektedir.</li>'
                '<li>Sonraki adim: tum lokasyonlar icin analiz sonuclarinin surekli guncellenmesi ve karsilastirmali raporlarin yenilenmesi.</li></ul>'
                '<p class="small">Kaynaklar: NASA POWER, World Bank Open Data, NASA Space Apps 2026. Bu rapor karar destek amaclidir.</p></div></section>')
    return pres.replace("</body></html>", "\n".join(extra) + "</body></html>")



# -------------------- UI --------------------
lang_choice = st.sidebar.selectbox("Language / Dil", list(LANG_LABELS.keys()), format_func=lambda k: LANG_LABELS[k], index=0)
T = tr(lang_choice)

st.markdown(
    """
<style>
.stApp { background: radial-gradient(circle at 10% 10%, #eef6ff 0%, #f7fafc 35%, #ffffff 100%); }
.hero { padding: 1.0rem 1.2rem; border-radius: 16px; background: linear-gradient(135deg, #0b3d91 0%, #1d4ed8 45%, #0ea5e9 100%); color: white; box-shadow: 0 10px 30px rgba(11,61,145,0.25); margin-bottom: 0.8rem; }
.hero h1 { margin: 0; font-size: 2rem; }
.hero p { margin: 0.2rem 0 0 0; opacity: 0.95; }
.stApp, .stMarkdown, .stText, .stCaption, p, li, label { color: #1f2937; }
.stCaption, [data-testid="stCaptionContainer"] { color: #374151 !important; }
.hero, .hero h1, .hero p, .hero span, .hero b { color: #ffffff !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #111827 100%) !important; }
[data-testid="stSidebar"] * { color: #f8fafc !important; }
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * , [data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea { color: #111827 !important; background-color: #f8fafc !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] small { color: #f8fafc !important; }
[data-testid="stSidebar"] button[title="View fullscreen"], [data-testid="stSidebar"] [data-testid="StyledFullScreenButton"], [data-testid="stImage"] button[title="View fullscreen"] { display: none !important; }
@media (max-width: 900px) { .hero h1 { font-size: 1.5rem; } [data-testid="stHorizontalBlock"] { flex-wrap: wrap; } }
img { max-width: 100%; height: auto; } [data-testid="stPlotlyChart"] { width: 100%; }
</style>
""", unsafe_allow_html=True)

logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Sayriks_Space_Tecnological_Research.jpeg")
if os.path.exists(logo_path):
    st.sidebar.markdown('<div style="width:min(250px,100%);max-width:100%;margin:0 auto;text-align:center;">', unsafe_allow_html=True)
    st.sidebar.image(logo_path, use_container_width=True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
st.sidebar.markdown(
    '''<div style="width:min(250px,100%);max-width:100%;margin:0 auto;text-align:center;padding:6px 8px;border-radius:10px;border:1px solid #334155;background:linear-gradient(180deg,#0f172a,#111827);box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 4px 10px rgba(0,0,0,0.35);font-weight:700;line-height:1.2;">
    <span style="color:#d4af37;text-shadow:0 1px 1px rgba(0,0,0,0.6);">Sayriks</span>
    <span style="color:#c0c7d1;text-shadow:0 1px 1px rgba(0,0,0,0.6);"> Space</span>
    <span style="color:#38bdf8;text-shadow:0 1px 1px rgba(0,0,0,0.6);"> Technological</span>
    <span style="color:#ef4444;text-shadow:0 1px 1px rgba(0,0,0,0.6);"> Research</span></div>''', unsafe_allow_html=True)

st.markdown(f"""
<div class="hero">
  <h1>🌍 Earth Trend Detective</h1>
  <p><b>{T['app_subtitle']}</b></p>
  <p style="font-size:0.95rem;">{T['hero_source']}</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.header(f"⚙️ {T['control_panel']}")
mysql_ok = _mysql_ok()
mode_options = [("mysql", T["mode_mysql"]), ("nasa", T["mode_nasa"]), ("sim", T["mode_sim"])]
mode_key = st.sidebar.selectbox(T["data_source_mode"], [m[0] for m in mode_options], format_func=lambda k: dict(mode_options)[k], index=0 if mysql_ok else 1)
if mysql_ok:
    st.sidebar.caption(f"✅ {T['mysql_ok']}")
else:
    st.sidebar.caption(f"ℹ️ {T['mysql_missing']}")

wide_mode = st.sidebar.checkbox(T["wide_mode"], value=True)
agg_disp = st.sidebar.selectbox(T["time_resolution"], [T["daily"], T["monthly_avg"]], index=1)
agg_mode = "monthly" if agg_disp == T["monthly_avg"] else "daily"

param_options = list(PARAMETERS.keys()) + [T["custom_param"]]
param_choice = st.sidebar.selectbox(T["parameter"], param_options, format_func=lambda k: PARAMETERS[k]["label"] if k in PARAMETERS else k)
if param_choice == T["custom_param"]:
    parameter = st.sidebar.text_input(T["custom_param_code"], value="T2M").strip().upper() or "T2M"
    unit = "-"
else:
    parameter = param_choice
    unit = PARAMETERS.get(parameter, {}).get("unit", "-")

preset_names = [p["name"] for p in PRESET_LOCATIONS]
default_idx = preset_names.index("Ankara, Türkiye") + 1 if "Ankara, Türkiye" in preset_names else 1
loc_choice = st.sidebar.selectbox(T["location_preset"], [T["custom_location"]] + preset_names, index=min(default_idx, len(preset_names)))
if loc_choice == T["custom_location"]:
    lat = st.sidebar.number_input(T["latitude"], value=39.9334, format="%.6f")
    lon = st.sidebar.number_input(T["longitude"], value=32.8597, format="%.6f")
    loc_name = st.sidebar.text_input(T["location_name"], value="Custom")
else:
    sel = next(p for p in PRESET_LOCATIONS if p["name"] == loc_choice)
    lat, lon, loc_name = sel["lat"], sel["lon"], sel["name"]

c1y, c1m = st.sidebar.columns(2)
start_year = int(c1y.number_input(T["start_year"], 1981, 2026, 1981 if wide_mode else 2015))
start_month = int(c1m.selectbox(T["start_month"], list(range(1, 13)), index=0, format_func=lambda x: f"{x:02d}"))
c2y, c2m = st.sidebar.columns(2)
end_year = int(c2y.number_input(T["end_year"], 1981, 2026, 2025))
end_month = int(c2m.selectbox(T["end_month"], list(range(1, 13)), index=11, format_func=lambda x: f"{x:02d}"))
if (end_year, end_month) < (start_year, start_month):
    st.sidebar.error("End date must be after start date / Bitiş tarihi başlangıçtan önce olamaz.")
    st.stop()

view_month_filter = st.sidebar.multiselect(T["months_filter"], list(range(1, 13)), default=[], format_func=lambda x: f"{x:02d}")
compare_presets = st.sidebar.checkbox(T["compare_scan"], value=True)
group_labels = {"Türkiye": T["group_tr"], "Dünya": T["group_world"], "Dünya Başkentleri": T["group_capitals"], "Tümü": T["group_all"]}
scan_group = st.sidebar.selectbox(T["scan_group"], list(group_labels.keys()), index=2, format_func=lambda k: group_labels[k])
if scan_group == "Dünya Başkentleri":
    candidates = [p for p in PRESET_LOCATIONS if p.get("type") == "capital" and p.get("group") == "Dünya"]
elif scan_group == "Türkiye":
    candidates = [p for p in PRESET_LOCATIONS if p.get("group") == "Türkiye"]
elif scan_group == "Dünya":
    candidates = [p for p in PRESET_LOCATIONS if p.get("group") == "Dünya"]
else:
    candidates = PRESET_LOCATIONS[:]
candidates_count = max(3, len(candidates))
max_scan = st.sidebar.slider(T["scan_count"], 3, len(PRESET_LOCATIONS), min(candidates_count, len(PRESET_LOCATIONS)), help=T["scan_help"])
scan_candidates = candidates[:max_scan]

df_raw, source_label, warn_msg = fetch_data(lat, lon, start_year, end_year, parameter, start_month, end_month, mode_key, T, loc_name)
if warn_msg:
    st.sidebar.warning(str(warn_msg)[:350])

analysis_df = to_analysis_df(df_raw, agg_mode, view_month_filter)
stats_res = calculate_trend_and_stats(analysis_df)
period_label = f"{start_year}-{start_month:02d} .. {end_year}-{end_month:02d}"
if view_month_filter:
    period_label += f" | months: {','.join(f'{m:02d}' for m in view_month_filter)}"

scan_df = pd.DataFrame()
if compare_presets and scan_candidates:
    scan_df = scan_locations(scan_candidates, start_year, end_year, parameter, start_month, end_month, mode_key, T)

db_overview = get_mysql_overview() if mysql_ok else None

tab1, tab2, tab3, tab4, tab5 = st.tabs([T["tab_map"], T["tab_trends"], T["tab_data"], T["tab_methods"], T["tab_presentation"]])

with tab1:
    st.subheader(f"{T['selected_location']}: {loc_name}")
    st.write(f"{T['coordinate']}: **{lat:.4f}, {lon:.4f}** | {T['period']}: **{period_label}** | {T['source']}: **{source_label}**")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric(T["average"], f"{stats_res['mean']:.2f} {unit}" if stats_res else "-")
    c2.metric(T["maximum"], f"{stats_res['max']:.2f} {unit}" if stats_res else "-")
    c3.metric(T["minimum"], f"{stats_res['min']:.2f} {unit}" if stats_res else "-")
    c4.metric(T["trend_10y"], f"{stats_res['slope_per_decade']:.3f} {unit}/10y" if stats_res else "-")

    st.markdown(f"### {T['point_analysis']}")
    st.caption(T["ocean_note"])
    g1, g2 = st.columns(2, gap="small")
    fig_g1 = build_globe(scan_df if not scan_df.empty else None, lat, lon, loc_name, "trend_10y", f"{parameter} — {T['globe']} (trend/10y)", f"{unit}/10y")
    fig_g2 = build_globe(scan_df if not scan_df.empty else None, lat, lon, loc_name, "mean" if (not scan_df.empty and "mean" in scan_df.columns) else "trend_10y", f"{parameter} — {T['global_heatmap']} (mean)", unit)
    # keep equal appearance
    for f in (fig_g1, fig_g2):
        f.update_layout(height=500, margin=dict(l=0, r=0, t=34, b=0))
        f.update_coloraxes(colorbar=dict(x=1.01, len=0.7, thickness=11))
    with g1:
        st.plotly_chart(fig_g1, use_container_width=True)
    with g2:
        st.plotly_chart(fig_g2, use_container_width=True)

    if not scan_df.empty:
        st.markdown("#### " + T["compare_scan"])
        show_cols = [c for c in ["name","group","trend_10y","p_value","mean","mk_trend"] if c in scan_df.columns]
        st.dataframe(scan_df[show_cols].sort_values("trend_10y", ascending=False, na_position="last"), use_container_width=True)

    with st.expander(f"🌍 {T['worldbank_shortcut']}", expanded=False):
        st.caption(T["wb_info"])
        default_country = "TUR" if "Türkiye" in loc_name else "USA"
        wb_c1, wb_c2, wb_c3 = st.columns([1,2,1])
        wb_country = wb_c1.text_input("Country ISO3", value=default_country)
        wb_ind = wb_c2.selectbox("Indicator", [
            ("EN.GHG.CO2.MT.CE.AR5", "CO2 emissions (Mt CO2e)"),
            ("EG.USE.PCAP.KG.OE", "Energy use (kg oil eq per capita)"),
            ("EG.FEC.RNEW.ZS", "Renewable energy consumption (%)"),
            ("EN.ATM.PM25.MC.M3", "PM2.5 air pollution (µg/m3)"),
        ], format_func=lambda x: f"{x[0]} — {x[1]}")
        if wb_c3.button(T["wb_fetch"], type="secondary"):
            try:
                with st.spinner(T["wb_fetching"]):
                    wb_df = fetch_world_bank(wb_country.strip().upper(), wb_ind[0], max(1990, start_year), end_year)
                if wb_df.empty:
                    st.info(T["no_data"])
                else:
                    st.dataframe(wb_df.tail(20), use_container_width=True)
                    fig_wb = px.line(wb_df, x="year", y="value", markers=True, title=f"{wb_ind[1]} — {wb_country}")
                    fig_wb.update_layout(height=320, template="plotly_white")
                    st.plotly_chart(fig_wb, use_container_width=True)
            except Exception as e:
                st.error(f"World Bank: {e}")

with tab2:
    if analysis_df is None or analysis_df.empty or not stats_res:
        st.warning(T["no_data"])
    else:
        st.markdown(f"### {T['chart_time_series']} — {parameter} ({unit})")
        fig_ts = px.line(analysis_df, x="Date", y="Value", labels={"Value": unit, "Date": ""})
        x_ord = analysis_df["Date"].map(pd.Timestamp.toordinal).astype(float)
        y_hat = stats_res["slope_per_day"] * x_ord + stats_res["intercept"]
        fig_ts.add_trace(go.Scatter(x=analysis_df["Date"], y=y_hat, mode="lines", name=T["chart_trend"], line=dict(color="#ef4444", dash="dash")))
        fig_ts.update_layout(template="plotly_white", height=420)
        st.plotly_chart(fig_ts, use_container_width=True)

        ydf = analysis_df.copy(); ydf["year"] = ydf["Date"].dt.year
        yearly = ydf.groupby("year", as_index=False)["Value"].mean()
        yearly["anomaly"] = yearly["Value"] - yearly["Value"].mean()
        fig_an = px.bar(yearly, x="year", y="anomaly", title=T["chart_anomaly"], labels={"anomaly": unit, "year": ""})
        fig_an.update_layout(template="plotly_white", height=320)
        st.plotly_chart(fig_an, use_container_width=True)

        st.markdown(f"#### {T['significance']}")
        s1,s2,s3,s4 = st.columns(4)
        s1.metric(T["p_value"], f"{stats_res.get('p_value', float('nan')):.4g}")
        s2.metric("R²", f"{stats_res.get('r_squared', float('nan')):.4f}")
        ci = stats_res.get("slope_ci95_decade")
        s3.metric(T["ci95"], f"±{ci:.4f}" if ci is not None else "-")
        s4.metric(T["mk"], str(stats_res.get("mk_trend", "-")))
        st.info(stats_res.get("significance", "-"))
        if "Simul" in source_label or "Simulation" in source_label:
            st.caption(T["sim_note"])

with tab3:
    st.markdown(f"### {T['data_table_title']}")
    if analysis_df is None or analysis_df.empty:
        st.warning(T["no_data"])
    else:
        st.caption(f"{T['records']}: {len(analysis_df):,}")
        st.dataframe(analysis_df[["Date","Value"]].rename(columns={"Value": f"{parameter} ({unit})"}), use_container_width=True, height=420)
        st.download_button(T["download_csv"], analysis_df.to_csv(index=False).encode("utf-8"), file_name=f"earth_trend_{parameter}_{start_year}_{end_year}.csv", mime="text/csv")
        if st.button(T["save_sqlite"], type="secondary"):
            try:
                n = save_series_sqlite(analysis_df, parameter, loc_name, lat, lon, source_label)
                st.success(f"{T['saved_sqlite']} ({n} {T['records']})")
            except Exception as e:
                st.error(str(e))

with tab4:
    st.markdown(f"### {T['nasa_data_used']}")
    st.markdown("- **NASA POWER Daily API (community=RE):** " + ", ".join(list(PARAMETERS.keys())))
    st.markdown(f"### {T['data_volume']}")
    if isinstance(db_overview, dict) and "error" not in db_overview:
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("nasa_power_raw", f"{int(db_overview['total_rows']):,}")
        c2.metric("locations", f"{int(db_overview['locations']):,}")
        c3.metric("parameters", f"{int(db_overview['params']):,}")
        c4.metric("analysis_results", f"{int(db_overview['analyses']):,}")
        st.caption(f"DB period: {db_overview.get('date_min')} — {db_overview.get('date_max')}")
    else:
        st.info(T["mysql_missing"] if not mysql_ok else str(db_overview))

    st.markdown(f"### {T['problematic_data']}")
    st.markdown(
        """
- **-999 / sentinel eksik değerler:** NASA POWER'da ölçüm/model değeri olmayan kayıtlar; ingest ve analiz öncesi ayıklanır.
- **Parametre kapsama farkı:** Tüm parametreler her lokasyon ve tarihte mevcut olmayabilir (uydu/model erişilebilirliği, kalite bayrakları).
- **Koordinat/tarih eşleşmesi ve ağ hataları:** Toleranslı eşleştirme, ay/gün sınırları ve bağlantı sorunları eksik satır oluşturabilir.
- **Analize etki:** n azalır, güven aralığı genişler, p-değeri/Mann-Kendall duyarlılığı düşebilir; sonuçlar veri yoğunluğu ile birlikte yorumlanmalıdır.
"""
    )
    st.markdown(f"### {T['methodology_title']}")
    st.markdown("- Lineer regresyon (trend/10y), R², p-değeri, %95 GA, Mann-Kendall. Günlük/aylık toplulaştırma ve ay filtresi desteklenir.")
    st.markdown(f"### {T['radiation_title']}")
    st.markdown(
        """
- **Fayda:** ALLSKY/CLRSKY SW, PAR → fotosentez ve güneş enerjisi potansiyeli.
- **Risk:** Yüksek UV ve T2M_MAX → canlılarda fizyolojik stres, ısı dalgası, kuraklık/yangın riski.
- **Bağlam:** Radyasyon-sıcaklık eğilimleri enerji talebi ve dolaylı emisyon/adaptasyon planlamasını etkiler.
"""
    )
    st.markdown(f"### {T['sources_title']}")
    st.markdown("- NASA POWER: https://power.larc.nasa.gov/\n- NASA Space Apps 2026 Challenge: https://www.spaceappschallenge.org/2026/challenges/earth-system-trend-detective/\n- World Bank Open Data: https://data.worldbank.org/")
    st.markdown(f"### {T['limitations_title']}")
    st.markdown(f"- {T['sim_note']}\n- {T['ocean_note']}\n- Tek nokta analizi tüm iklim sistemini temsil etmez; ek doğrulama gerekebilir.")

with tab5:
    st.markdown(f"### {T['presentation_title']}")
    if not stats_res:
        st.warning(T["no_data"])
    else:
        country_avg_df = get_country_averages_t2m(120) if mysql_ok else pd.DataFrame()
        rad_df = get_radiation_country_summary(80) if mysql_ok else pd.DataFrame()

        st.markdown(f"**{T['selected_location']}:** {loc_name}  \n**{T['parameter']}:** {parameter} ({unit})  \n**{T['period']}:** {period_label}  \n**{T['source']}:** {source_label}")
        m1,m2,m3,m4 = st.columns(4)
        m1.metric(T["average"], f"{stats_res['mean']:.2f} {unit}")
        m2.metric(T["trend_10y"], f"{stats_res['slope_per_decade']:.4f} {unit}/10y")
        m3.metric(T["p_value"], f"{stats_res['p_value']:.4g}")
        m4.metric(T["records"], f"{stats_res['count']:,}")

        figs_b64 = []
        if analysis_df is not None and not analysis_df.empty:
            fig_ts = px.line(analysis_df, x="Date", y="Value", title=f"{T['chart_time_series']} — {loc_name}")
            x_ord = analysis_df["Date"].map(pd.Timestamp.toordinal).astype(float)
            y_hat = stats_res["slope_per_day"] * x_ord + stats_res["intercept"]
            fig_ts.add_trace(go.Scatter(x=analysis_df["Date"], y=y_hat, mode="lines", name=T["chart_trend"]))
            fig_ts.update_layout(template="plotly_white", height=360)
            st.plotly_chart(fig_ts, use_container_width=True)
            figs_b64.append(fig_to_b64(fig_ts))

            ydf = analysis_df.copy(); ydf["year"] = ydf["Date"].dt.year
            yearly = ydf.groupby("year", as_index=False)["Value"].mean(); yearly["anomaly"] = yearly["Value"] - yearly["Value"].mean()
            fig_an = px.bar(yearly, x="year", y="anomaly", title=T["chart_anomaly"])
            fig_an.update_layout(template="plotly_white", height=300)
            st.plotly_chart(fig_an, use_container_width=True)
            figs_b64.append(fig_to_b64(fig_an))

        st.markdown("#### Yapılan Çalışmalar ve Süren İşlem Özeti")
        if isinstance(db_overview, dict) and "error" not in db_overview:
            done_locs = int(db_overview.get('locations', 0))
            done_raw = int(db_overview.get('total_rows', 0))
        else:
            done_locs, done_raw = 0, 0
        st.info(
            f"**Süren işlem:** 81 il + ek dünya ülkeleri/başkentleri için genişletilmiş NASA POWER ingest arka planda devam ediyor (hedef 201 lokasyon, mevcut {done_locs} lokasyon, {done_raw:,} ham kayıt). "
            "Her lokasyon için 36 parametre, 1981–günümüz günlük veriler NASA POWER API'den çekiliyor; -999/eksik değerler ayıklanıyor, geçerli kayıtlar MySQL `nasa_power_raw` tablosuna yazılıyor. "
            "İşlem 10 dk aralıklarla izleniyor, durursa otomatik yeniden başlatılıyor; ingest tamamlandığında eksik `analysis_results` (trend, p-değeri, %95 GA, Mann-Kendall, özet istatistikler) otomatik hesaplanıp kaydediliyor. "
            "Uygulama mevcut işlenmiş veriyi anlık olarak analize ve görsellere yansıtır."
        )
        st.markdown(f"#### {T['nasa_data_used']}")
        st.write("NASA POWER Daily (community=RE) parametreleri: " + ", ".join(list(PARAMETERS.keys())[:12]) + ", ...")
        if isinstance(db_overview, dict) and "error" not in db_overview:
            st.markdown(f"#### {T['data_volume']}")
            d1,d2,d3,d4 = st.columns(4)
            d1.metric("nasa_power_raw", f"{int(db_overview['total_rows']):,}")
            d2.metric("locations", f"{int(db_overview['locations']):,}")
            d3.metric("parameters", f"{int(db_overview['params']):,}")
            d4.metric("analysis_results", f"{int(db_overview['analyses']):,}")

        st.markdown(f"#### {T['problematic_data']}")
        st.info("NASA POWER -999 eksik değerleri ve parametre kapsama farkları ayıklanır; bu durum örneklem (n), güven aralığı ve anlamlılık (p/MK) hassasiyetini etkileyebilir. Ağ/erişim hatalarında fallback uygulanır.")

        st.markdown(f"#### {T['country_avg']}")
        if country_avg_df is not None and not country_avg_df.empty:
            show_c = country_avg_df.head(20)[["name","country","avg_early","avg_late","delta","n"]].copy()
            st.dataframe(show_c, use_container_width=True)
            fig_c = px.bar(show_c.head(15).sort_values("delta"), x="delta", y="name", orientation="h", title="T2M Δ (avg ≥2015 − avg ≤2000)")
            fig_c.update_layout(template="plotly_white", height=420)
            st.plotly_chart(fig_c, use_container_width=True)
            figs_b64.append(fig_to_b64(fig_c))
        else:
            st.caption("MySQL ülke ortalaması verisi henüz yeterli değil veya ingest devam ediyor.")

        st.markdown(f"#### {T['radiation_section']}")
        if rad_df is not None and not rad_df.empty:
            st.dataframe(rad_df.head(20), use_container_width=True)
            if "sw_dwn" in rad_df.columns:
                fig_r = px.scatter(rad_df.dropna(subset=["sw_dwn","uv_index"]), x="sw_dwn", y="uv_index", hover_name="name", size="t2m_max" if "t2m_max" in rad_df.columns else None, title="SW Radiation vs UV Index (bubble ~ T2M_MAX)")
                fig_r.update_layout(template="plotly_white", height=380)
                st.plotly_chart(fig_r, use_container_width=True)
                figs_b64.append(fig_to_b64(fig_r))
        st.markdown("- **Fayda:** Güneş radyasyonu/PAR fotosentez ve yenilenebilir enerji için kritiktir.\n- **Risk:** Yüksek UV ve T2M_MAX ısı stresi, sağlık ve ekosistem zararlarını artırabilir; adaptasyon gerekir.")

        if not scan_df.empty:
            st.markdown("#### " + T["compare_scan"])
            st.dataframe(scan_df.sort_values("trend_10y", ascending=False, na_position="last"), use_container_width=True)

        pres_html = build_presentation_html(T, lang_choice, parameter, unit, loc_name, period_label, source_label, stats_res, analysis_df, scan_df, db_overview, country_avg_df, rad_df, figs_b64)
        report_html = build_report_html(T, lang_choice, parameter, unit, loc_name, period_label, source_label, stats_res, analysis_df, scan_df, db_overview, country_avg_df, rad_df, figs_b64)
        st.download_button(f"📥 {T['presentation_download']} (7+ sayfa)", data=pres_html.encode("utf-8"), file_name=f"earth_trend_presentation_{parameter}_{start_year}_{end_year}.html", mime="text/html")
        st.download_button("📥 Detaylı Rapor indir (A4, 10+ sayfa, HTML/PDF)", data=report_html.encode("utf-8"), file_name=f"earth_trend_report_{parameter}_{start_year}_{end_year}.html", mime="text/html")
        try:
            report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAPOR_Earth_Trend_Detective.html")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_html)
        except Exception:
            pass
        st.caption(T["print_pdf_hint"] + " Sunum: 8 sayfa, Rapor: 13 A4 sayfa (yazdırılabilir).")

st.caption("Earth Trend Detective — NASA Space Apps 2026 | NASA POWER, World Bank Open Data")
