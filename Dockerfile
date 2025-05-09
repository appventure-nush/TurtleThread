FROM python:3.12-alpine AS build

WORKDIR /app 

RUN apk add make python3-tkinter

COPY src/ ./src
COPY requirements.txt .
COPY pyproject.toml .
COPY README.md .

RUN pip install --no-cache-dir -r requirements.txt

COPY docs/ ./docs
COPY logo/ ./logo
WORKDIR /app/docs
RUN make clean
RUN make html

FROM busybox:musl AS deploy

EXPOSE 80

RUN adduser -D static
USER static
WORKDIR /home/static

COPY --from=build /app/docs/_build/html /data/www/

CMD ["busybox", "httpd", "-f", "-v", "-p", "80", "-h", "/data/www"]