FROM python:3.10-slim AS builder

RUN apt-get update && apt-get install -y binutils && pip install pyinstaller poetry

WORKDIR /app

COPY . /app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

RUN pyinstaller --onefile heartbeat.py

RUN chmod +x /app/dist/heartbeat

FROM gcr.io/distroless/static-debian11

ARG CHIPSET_ARCH=x86_64-linux-gnu

COPY --from=builder /lib64/ld-linux-x86-64.so.2 /lib64/
COPY --from=builder /lib/${CHIPSET_ARCH}/libpthread.so.0 /lib/${CHIPSET_ARCH}/
COPY --from=builder /lib/${CHIPSET_ARCH}/libz.so.1 /lib/${CHIPSET_ARCH}/
COPY --from=builder /lib/${CHIPSET_ARCH}/libdl.so.2 /lib/${CHIPSET_ARCH}/
COPY --from=builder /lib/${CHIPSET_ARCH}/libc.so.6 /lib/${CHIPSET_ARCH}/
COPY --from=builder /lib/${CHIPSET_ARCH}/libm.so.6 /lib/${CHIPSET_ARCH}/

COPY --from=builder /app/dist/heartbeat .

ENTRYPOINT ["./heartbeat"]
