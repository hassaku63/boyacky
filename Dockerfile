FROM python:alpine

WORKDIR /boyacky
COPY . /boyacky

RUN pip3 install -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["python3"]
CMD ["-m", "app"]

