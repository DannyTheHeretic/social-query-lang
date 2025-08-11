"""The main script file for Pyodide."""

from js import Event, document
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch

from frontend import CLEAR_BUTTON, EXECUTE_BUTTON, clear_interface, update_table


def flatten_response(data: dict) -> dict:
    """Flatten a dictionary."""
    flattened_result = {}

    def _flatten(current: dict, name: str = "") -> dict:
        if isinstance(current, dict):
            for field, value in current.items():
                _flatten(value, name + field + "_")
        elif isinstance(current, list):
            for idx, i in enumerate(current):
                _flatten(i, name + str(idx) + "_")
        else:
            flattened_result[name[:-1]] = current  # Drops the extra _

    _flatten(data)
    return flattened_result


async def parse_input(_: Event) -> None:
    """Start of the parser."""
    y = document.getElementById("query-input").value.split("=")
    # TODO: Put SQL Parser in # tokenize(y) from parser import tokenize
    await get_user_data(y[-1])


async def get_user_data(user: dict) -> dict:
    """Pyfetch command example."""
    url = f"https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor={user}"
    response = await pyfetch(url)
    val = (await response.json())["feed"]
    tb = document.getElementById("table-body")
    tb.innerHTML = ""
    head = []
    body = []

    for i in val:
        data = i["post"]

        d = flatten_response(data)
        body.append(d)
        [head.append(k) for k in d if k not in head]

    update_table(head, body)
    return val


EXECUTE_BUTTON.addEventListener("click", create_proxy(parse_input))
CLEAR_BUTTON.addEventListener("click", create_proxy(clear_interface))
