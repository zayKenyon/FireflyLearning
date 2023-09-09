"""Firefly API Wrapper."""
import datetime
import urllib.parse
from xml.etree import ElementTree

import requests

from .Exceptions import InvalidSchoolCodeError, HandshakeError


class Client:
    """
    Represents an integration between the user and Firefly's integrations.
    """

    def __init__(self, config):
        """🤖"""
        self._device_id: str = config["DEVICE_ID"]
        """Id of the device this is being ran on."""
        self._app_id: str = config["APP_ID"]
        """Id of the app this is being ran through."""
        self.school_code: str = config["SCHOOL_CODE"]
        """School code this is being hosted by."""
        self.host: str = self.__get_school_portal
        """School's unique Firefly domain."""
        self.token: str = config["TOKEN"] or None
        """Used to authenticate requests."""
        self.session_id: str | None = None
        """Cached 🍪 to avoid re-authentication."""
        self.ready_at: datetime.datetime | None = None
        """Time at which the client was last regarded as being authenticated."""

        self.__create_integration()

    def __str__(self):
        return f"""AppId: {self._app_id}
DeviceId: {self._device_id}
SessionId: {self.session_id}
ReadyAt: {self.ready_at}
Token: {self.token}
Code: {self.school_code}
Host: {self.host}"""

    def __create_integration(self) -> bool:
        """
        Either begins the workflow for creating an integration, or, verifies that the
        existing one is still valid.

        Returns:
            bool: True if integration created or authenticated, otherwise False.

        Raises:
            HandshakeError: Invalid Token Supplied.
        """
        if self.token == "<REMOVE ME>":
            raise HandshakeError

        if self.token is None:
            token_url = (
                f"{self.host}/login/api/gettoken"
                f"?ffauth_device_id={self._device_id}"
                f"&ffauth_secret"
                f"&device_id={self._device_id}"
                f"&app_id={self._app_id}"
            )
            sanitised_token_url = urllib.parse.quote(token_url.encode("utf-8"))
            login_url = f"{self.host}/login/login.aspx?prelogin={sanitised_token_url}"
            print(
                "<!> USER ACTION REQUIRED\nPLEASE USE THE FOLLOWING LINK"
                "\nTHEN ENTER TOKEN INTO .env",
                "\n",
                login_url,
            )
            return False

        if self.__verify_integration():
            self.ready_at = datetime.datetime.now()
            return True

        return False

    def __verify_integration(self) -> bool:
        """
        Verifies whether the Client can successfully connect to the API.

        Returns:
            bool: True if valid.

        Raises:
            HandshakeError: If the Client could not authenticate.
        """
        url = (
            f"{self.host}/login/api/verifytoken"
            f"?ffauth_device_id={self._device_id}"
            f"&ffauth_secret={self.token}"
        )
        res = requests.get(url=url, timeout=5)

        if not res.ok or res.json()["valid"] is False:
            raise HandshakeError

        self.session_id = res.cookies["ASP.NET_SessionId"]
        return True

    @property
    def __get_school_portal(self) -> str:
        """
        Uses the school code written in the config file to fetch the
        corresponding Firefly portal page.

        Raises:
            InvalidSchoolCodeError: Thrown whenever the client cannot establish a
            connection with the attempted school portal.

        Returns:
             URL of school portal.
        """
        res = requests.get(
            url="https://appgateway.fireflysolutions.co.uk"
            f"/appgateway/school/{self.school_code}",
            timeout=5,
        )
        root = ElementTree.fromstring(res.text)

        if not root.attrib.get("exists") or not root.attrib.get("enabled"):
            raise InvalidSchoolCodeError

        address = root.find("address")
        return f"http{(address.get('ssl') == 'true') * 's'}://{address.text}"

    @property
    def api_version(self) -> str:
        """
        Fetches the current API version of Firefly.

        Returns:
             API version "v.X.Y.Z"
        """
        res = requests.get(url=f"{self.host}/login/api/version", timeout=5)
        root = ElementTree.fromstring(res.text)

        major_version = root.find("majorVersion").text
        minor_version = root.find("minorVersion").text
        increment_version = root.find("incrementVersion").text

        return f"v{major_version}.{minor_version}.{increment_version}"
