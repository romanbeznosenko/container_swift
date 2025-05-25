FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y default-mysql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY wait-for-mysql.sh .
RUN chmod +x wait-for-mysql.sh

EXPOSE 8000

CMD ["./wait-for-mysql.sh", "mysql_12", "python", "start.py"]