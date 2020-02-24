FROM python:3.8.1-alpine
RUN mkdir -p /home/app
COPY . /home/app
RUN pip3 install Flask gunicorn
WORKDIR /home/app/web
ENTRYPOINT ["gunicorn","app:app","-b","0.0.0.0:3395"]
