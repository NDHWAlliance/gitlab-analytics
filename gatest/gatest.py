import requests
import re
import click


@click.command()
@click.option("--ga-url", default="http://127.0.0.1:8080")
@click.option("--gitlab-url", default="http://127.0.0.1:8081")
@click.option("--private-token", default="private_token")
def run(ga_url, gitlab_url, private_token):
    s = requests.Session()
    # TODO waiting database ready

    # http://docs.python-requests.org/en/master/api/#requests.Response
    r = s.get(ga_url + "/signup", allow_redirects=False)
    # assert r.status_code == 200

    r = s.post(ga_url + "/signup", data={"password": "owen"},
               allow_redirects=False)
    assert r.status_code == 302
    assert r.headers['Location'] == ga_url + "/signin"

    # TODO check setting table

    r = s.post(ga_url + "/signin", data={"password": "owen"},
               allow_redirects=False)
    assert r.status_code == 302
    assert r.headers['Location'] == ga_url + "/settings"

    data = {"external_url": ga_url + "/webhook/",
            "gitlab_url": gitlab_url,
            "private_token": private_token}
    r = s.post(ga_url + "/settings", data=data, allow_redirects=False)
    assert r.status_code == 302
    assert r.headers['Location'] == ga_url + "/hooks"

    r = s.get(ga_url + "/hooks")
    assert r.status_code == 200
    #    var projects = [{'id': 4, 'url': 'http://example.com/diaspora/diaspora-client', 'hooked': 0, 'loading': 0}]
    ret = re.search("var projects = (\[.*\])", r.text, re.MULTILINE)
    assert ret is not None
    assert len(ret.group(1)) > 2

    r = s.post(ga_url + "/add_hook_to_project", json={"id": "1"})
    assert r.status_code == 200

    print("integration test finished")


if __name__ == '__main__':
    run()
