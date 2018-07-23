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

### Intialize with Docker

```shell
git clone https://github.com/NDHWAlliance/gitlab-analytics.git
cd gitlab-analytics
docker-compose up mysql grafana ga
```
 
### Configuration
* Step 1: Access flaks's root with port 8080, like: http://127.0.0.1:8080. Submit the configuration to access gitlab and initialize webhook for gitlab's projects. Default webhook(External Url) is the '$base_url/web_hook/' like http://127.0.0.1:8080/web_hook/.
* Step 2: In the addhook page, choose the projects that you would like to add the webhook.
* Step 3: If you would like to bind the webhook to your new project automatically, just configure the system hook '$base_url/system_hook' to your gitlab， like: http:/127.0.0.1:8080/system_hook/.

  
# Reference
* [Install Docker-Compose](https://docs.docker.com/compose/install/)
* [Initializing Grafana with preconfigured dashboards](https://ops.tips/blog/initialize-grafana-with-preconfigured-dashboards/)
* [Dockerize Simple Flask App](http://containertutorials.com/docker-compose/flask-simple-app.html)
* https://hub.docker.com/_/mariadb/
* https://hub.docker.com/r/grafana/grafana/
* [Using MySQL in Grafana - Configure the Datasource with Provisioning](http://docs.grafana.org/features/datasources/mysql/#configure-the-datasource-with-provisioning)
* [Provisioning Grafana](http://docs.grafana.org/administration/provisioning/)
* [Webhook for gitlab's events](http://developer.dpstorm.com/help/user/project/integrations/webhooks.md)
* [System hook for gitlab's evnets](https://docs.gitlab.com/ee/system_hooks/system_hooks.html)
* [Python-gitlab](http://python-gitlab.readthedocs.io/en/stable/gl_objects/system_hooks.html)
