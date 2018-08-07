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

cleandb:
	-docker rm --force mysql
	rm -rf data/db/

test:
	cd server && python3 -m pytest --cov=ga --cov-report html

integration:
	cd server && docker build -t ga-test:latest -f Dockerfile .
	cd gatest && \
		docker run -d -it --rm -v `pwd`:/app \
		--network ganet --network-alias fakegitlab --name fakegitlab ga-test:latest \
		fakegitlab.py --host 0.0.0.0 --port 8081
	cd gatest && \
		docker run -it --rm -v `pwd`:/app \
		--network ganet ga-test:latest \
		gatest.py --ga-url "http://gaserver:8080" --gitlab-url "http://fakegitlab:8081"
	docker stop fakegitlab
