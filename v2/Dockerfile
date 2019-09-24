FROM python:slim

ENV PYTHONUNBUFFERED 1
ENV login = gdcirco
ENV password = gdcirco123

RUN pip3 install pandas matplotlib seaborn

COPY . /core
WORKDIR /core

CMD ["python3", "main.py"]
