# Gunakan image dasar Python
FROM python:3.9-slim

# Instal aria2, Node.js, dan npm
RUN apt-get update && \
    apt-get install -y aria2 nodejs npm && \
    npm install -g webcrack

# Set lingkungan kerja di dalam kontainer
WORKDIR /app

# Salin requirements.txt ke lingkungan kerja
COPY requirements.txt .

# Instal dependencies Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Salin semua file ke lingkungan kerja
COPY . .

# Tentukan command yang akan dijalankan saat kontainer dimulai
CMD ["python3", "run.py"]
