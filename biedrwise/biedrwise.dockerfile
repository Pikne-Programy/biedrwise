FROM python:3.10
EXPOSE 5000
WORKDIR /app
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y libgl1-mesa-glx poppler-utils tesseract-ocr
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD python3 app.py
