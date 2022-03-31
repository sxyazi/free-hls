FROM alpine
RUN apk update \
    && apk add python3 py3-pip \
    && pip3 install Flask peewee gunicorn python-dotenv
WORKDIR /var/app
COPY . .
WORKDIR /var/app/web
ENTRYPOINT ["gunicorn","app:app","-b","0.0.0.0:3395","--workers=5","--threads=2"]
EXPOSE 3395
