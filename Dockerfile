FROM python:3.12-bookworm AS build

WORKDIR /app 

COPY src/ ./src
COPY requirements.txt .
COPY pyproject.toml .
COPY README.md .

RUN apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        xvfb \
        ghostscript \
        inkscape 
RUN pip install --no-cache-dir -r requirements.txt

COPY docs/ ./docs
WORKDIR /app/docs
RUN make en

FROM busybox:musl AS deploy

EXPOSE 80

RUN adduser -D static
USER static
WORKDIR /home/static

COPY --from=build /app/docs/_build/en /data/www/

CMD ["busybox", "httpd", "-f", "-v", "-p", "80", "-h", "/data/www"]


# ENV TURTLETHREAD_VENV=/turtlethread-venv
# ENV DISPLAY=:12

#     && python -m venv $TURTLETHREAD_VENV \
#     && echo "if ! pidof Xvfb; then Xvfb $DISPLAY -screen 0 1920x1080x24 2>/tmp/Xvfb.log & fi" >> /root/.bashrc \
#     && echo "test -z $VIRTUAL_ENV && source $TURTLETHREAD_VENV/bin/activate" >> /root/.bashrc

# CMD Xvfb $DISPLAY -screen 0 1920x1080x24 2>/tmp/Xvfb.log & sleep 1 && bash