FROM python:3.6.5-slim
MAINTAINER oylbin "oylbin@gmail.com"
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app
ENTRYPOINT ["python"]
CMD ["web.py"]