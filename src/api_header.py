import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict

import settings


def get_gmt_date() -> str:
    """Returns the current GMT date formatted as an HTTP-compatible string."""
    return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())


def get_content_md5(body: Any) -> str:
    """
    Computes the MD5 hash of the given body and returns it as a base64-encoded string.

    Args:
        body (Any): The request body (dictionary or string).

    Returns:
        str: The base64-encoded MD5 hash of the body.
    """
    body_str = json.dumps(body) if isinstance(body, dict) else str(body)
    md5_value = hashlib.md5(body_str.encode("utf-8"))

    return base64.b64encode(md5_value.digest()).decode("utf-8").strip("\n")


def get_sign(content_md5: str, gmt_date: str, canonicalized_resource: str) -> str:
    """
    Generates an HMAC-SHA1 signature required for API authorization.

    Args:
        content_md5 (str): The MD5 hash of the request body.
        gmt_date (str): The request timestamp in GMT.
        canonicalized_resource (str): The API endpoint path.

    Returns:
        str: The base64-encoded signature.
    """
    raw_str = f"{settings.VERB}\n{content_md5}\n{settings.CONTENT_TYPE}\n{gmt_date}\n{canonicalized_resource}"

    hashed = hmac.new(
        settings.API_KEYSECRET.encode("utf-8"),  # type: ignore
        raw_str.encode("utf-8"),
        hashlib.sha1,
    )

    return base64.b64encode(hashed.digest()).decode("utf-8").strip("\n")


def get_auth(sign: str) -> str:
    """
    Generates the API authorization header.

    Args:
        sign (str): The computed signature.

    Returns:
        str: The authorization header value.
    """
    return f"API {settings.API_KEYID}:{sign}"


def get_request_header(endpoint: str, body: Any) -> Dict[str, str]:
    """
    Generates the request headers required for API authentication.

    Args:
        endpoint (str): The API endpoint.
        body (Any): The request body (dictionary or string).

    Returns:
        Dict[str, str]: A dictionary containing the required headers.
    """
    canonicalized_resource = f"/v1/api/{endpoint}"
    content_md5 = get_content_md5(body)
    gmt_date = get_gmt_date()

    sign = get_sign(content_md5, gmt_date, canonicalized_resource)
    auth = get_auth(sign)

    return {
        "Content-MD5": content_md5,
        "Content-Type": settings.CONTENT_TYPE,
        "Date": gmt_date,
        "Authorization": auth,
    }

