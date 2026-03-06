FROM python:3.11-slim

# FFmpeg ve gerekli sistem kütüphanelerinin kurulumu
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl && \
    rm -rf /var/lib/apt/lists/*

# Çalışma dizinini ayarla
WORKDIR /app

# Gereksinim dosyasını kopyala ve kurulumları yap
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Geri kalan proje dosyalarını kopyala
COPY . .

# Botu başlat
CMD ["python", "main.py"]
