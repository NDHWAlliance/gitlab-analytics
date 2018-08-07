FROM python:3.6.5-slim
MAINTAINER oylbin "oylbin@gmail.com"
ARG INDEX_URL=https://pypi.python.org/simple
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -i $INDEX_URL -r requirements.txt
COPY . /app
ENTRYPOINT ["python"]
CMD ["run.py"]
