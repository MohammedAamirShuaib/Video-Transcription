FROM python:3.7.9
WORKDIR /app
COPY . .
ENV access_id=""
ENV secret_id=""
RUN pip install -r requirements.txt
