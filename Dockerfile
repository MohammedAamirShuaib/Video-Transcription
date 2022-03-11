FROM python:3.7.9
WORKDIR /app
COPY . .
ENV access_id="AKIA2H25YUUMHYJD2CER"
ENV secret_id="wyZMkupZHo6NVpF8P58T2WHYG4Wbm7bW/y0loKWx"
RUN pip install -r requirements.txt
