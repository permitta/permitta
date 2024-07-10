from flask import Flask
from flask.testing import FlaskClient


def test_index(client: FlaskClient):
    response = client.get("/policies/")
    # TODO implement snapshot tests
    assert response.status_code == 200


def test_create_policy(flask_app: Flask, client: FlaskClient):
    # bob is not allowed to create policies
    with client.session_transaction() as session:
        session["userinfo"] = {
            "email": "bob@permitta.co",
        }
    response = client.post("/policies/create", json={"policy_type": "Builder"})
    assert response.status_code == 403

    # alice is allowed to create policies
    with client.session_transaction() as session:
        session["userinfo"] = {
            "email": "alice@permitta.co",
        }
    response = client.post(
        "/policies/create", json={"policy_type": "Builder"}, follow_redirects=True
    )

    # expect one redirect, and to land on /policies
    assert len(response.history) == 1
    assert response.history[0].status_code == 303
    assert response.status_code == 200
    assert response.request.path == "/policies/7"

    # check we have a draft policy with builder type
    assert 'hx-get="/policies/7/object_attributes_tab"' in response.text
    assert "Draft" in response.text


def test_clone_policy(flask_app: Flask, client: FlaskClient):
    # 42 does not exist ;)
    response = client.post("/policies/42/clone")
    assert response.status_code == 404

    # bob is not allowed to clone policies
    with client.session_transaction() as session:
        session["userinfo"] = {
            "email": "bob@permitta.co",
        }
    response = client.post("/policies/1/clone", json={"policy_type": "Builder"})
    assert response.status_code == 403

    # alice is allowed to clone policies
    with client.session_transaction() as session:
        session["userinfo"] = {
            "email": "alice@permitta.co",
        }
    response = client.post("/policies/1/clone")
    assert response.status_code == 200


def test_get_policy(flask_app: Flask, client: FlaskClient):
    # 42 does not exist ;)
    response = client.get("/policies/42")
    assert response.status_code == 404

    # even bob is allowed to view policies
    with client.session_transaction() as session:
        session["userinfo"] = {
            "email": "bob@permitta.co",
        }
    response = client.get("/policies/1")
    assert response.status_code == 200


def test_get_policy_modal(flask_app: Flask, client: FlaskClient):
    pass


def test_set_policy_status(flask_app: Flask, client: FlaskClient):
    response = client.post("/policies/42/status/disabled")
    assert response.status_code == 404

    # bob can't set statuses
    with client.session_transaction() as session:
        session["userinfo"] = {
            "email": "bob@permitta.co",
        }
    response = client.post("/policies/1/status/disabled")
    assert response.status_code == 403

    with client.session_transaction() as session:
        session["userinfo"] = {
            "email": "alice@permitta.co",
        }

    # invalid state
    assert client.post("/policies/5/status/invalid").status_code == 400

    # initial state is Published, expect to be able to clone, req-disable
    assert client.post("/policies/5/status/request-publish").status_code == 403
    assert client.post("/policies/5/status/request-delete").status_code == 200
    assert client.post("/policies/5/status/published").status_code == 403
    assert client.post("/policies/5/status/disabled").status_code == 403

    # TODO test from other states

    # TODO assert admin can publish
    with client.session_transaction() as session:
        session["userinfo"] = {
            "email": "admin@permitta.co",
        }
    assert client.post("/policies/5/status/request-publish").status_code == 200


def test_delete_policy(flask_app: Flask, client: FlaskClient):
    response = client.delete("/policies/42")
    assert response.status_code == 404

    # bob can't delete
    with client.session_transaction() as session:
        session["userinfo"] = {
            "email": "bob@permitta.co",
        }
    response = client.delete("/policies/5")
    assert response.status_code == 403

    # alice can delete policies in draft or disabled
    with client.session_transaction() as session:
        session["userinfo"] = {
            "email": "alice@permitta.co",
        }
    response = client.delete("/policies/1")  # draft
    assert response.status_code == 200

    response = client.delete("/policies/2")  # pending delete
    assert response.status_code == 403

    response = client.delete("/policies/3")  # disabled
    assert response.status_code == 200

    response = client.delete("/policies/4")  # published
    assert response.status_code == 403
