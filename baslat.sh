#!/bin/bash
echo "[SAYRİKS AR-GE] Otomatisasyon baslatiliyor..."

if [ ! -d "venv" ]; then
    echo "[INFO] venv olusturuluyor..."
    python3 -m venv venv
fi

echo "[INFO] Sanal ortam aktiflestiriliyor..."
source venv/bin/activate

echo "[INFO] Bagimliliklar yukleniyor..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[INFO] Uygulama calistiriliyor..."
streamlit run app.py