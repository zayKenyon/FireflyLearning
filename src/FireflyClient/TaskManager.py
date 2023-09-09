"""Manages API methods for tasks and stores their cache."""
import requests


class TaskManager:
    """Manages API methods for tasks and stores their cache."""

    def __init__(self, client):
        self.client = client
        """The `Client` that instantiated this manager"""
        self.cache: list | None = None
        """The cache of this manager."""

    def __str__(self):
        return self.fetch()

    def fetch(self, options=None) -> list:
        """
        Obtains tasks from Firefly, or the TaskManager `cache` if it's available.

        Args:
            options (dict, optional): Task Fetch options. Defaults to None.
                force (bool): Whether to skip cache, even if it's available.

        Examples:
            Force-fetching even when cache is available, use sparingly.

            >>> <client>.tasks.fetch({force: True})
            ...
        """
        if options is None:
            options = {"force": False}

        if self.cache is not None and options.get("force") is not True:
            return self.cache

        url = f"{self.client.host}/api/v2/taskListing/view/student/tasks/all/filterBy"
        payload = {
            "ffauth_device_id": self.client.device_id,
            "ffauth_secret": self.client.token,
        }
        body = {
            "archiveStatus": "All",
            "completionStatus": "Todo",
            "ownerType": "OnlySetters",
            "page": 0,
            "pageSize": 100,
            "sortingCriteria": [{"column": "DueDate", "order": "Descending"}],
        }

        res = requests.post(
            url=url,
            params=payload,
            json=body,
            cookies=self.client.session,
            timeout=5,
        )
        tasks = res.json()["items"]
        self.cache = tasks
        return tasks
