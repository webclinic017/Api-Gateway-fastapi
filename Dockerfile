FROM python:3.11.4-slim-buster

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONUNBUFFERED=1

WORKDIR /cephalopodus/gateway

COPY ./requirements.txt /cephalopodus/gateway/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /cephalopodus/gateway/requirements.txt

COPY ./src /cephalopodus/gateway

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]