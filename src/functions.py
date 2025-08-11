"""The main script file for Pyodide."""

from js import Event, document  # noqa: I001
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch

from frontend import CLEAR_BUTTON, EXECUTE_BUTTON, clear_interface, update_table
from parser import ParentKind, Token, TokenKind, Tree, parse, tokenize


def flatten_response(data: dict) -> dict:
    """Flatten a dictionary."""
    flattened_result = {}

    def _flatten(current: dict, name: str = "") -> dict:
        if isinstance(current, dict):
            for field, value in current.items():
                _flatten(value, name + field + "_")
        elif isinstance(current, list):
            """old code
            # for idx, i in enumerate(current):
            #     _flatten(i, name + str(idx) + "_")
            """
        else:
            flattened_result[name[:-1]] = current  # Drops the extra _

    _flatten(data)
    return flattened_result


def extract_actor(tree: Tree) -> str | None:
    """Extract the actor from the tree."""
    if not tree.kind == ParentKind.FILE:
        raise ValueError
    stmt = tree.children[0]
    for c in stmt.children:
        if c.kind == ParentKind.WHERE_CLAUSE:
            where_clause = c
            break
    else:
        return None

    expr = where_clause.children[1]

    if expr.kind != ParentKind.EXPR_BINARY or expr.children[1].kind != TokenKind.EQUALS:
        return None

    if (
        expr.children[0].children[0].kind == TokenKind.IDENTIFIER
        and expr.children[0].children[0].text == "actor"
        and expr.children[2].children[0].kind == TokenKind.STRING
    ):
        v = expr.children[2].children[0].text
        return v[1:-1] if v[0] == "'" else v
    if (
        expr.children[2].children[0].kind == TokenKind.IDENTIFIER
        and expr.children[2].children[0].text == "actor"
        and expr.children[0].children[0].kind == TokenKind.STRING
    ):
        v = expr.children[0].children[0].text
        return v[1:-1] if v[0] == "'" else v
    return None


def extract_fields(tree: Tree) -> list[Token] | None:
    """Extract the actor from the tree."""
    if not tree.kind == ParentKind.FILE:
        raise ValueError
    stmt = tree.children[0]
    for c in stmt.children:
        if c.kind == ParentKind.FIELD_LIST:
            return c.children[::2]
            break
    else:
        return None


async def parse_input(_: Event) -> None:
    """Start of the parser."""
    y = document.getElementById("query-input").value
    tokens = parse(tokenize(y))
    # TODO: Put SQL Parser in
    await get_user_data(tokens)


async def get_user_data(tokens: Tree) -> dict:
    """Pyfetch command example."""
    user = extract_actor(tokens)
    fields = extract_fields(tokens)
    field_tokens = [i.children[0] for i in fields if i.kind != TokenKind.STAR]
    url = f"https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor={user}"
    response = await pyfetch(url)
    val = (await response.json())["feed"]
    tb = document.getElementById("table-body")
    tb.innerHTML = ""
    head = []
    if field_tokens:
        head = [j.text for j in field_tokens]
    body = []
    for i in val:
        data = i

        d = flatten_response(data)
        if field_tokens:
            body.append({j: d[j] for j in head})
        else:
            body.append(d)
            [head.append(k) for k in d if k not in head]

    update_table(head, body)
    return val


EXECUTE_BUTTON.addEventListener("click", create_proxy(parse_input))
CLEAR_BUTTON.addEventListener("click", create_proxy(clear_interface))
