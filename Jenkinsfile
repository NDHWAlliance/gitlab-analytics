node {
   stage('Preparation') { // for display purposes
      sh "(docker network ls | grep ganet) || docker network create ganet"
      sh "docker rm --force gaserver mysql fakegitlab || echo ok"
   }
   stage('Build') {
      sh "docker build -t ga-test:latest -f server/Dockerfile server"
   }
   stage('Test') {
        try {
            sh "docker run -d --rm --network ganet --network-alias mysql --name mysql -v `pwd`/mysql/initdb:/docker-entrypoint-initdb.d -v `pwd`/mysql/conf:/etc/mysql/conf.d -e MYSQL_RANDOM_ROOT_PASSWORD=yes -e MYSQL_DATABASE=gitlab_analytics -e MYSQL_USER=ga -e MYSQL_PASSWORD=4t9wegcvbYSd mariadb:5.5.60"       
            sh "docker run -d --rm --network ganet --network-alias gaserver --name gaserver -e MYSQL_DATABASE=gitlab_analytics -e MYSQL_USER=ga -e MYSQL_PASSWORD=4t9wegcvbYSd -e MYSQL_HOST=mysql -e MYSQL_PORT=3306 -e PORT=8080 ga-test:latest"
            sh "docker run -d --rm --network ganet --network-alias fakegitlab --name fakegitlab -v `pwd`/gatest:/app ga-test:latest  fakegitlab.py --host 0.0.0.0 --port 8081"
            sh "sleep 30"
            sh "docker run --rm --network ganet -v `pwd`/gatest:/app  ga-test:latest gatest.py --ga-url 'http://gaserver:8080' --gitlab-url 'http://fakegitlab:8081'"
        }
        finally {
            sh "docker stop gaserver mysql fakegitlab"
            sh "docker network rm ganet"
        }
   }
}
