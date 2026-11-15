@echo off
TITLE SAYRİKS Space Apps - Otomatik Baslatici
cd /d %~dp0
echo [SAYRİKS AR-GE] Calisma dizini: %CD%

if not exist venv (
    echo [INFO] venv bulunamadi, yeni sanal ortam olusturuluyor...
    python -m venv venv
)

echo [INFO] Sanal ortam aktiflestiriliyor...
call venv\Scripts\activate

echo [INFO] Gerekli kutuphaneler yukleniyor...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo [INFO] SAYRİKS Earth Trend Detective baslatiliyor...
streamlit run app.py
pause