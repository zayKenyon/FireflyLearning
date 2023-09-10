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
            options (:obj:`dict`, optional): Task Fetch options. Defaults to None.

                - force (:obj:`bool`): Whether to skip cache, even if it's available.
                    - Default: `False`
                - archive_status (:obj:`str`): `All`
                    - Default: `All`
                - completion_status (:obj:`str`): `AllIncludingArchived`, `Todo`,
                `DoneOrArchived`
                    - Default: `Todo`
                - owner_type (:obj:`str`): `OnlySetters`
                    - Default: `OnlySetters`
                - page (:obj:`int`): Results are paginated to prevent query spam.
                    - Default: `0`
                - page_size (:obj:`int`): Number of results per page.
                    - Default: `100`
                - sorting_criteria (:obj:`list[dict]`): `DueDate`, `SetDate`: Can be
                either ascending or descending.
                    - Default: `{ "column": "DueDate", "order": "Descending }`


        Examples:
            Force-fetching even when cache is available, use sparingly.

            >>> <client>.tasks.fetch({"force": True})
            [...]

            Fetch all tasks that have been done.
            >>> <client>.tasks.fetch({"completion_status": "DoneOrArchived"})
            [...]

            Fetch the oldest tasks that have been done.
            >>> <client>.tasks.fetch(
            >>>     {
            >>>         "completion_status": "DoneOrArchived",
            >>>         "sorting_criteria":
            >>>             [
            >>>                 {
            >>>                     "column": "SetDate",
            >>>                     "order": "Ascending"
            >>>                 }
            >>>             ]
            >>>     }
            >>> )
            [...]
        """
        default_body = {
            "archiveStatus": "All",
            "completionStatus": "Todo",
            "ownerType": "OnlySetters",
            "page": 0,
            "pageSize": 100,
            "sortingCriteria": [{"column": "DueDate", "order": "Descending"}],
        }

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
            "archiveStatus": options.get("archive_status")
            or default_body.get("archiveStatus"),
            "completionStatus": options.get("completion_status")
            or default_body.get("completionStatus"),
            "ownerType": options.get("owner_type") or default_body.get("ownerType"),
            "page": options.get("page") or default_body.get("page"),
            "pageSize": options.get("page_size") or default_body.get("pageSize"),
            "sortingCriteria": options.get("sorting_criteria")
            or default_body.get("sortingCriteria"),
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
