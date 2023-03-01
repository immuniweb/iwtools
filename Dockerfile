FROM python:3.11-alpine
WORKDIR /app/
COPY iwtools /app/
RUN pip install -r requirements.txt
RUN adduser --no-create-home --disabled-password --gecos "" --uid 1001 iwtools
USER iwtools
ENTRYPOINT ["./iwtools.py"]