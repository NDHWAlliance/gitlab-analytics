FROM python:3.6.5-slim
MAINTAINER oylbin "oylbin@gmail.com"
# ARG is used in build time
ARG INDEX_URL=https://pypi.python.org/simple
# ENV is used in runtime
ENV FLASK_APP=ga
ENV FLASK_DEBUG=1
ENV FLASK_ENV=development
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -i $INDEX_URL -r requirements.txt
COPY . /app
ENTRYPOINT ["python"]
CMD ["-m", "flask", "run","-h","0.0.0.0","-p","8080"]
