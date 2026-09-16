# syntax=docker/dockerfile:1
FROM python:3.10-slim

WORKDIR /
COPY requirements.txt /requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY rp_handler.py /
COPY test_input.json /
CMD ["python3", "-u", "rp_handler.py"]