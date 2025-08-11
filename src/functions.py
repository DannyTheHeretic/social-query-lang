"""The main script file for Pyodide."""

from js import Event, document
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch

from frontend import CLEAR_BUTTON, EXECUTE_BUTTON, clear_interface, update_table


async def parse_input(_: Event) -> None:
    """Start of the parser."""
    print("testing")
    y = document.getElementById("query-input").value.split("=")
    print(y[-1])  # TODO: Put SQL Parser in # tokenize(y) from parser import tokenize
    await get_user_data(y[-1])


async def get_user_data(user: dict) -> dict:
    """Pyfetch command example."""
    url = f"https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor={user}"
    response = await pyfetch(url)
    val = (await response.json())["feed"]
    tb = document.getElementById("table-body")
    tb.innerHTML = ""
    head = ["Name", "Post"]
    body = []
    for i in val:
        data_point = i["post"]
        try:
            body.append([data_point["author"]["displayName"], data_point["record"]["text"]])
        except KeyError:
            continue  # Handle if a field is missing (no text maybe?)
    update_table(head, body)
    return val


EXECUTE_BUTTON.addEventListener("click", create_proxy(parse_input))
CLEAR_BUTTON.addEventListener("click", create_proxy(clear_interface))
