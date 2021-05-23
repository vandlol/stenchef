FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /stenchef/stenchef
COPY requirements.txt /stenchef/
RUN pip install -r requirements.txt
COPY . /stenchef/