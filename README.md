# gitlab-analytics 

### Goals

* Improve the developers' enthusiasm to build more standard gitlab's project. 
* Provide a guidance to the developers for gitlab's features. 
* Analysis the activity of gitlab's users via statistics.
* Support kpi's measurement for project managers.

### Analytics

* commits
* wikis
* issues
* comments
* merge-requests

![alt text](https://github.com/NDHWAlliance/gitlab-analytics/blob/master/display.jpeg)

# Installation

### Prerequest

* A gitlab instance
* A server
  * with docker installed
  * has a domain name or IP that can be accessed by gitlab instance.

Suppose the hostname of the server you deploy gitlab-analytics on is `gitlab-analytics.example.com`

### Initialize with Docker

```shell
git clone https://github.com/NDHWAlliance/gitlab-analytics.git
cd gitlab-analytics
docker-compose up mysql grafana ga
```

If you are a Chinese user, you can use following commands to speed up `ga` image
build process;

```shell
git clone https://github.com/NDHWAlliance/gitlab-analytics.git
cd gitlab-analytics
docker-compose build --build-arg INDEX_URL=https://mirrors.aliyun.com/pypi/simple ga
docker-compose up mysql grafana ga
```



### Configuration

* Step 1: Access `http://gitlab-analytics.example.com:8080` .
  * Set a password to access the setting page.
  * In the setting page
    * Default webhook(External Url) is the '$base_url/web_hook/' like `http://gitlab-analytics.example.com:8080/web_hook/`.
    * set gitlab server URL and access token, the access token should have complete read/write access to gitlab API.
    * If your gitlab's version is higher than 10.6, remember to check the option ["Allow requests to the local network from hooks and services"](https://docs.gitlab.com/ee/security/webhooks.html) in the "Outbound requests" section inside the Admin area under Settings. 
* Step 2: In the hooks page, choose the projects that you would like to add the webhook.
* Step 3: If you would like to bind the webhook to your new project automatically, just configure the system hook '$base_url/system_hook' to your gitlab， like: `http://gitlab-analytics.example.com:8080/system_hook/`.

### analytics page

You can access analytics page from the following URL:

    http://gitlab-analytics.example.com:3000

The default user/password is admin/admin.

### 

# Reference
* [Install Docker-Compose](https://docs.docker.com/compose/install/)
* [Initializing Grafana with preconfigured dashboards](https://ops.tips/blog/initialize-grafana-with-preconfigured-dashboards/)
* [Dockerize Simple Flask App](http://containertutorials.com/docker-compose/flask-simple-app.html)
* https://hub.docker.com/_/mariadb/
* https://hub.docker.com/r/grafana/grafana/
* [Using MySQL in Grafana - Configure the Datasource with Provisioning](http://docs.grafana.org/features/datasources/mysql/#configure-the-datasource-with-provisioning)
* [Provisioning Grafana](http://docs.grafana.org/administration/provisioning/)
* [Webhook for gitlab's events](http://developer.dpstorm.com/help/user/project/integrations/webhooks.md)
* [System hook for gitlab's events](https://docs.gitlab.com/ee/system_hooks/system_hooks.html)
* [Python-gitlab](http://python-gitlab.readthedocs.io/en/stable)
