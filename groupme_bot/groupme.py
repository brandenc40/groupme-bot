import httpx

_status_codes = {
    200: "Success!",
    201: "Resource was created successfully.",
    204: "Resource was deleted successfully.",
    304: "There was no new data to return.",
    400: "Returned when an invalid format or invalid data is specified in the request.",
    401: "Authentication credentials were missing or incorrect.",
    403: "The request is understood, but it has been refused.",
    404: "The URI requested is invalid or the resource requested, such as a user, does not exists.",
    420: "You are being rate limited. Chill the heck out.",
    500: "Something unexpected occurred. GroupMe will be notified.",
    502: "GroupMe is down or being upgraded.",
    503: "The GroupMe servers are up, but overloaded with requests. Try again later."
}


def status_code_message(code: int):
    return _status_codes.get(code, "Unknown status code")


class GroupMeException(Exception):
    pass


class GroupMe(object):
    __slots__ = 'groupme_api_token'

    def __init__(self, groupme_api_token: str):
        self.groupme_api_token: str = groupme_api_token

    def image_url_to_groupme_image_url(self, image_url: str) -> str:
        """
        Convert a normal image URL to a GroupMe image
        :param str image_url: The URL for any image
        :return str: The URL for the converted GroupMe image
        """
        with httpx.Client() as client:
            res = client.get(image_url)
            res.raise_for_status()
            headers = {
                'X-Access-Token': self.groupme_api_token,
                'Content-Type': res.headers['Content-type'],
            }
            res = client.post(
                'https://image.groupme.com/pictures',
                headers=headers,
                content=res.content
            )
            res.raise_for_status()
            res = res.json()
            return res['payload']['picture_url']

    def get_group(self, group_id: str) -> dict:
        """
        Get a summary of the group from the GroupMe API
        :return dict:
        """
        return self.__get(f'/groups/{group_id}')

    def __get(self, path: str) -> dict:
        res = httpx.get(
            f'https://api.groupme.com/v3{path}',
            params={'token': self.groupme_api_token}
        )
        res.raise_for_status()
        res = res.json()
        status_code = res['meta']['code']
        if status_code <= 299:
            return res['response']
        elif status_code >= 400:
            msg = status_code_message(status_code)
            errors = res.get('meta', {}).get('errors', '')
            raise GroupMeException(f"{status_code} {msg} {str(errors)}")
