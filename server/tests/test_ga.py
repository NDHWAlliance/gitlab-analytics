import os
import tempfile
from functools import wraps
import decorator
import pytest
import peewee
from flask import url_for
from ga import create_app
from ga.services import dbservice
from ga.models.gitlab_analytics_models import *

fake_db = peewee.SqliteDatabase(':memory:')


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    c = app.test_client()
    with app.app_context():
        # init db ...
        pass
    yield c

    # do some cleanup staff


# 参考 https://stackoverflow.com/questions/19614658/how-do-i-make-pytest-fixtures-work-with-decorated-functions
# 参考 https://github.com/coleifer/peewee/issues/1450#issuecomment-362326035
def use_test_database(models):
    def real_decorator(func):
        def wrapper(func, *args, **kwargs):
            with fake_db.bind_ctx(models):
                fake_db.create_tables(models)
                try:
                    ret = func(*args, **kwargs)
                finally:
                    fake_db.drop_tables(models)
            return ret

        return decorator.decorator(wrapper, func)

    return real_decorator


@use_test_database([Settings])
def test_settings2():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_request_context():
        c = app.test_client()
        ret = c.get("/")
        # ret 文档 http://werkzeug.pocoo.org/docs/0.14/wrappers/#werkzeug.wrappers.Response
        assert ret.status_code == 302
        # assert url_for(".setup", _external=True) == ret.location

        ret = c.get("/get_db_status")
        import json
        d = json.loads(ret.data)
        assert d['connected']

        # print(dir(Settings._meta))
        # assert Settings._meta.database.connect() == ""

    # ret = client.post('/signup',{"password":"owen"})


@use_test_database([Settings])
def test_signup():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_request_context():
        c = app.test_client()
        ret = c.get("/signup")
        assert ret.status_code == 200

        ret = c.post('/signup', data={"password": "owen"})
        assert ret.status_code == 302
        assert ret.location == url_for(".signin", _external=True)

        ret = c.get("/signup")
        assert ret.status_code == 302
        assert ret.location == url_for(".signin", _external=True)

        ret = c.post('/signin', data={"password": "owenx"})
        assert ret.status_code == 302
        assert ret.location == url_for(".signin", _external=True)

        ret = c.post('/signin', data={"password": "owen"})
        assert ret.status_code == 302
        assert ret.location == url_for(".settings", _external=True)

        r = Settings.get_or_none(name="external_url")
        assert r is None
        ret = c.post('/settings', data={"external_url": "x", "gitlab_url": "y",
                                        "private_token": "z"})
        assert ret.status_code == 302
        assert ret.location == url_for(".hooks", _external=True)

        r = Settings.get_or_none(name="external_url")
        assert r is not None
        assert r.value == "x"


@use_test_database([Settings])
def test_settings1():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_request_context():
        assert app.config.get('external_url') is None
        dbservice.load_settings()
        assert app.config.get('external_url') is ''
        dbservice.save_settings({"external_url": "x",
                                 "gitlab_url": "y",
                                 "private_token": "z"})
        assert app.config.get('external_url') is 'x'


@use_test_database([Settings])
def test_password():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_request_context():
        assert dbservice.is_initialized()
        assert not dbservice.password_exists()

        dbservice.save_password("owen")

        assert dbservice.password_exists()
        assert dbservice.check_password("owen")

        from ga.services import adminservice
        assert adminservice.login("owen")

        assert not adminservice.login("xxx")

        # v1 password
        r = Settings.get_or_none(name="password")
        r.value = dbservice._password_salt("xxx")
        r.save()
        assert adminservice.login("xxx")
