FROM python:3.10
EXPOSE 5000
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD python3 app.py
