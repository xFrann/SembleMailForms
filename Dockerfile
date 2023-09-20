FROM python:latest
LABEL authors="Frann"

WORKDIR /usr/app/src

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "./main.py"]