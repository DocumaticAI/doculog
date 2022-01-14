"""
Call the server for intelligent changelog features.
"""
import hashlib
import json
import os
from typing import Dict, List, Optional, Union

import requests

SERVER_DOMAIN = "https://av9kmkrq4f.execute-api.eu-west-2.amazonaws.com/Prod/"


def post(
    endpoint: str, payload: Union[str, List[str]], params: Dict = {}
) -> Optional[Union[str, List[str]]]:
    """
    Call server with changelog info for advanced parsing features.

    If no API key in environment variables, no call if made.
    If API key is present but environment variable is set to run locally,
    then posts to a localhost server instead.

    Parameters
    ----------
    endpoint : str
        The endpoint to query
    payload : str or list of str
        The data to post to the endpoint
    params : dict of {str: Any}. Default = {}
        Optional params to put in the request

    Returns
    -------
    None, str or list of str
        None if POST fails or returns non-200 status code.
        Otherwise, the parsed payload.

    Notes
    -----
    * Sends a POST request to server
    * Sends HASHED project name purely for usage logging purposes
    """
    project_name = os.getenv("DOCULOG_PROJECT_NAME")
    project_name = project_name if project_name else "DefaultProject"

    hashed_project = hashlib.sha224(project_name.encode("utf-8")).hexdigest()

    api_key = os.getenv("DOCUMATIC_API_KEY") or os.getenv("DOCULOG_API_KEY")

    if not api_key:
        return

    _run_locally = os.getenv("DOCULOG_RUN_LOCALLY") == "True"
    _server_domain = SERVER_DOMAIN if not _run_locally else "http://127.0.0.1:3000/"

    request_url = _server_domain + endpoint

    all_params = {"project": hashed_project}
    all_params.update(params)

    try:
        response = requests.post(
            request_url,
            params=all_params,
            data=json.dumps(payload),
            headers={
                "x-api-key": api_key,
                "content-type": "application/json",
            },
        )
    except requests.exceptions.ConnectionError:
        # Happens if running locally but server hasn't set up (or API server has crashed!)
        return None

    if response.status_code == 200:
        message = response.json()["message"]
        if isinstance(message, list):
            return message

        try:
            message = json.loads(message)
        except Exception:
            pass
        return message
    else:
        return None


def validate_key() -> bool:
    """Validate a user's API key by querying the server."""
    project_name = os.getenv("DOCULOG_PROJECT_NAME")
    project_name = project_name if project_name else "DefaultProject"

    hashed_project = hashlib.sha224(project_name.encode("utf-8")).hexdigest()

    api_key = os.getenv("DOCUMATIC_API_KEY") or os.getenv("DOCULOG_API_KEY")

    if not api_key:
        print("DOCUMATIC_API_KEY not in environment")
        return False

    if os.getenv("DOCULOG_RUN_LOCALLY") != "False":
        # Var not set or is running locally (we can't validate key/it doesn't matter)
        return False

    try:
        response = requests.get(
            SERVER_DOMAIN + "validate",
            params={"project": hashed_project},
            headers={"x-api-key": api_key, "content-type": "application/json"},
        )
    except requests.exceptions.ConnectionError:
        return False

    if response.status_code == 200:
        return response.json()["message"]
    else:
        if response.status_code == 403:
            print(
                f"""\nAPI call error: {response.headers['x-amzn-errortype']}.
Please file a bug report if this is unexpected.
doculog can still run, but without advanced features.\n"""
            )
        return False
