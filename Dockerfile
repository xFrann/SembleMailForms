FROM python:3.9
LABEL authors="Frann"

WORKDIR /home/semble_email

COPY . .

RUN pip install -r requirements.txt
EXPOSE 1025
CMD ["python", "./main.py"]