FROM golang:latest 
RUN mkdir /app 
ADD . /app/
COPY --from=ghcr.io/ufoscout/docker-compose-wait:latest /wait /wait

WORKDIR /app/
RUN go build -o unifai .

CMD /wait && /app/unifai
