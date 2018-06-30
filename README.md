# gitlab-analytics 

### Goals
* Improve the developers' enthusiasm to build more standard gitlab's project. 
* Provide a guidence to the developers for gitlab's features. 
* Analysis the activity of gitlab's users via statistics.
* Support kpi's measurement for project managers.

### Analytics
* commits
* wikis
* issues
* comments
* merge-requests

# Installation

### Install & Start with Docker

```shell
git clone https://github.com/NDHWAlliance/gitlab-analytics.git
cd gitlab-analytics
docker-compose up mysql grafana ga
```
 
### Configuration
Configure your gitlab's url and private_token.

```shell
cd server && cp config.ini.tpl config.ini
```

```ini
[gitlab]
url = http://your.github.com 
private_token = YourPrivateToken
```
  
# Reference
* [Initializing Grafana with preconfigured dashboards](https://ops.tips/blog/initialize-grafana-with-preconfigured-dashboards/)
* [Dockerize Simple Flask App](http://containertutorials.com/docker-compose/flask-simple-app.html)
* https://hub.docker.com/_/mariadb/
* https://hub.docker.com/r/grafana/grafana/
* [Using MySQL in Grafana - Configure the Datasource with Provisioning](http://docs.grafana.org/features/datasources/mysql/#configure-the-datasource-with-provisioning)
* [Provisioning Grafana](http://docs.grafana.org/administration/provisioning/)
