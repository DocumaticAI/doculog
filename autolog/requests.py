"""
Call the server for intelligent changelog features.
"""
import hashlib
import json
import os
from typing import Dict, List, Optional, Union

import requests

SERVER_DOMAIN = "https://testurl/"


def post(
    endpoint: str, payload: Union[str, List[str]], params: Dict = {}
) -> Optional[Union[str, List[str]]]:
    """
    Call server with changelog info for advanced parsing features.

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
    *
    """
    project_name = os.getenv("AUTOLOG_PROJECT_NAME")
    project_name = project_name if project_name else "DefaultProject"

    hashed_project = hashlib.sha224(project_name.encode("utf-8")).hexdigest()

    api_key = os.getenv("AUTOLOG_API_KEY")

    _run_locally = (os.getenv("AUTOLOG_RUN_LOCALLY") == "True") or not api_key
    _server_domain = SERVER_DOMAIN if not _run_locally else "http://127.0.0.1:3000/"

    request_url = _server_domain + endpoint + f"?project={hashed_project}"

    for _param, _param_value in params.items():
        request_url += f"&{_param}={_param_value}"

    try:
        response = requests.post(
            request_url,
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
