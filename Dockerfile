FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /stenchef
COPY . .
RUN pip install -r requirements.txt
WORKDIR /stenchef/stenchef