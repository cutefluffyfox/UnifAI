FROM golang:latest 
RUN mkdir /app 
ADD . /app/

WORKDIR /app/
RUN go build -o unifai .

CMD ["/app/unifai"]
