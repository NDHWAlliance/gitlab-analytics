dev:
	MYSQL_HOST=localhost \
	MYSQL_PORT=3306  \
	MYSQL_USER=ga \
	MYSQL_PASSWORD=4t9wegcvbYSd \
	MYSQL_DATABASE=gitlab_analytics \
	PORT=8080 \
	FLASK_ENV=development \
	FLASK_DEBUG=1 \
	python3 server/run.py

image:
	docker-compose build --build-arg INDEX_URL=https://mirrors.aliyun.com/pypi/simple ga

run:
	docker-compose up ga
