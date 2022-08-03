FROM docker.io/library/python:3.10-alpine AS requirements
WORKDIR /app/
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin/:$PATH"
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --no-input --verbose \
  -r /tmp/requirements.txt && \
  rm /tmp/requirements.txt

FROM docker.io/library/python:3.10-alpine AS app
WORKDIR /app/
COPY --from=requirements /opt/venv/ /opt/venv
ENV PATH="/opt/venv/bin:$PATH" 
COPY iwtools /app/
RUN adduser --no-create-home --disabled-password --gecos "" --uid 1001 iwtools
USER iwtools
ENTRYPOINT ["python", "iwtools.py"]
CMD ["--help"]
