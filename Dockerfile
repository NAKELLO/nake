# Python 3.11 базалық образ
FROM python:3.11-slim

# Жұмыс қалтасы
WORKDIR /app

# Файлдарды көшіру
COPY requirements.txt .
COPY main.py .

# Пайдаланылатын пакеттерді орнату
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Ботты іске қосу
CMD ["python", "main.py"]
