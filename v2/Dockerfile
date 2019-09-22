FROM python:3.7-alpine

ENV login = gdcirco
ENV password = gdcirco123

RUN pip install pandas

COPY . /core
WORKDIR /core

CMD ["python3", "main.py"]
