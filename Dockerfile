FROM python:3.7.9
WORKDIR /app
COPY . .
ENV access_id="AKIAWFPZMNZHUGEYWIIS"
ENV secret_id="ibRCFPIGejwp0HJpdCZC8IahxY4GnKBp8DNU/Awh"
RUN pip install -r requirements.txt