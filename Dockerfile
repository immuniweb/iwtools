FROM python:3.7-alpine

RUN apk update && apk add git

WORKDIR /usr/src/app

RUN git clone https://github.com/ImmuniwebSA/iwtools .

WORKDIR /usr/src/app/iwtools

RUN pip install -r requirements.txt

ENTRYPOINT ["./iwtools.py"]