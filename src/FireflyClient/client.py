from xml.etree import ElementTree

import requests

from .exceptions import InvalidSchoolCode


class Client:
    """
    Represents an integration between the user and Firefly's integrations.
    """

    def __init__(self, config):
        self.school_code = config["SCHOOL_CODE"]
        self.host = self.__get_school_portal()

    def __get_school_portal(self) -> str:
        """
        Uses the school code written in the config file to fetch the
        corresponding Firefly portal page.

        Raises:
            InvalidSchoolCode: Thrown whenever the client cannot establish a
            connection with the attempted school portal.
        :return: URL of school portal.
        """
        res = requests.get(
            url="https://appgateway.fireflysolutions.co.uk"
            f"/appgateway/school/{self.school_code}",
            timeout=5,
        )
        root = ElementTree.fromstring(res.text)

        if not root.attrib.get("exists") or not root.attrib.get("enabled"):
            raise InvalidSchoolCode

        address = root.find("address")
        return f"http{(address.get('ssl') == 'true') * 's'}://{address.text}"

    def get_api_version(self) -> str:
        """
        Fetches the current API version of Firefly.
        :return: API version "v.X.Y.Z"
        """
        res = requests.get(url=f"{self.host}/login/api/version", timeout=5)
        root = ElementTree.fromstring(res.text)

        major_version = root.find("majorVersion").text
        minor_version = root.find("minorVersion").text
        increment_version = root.find("incrementVersion").text

        return f"v{major_version}.{minor_version}.{increment_version}"
