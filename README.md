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

### Add hook

```shell
virtualenv -p python env
source env/bin/activate
pip install --editable .
python base_git.py hook -r http://**/api/v4 -t your-private-token -h somehook
```
