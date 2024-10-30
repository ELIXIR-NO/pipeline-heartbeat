FROM python:3.10-slim AS builder

RUN apt-get update && apt-get install -y binutils && pip install pyinstaller poetry

WORKDIR /app

COPY . /app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

RUN pyinstaller --onefile heartbeat.py

RUN chmod +x /app/dist/heartbeat

FROM gcr.io/distroless/python3-debian12

COPY --from=builder /app/dist/heartbeat .

CMD ["/heartbeat"]
