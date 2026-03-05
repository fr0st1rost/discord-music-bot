FROM python:3.11-slim

# Установить ffmpeg и nodejs (нужно для yt-dlp)
RUN apt-get update && apt-get install -y ffmpeg nodejs && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Скопировать файлы проекта
COPY . .

# Установить зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Запустить бота
CMD ["python", "bot.py"]
