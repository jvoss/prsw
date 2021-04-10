import requests

from ripe import Output

RIPE_URL = "https://stat.ripe.net/data"


def _get(url, params):
    url = RIPE_URL + str(url) + "data.json?" + str(params)
    r = requests.get(url)

    return Output(**r.json())
