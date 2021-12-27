import hashlib
import json
import os
from unittest import mock

import pytest
import responses

from autolog.requests import SERVER_DOMAIN, post


class TestPost:
    @responses.activate
    @pytest.mark.parametrize("endpoint", ("", "tester", "summarise_function"))
    def test_posts_to_endpoint(self, endpoint):
        responses.add(
            responses.POST, SERVER_DOMAIN + endpoint, json={"message": "test"}
        )
        os.environ["AUTOLOG_API_KEY"] = "12345"
        os.environ["AUTOLOG_PROJECT_NAME"] = "Autolog"

        post(endpoint, "test payload")

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url.split("/")[-1].split("?")[0] == endpoint

    @responses.activate
    @mock.patch.dict(
        os.environ,
        {
            "AUTOLOG_API_KEY": "12345",
            "AUTOLOG_PROJECT_NAME": "Autolog",
            "AUTOLOG_RUN_LOCALLY": "False",
        },
    )
    def test_receives_and_parses_list(self):
        responses.add(
            responses.POST,
            SERVER_DOMAIN + "test",
            json={"message": json.dumps([1, 2, 3, 4])},
        )

        response = post("test", "test payload")
        assert response == [1, 2, 3, 4]

    @responses.activate
    @mock.patch.dict(
        os.environ,
        {
            "AUTOLOG_API_KEY": "12345",
            "AUTOLOG_PROJECT_NAME": "Autolog",
            "AUTOLOG_RUN_LOCALLY": "False",
        },
    )
    def test_receives_and_parses_string(self):
        responses.add(
            responses.POST,
            SERVER_DOMAIN + "test",
            json={"message": json.dumps("some string result")},
        )

        response = post("test", "test payload")
        assert response == "some string result"

    @responses.activate
    @mock.patch.dict(
        os.environ,
        {
            "AUTOLOG_API_KEY": "12345",
            "AUTOLOG_PROJECT_NAME": "Autolog",
            "AUTOLOG_RUN_LOCALLY": "False",
        },
    )
    def test_receives_and_parses_dict(self):
        responses.add(
            responses.POST,
            SERVER_DOMAIN + "test",
            json={
                "message": json.dumps({"summary": "some string result", "num_calls": 1})
            },
        )

        response = post("test", "test payload")
        assert response == {"summary": "some string result", "num_calls": 1}

    @responses.activate
    @pytest.mark.parametrize(
        "project_name", ("some-project", "MyProj!", "A.Cool.Project")
    )
    def test_posts_with_hashed_project_name(self, project_name):
        endpoint = "test"
        responses.add(
            responses.POST, SERVER_DOMAIN + endpoint, json={"message": "test"}
        )
        os.environ["AUTOLOG_API_KEY"] = "12345"
        os.environ["AUTOLOG_PROJECT_NAME"] = project_name

        expected_hash = hashlib.sha224(project_name.encode("utf-8")).hexdigest()

        post(endpoint, "test payload")
        actual_request = responses.calls[0].request

        assert actual_request.params["project"] == expected_hash
        assert len(actual_request.params) == 1

    @responses.activate
    def test_posted_with_hashed_project_default_if_env_var_not_set(self):
        if "AUTOLOG_PROJECT_NAME" in os.environ:
            del os.environ["AUTOLOG_PROJECT_NAME"]

        endpoint = "test"

        responses.add(
            responses.POST, SERVER_DOMAIN + endpoint, json={"message": "test"}
        )

        expected_hash = hashlib.sha224("DefaultProject".encode("utf-8")).hexdigest()

        post(endpoint, "test payload")
        actual_request = responses.calls[0].request

        assert actual_request.params["project"] == expected_hash
        assert len(actual_request.params) == 1

    @responses.activate
    def test_can_post_list_data(self):
        endpoint = "test"
        responses.add(
            responses.POST, SERVER_DOMAIN + endpoint, json={"message": "test"}
        )
        os.environ["AUTOLOG_API_KEY"] = "12345"
        os.environ["AUTOLOG_PROJECT_NAME"] = "some-project"

        post(endpoint, ["some", "data"])
        assert len(responses.calls) == 1

    @responses.activate
    def test_can_post_str_data(self):
        endpoint = "test"
        responses.add(
            responses.POST, SERVER_DOMAIN + endpoint, json={"message": "test"}
        )
        os.environ["AUTOLOG_API_KEY"] = "12345"
        os.environ["AUTOLOG_PROJECT_NAME"] = "some-project"

        post(endpoint, "import json\n\nclass A:\npass")
        assert len(responses.calls) == 1

    @responses.activate
    @pytest.mark.parametrize("api_key", ("12345", "aggj!33"))
    def test_reads_api_from_environ_and_includes_in_header(self, api_key):
        endpoint = "test"
        responses.add(
            responses.POST, SERVER_DOMAIN + endpoint, json={"message": "test"}
        )
        os.environ["AUTOLOG_API_KEY"] = api_key
        os.environ["AUTOLOG_PROJECT_NAME"] = "MyProject"

        post(endpoint, "test payload")
        actual_request = responses.calls[0].request

        assert actual_request.headers["x-api-key"] == api_key

    @responses.activate
    @mock.patch.dict(
        os.environ,
        {
            "AUTOLOG_API_KEY": "12345",
            "AUTOLOG_PROJECT_NAME": "some-proj",
            "AUTOLOG_RUN_LOCALLY": "True",
        },
    )
    def test_calls_local_host_if_env_var_set_to_true(self):
        endpoint = "test"
        responses.add(
            responses.POST,
            f"http://127.0.0.1:3000/{endpoint}",
            json={"message": "test"},
        )

        post(endpoint, "test payload")
        assert len(responses.calls) == 1

    @responses.activate
    @mock.patch.dict(
        os.environ,
        {
            "AUTOLOG_PROJECT_NAME": "some-proj",
            "AUTOLOG_RUN_LOCALLY": "False",
        },
    )
    def test_calls_local_if_run_local_is_false_but_api_key_not_set(self):
        if "AUTOLOG_API_KEY" in os.environ:
            del os.environ["AUTOLOG_API_KEY"]

        endpoint = "test"
        responses.add(
            responses.POST,
            f"http://127.0.0.1:3000/{endpoint}",
            json={"message": "test"},
        )

        post(endpoint, "test payload")
        assert len(responses.calls) == 1

    @responses.activate
    @mock.patch.dict(
        os.environ,
        {
            "AUTOLOG_API_KEY": "12345",
            "AUTOLOG_PROJECT_NAME": "some-proj",
            "AUTOLOG_RUN_LOCALLY": "False",
        },
    )
    def test_calls_server_if_env_var_set_to_false(self):
        endpoint = "test"
        responses.add(
            responses.POST, SERVER_DOMAIN + endpoint, json={"message": "test"}
        )

        post(endpoint, "test payload")
        assert len(responses.calls) == 1

    @responses.activate
    @mock.patch.dict(
        os.environ, {"AUTOLOG_API_KEY": "12345", "AUTOLOG_PROJECT_NAME": "some-proj"}
    )
    def test_calls_server_if_env_var_not_set(self):
        endpoint = "test"
        responses.add(
            responses.POST, SERVER_DOMAIN + endpoint, json={"message": "test"}
        )

        post(endpoint, "test payload")
        assert len(responses.calls) == 1

    @mock.patch.dict(
        os.environ,
        {
            "AUTOLOG_API_KEY": "12345",
            "AUTOLOG_PROJECT_NAME": "some-proj",
            "AUTOLOG_RUN_LOCALLY": "True",
        },
    )
    def test_returns_None_if_cannot_connect_to_server(self):
        endpoint = "test"
        assert post(endpoint, "test payload") is None

    @responses.activate
    @mock.patch.dict(
        os.environ,
        {
            "AUTOLOG_API_KEY": "12345",
            "AUTOLOG_PROJECT_NAME": "Autolog",
        },
    )
    @pytest.mark.parametrize("paramvalue", (5, "somestring"))
    def test_can_add_optional_params(self, paramvalue):
        responses.add(
            responses.POST,
            SERVER_DOMAIN + "test",
            json={"message": json.dumps([1, 2, 3, 4])},
        )

        post("test", "test", params={"somekey": paramvalue})
        call_params = responses.calls[0].request.params

        assert call_params["somekey"] == str(paramvalue)

    @responses.activate
    @mock.patch.dict(
        os.environ,
        {
            "AUTOLOG_API_KEY": "12345",
            "AUTOLOG_PROJECT_NAME": "Autolog",
        },
    )
    def test_can_add_multiple_params(self):
        responses.add(
            responses.POST,
            SERVER_DOMAIN + "test",
            json={"message": json.dumps([1, 2, 3, 4])},
        )

        post("test", "test", params={"somekey": 555, "anotherkey": "testparam"})
        call_params = responses.calls[0].request.params

        assert call_params["somekey"] == "555"
        assert call_params["anotherkey"] == "testparam"
