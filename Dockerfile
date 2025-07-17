FROM python:3.14-rc-alpine3.20

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libpango-1.0-0 libcairo2 gdk-pixbuf2.0-0 libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip cache purge || true && pip install --no-cache-dir -r requirements.txt

COPY start.sh ./
RUN chmod +x start.sh

COPY . .

EXPOSE 8000

CMD ["./start.sh"]
