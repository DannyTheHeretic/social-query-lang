"""The main script file for Pyodide."""

from js import Event, document, window
from pyodide.ffi import create_proxy

import frontend  # noqa: F401
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
            flattened_result[name[:-1].lower()] = current  # Drops the extra _

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
    tree: Tree = parse(tokenize(y))
    await get_author_feed(tree)


async def get_user_timeline(tokens: Tree) -> dict:
    """Get the current users timeline."""
    fields = extract_fields(tokens)
    field_tokens = [i.children[0] for i in fields if i.kind != TokenKind.STAR]
    feed = await window.session.get_timeline()
    val = feed["feed"]
    tb = document.getElementById("table-body")
    tb.innerHTML = ""
    head = []
    if field_tokens:
        head = [j.text for j in field_tokens]
    body = []
    for i in val:
        data = i

        # Extract any embedded images from the post and put their link in data
        post = data["post"]
        if "embed" in post:
            embed_type = post["embed"]["$type"]
            images = None
            if embed_type == "app.bsky.embed.images#view":
                images = post["embed"]["images"]
            image_links = []
            if images:
                for image in images:
                    image_link = image["thumb"]
                    image_links.append(image_link)
            if image_links:
                post["images"] = " | ".join(image_links)

        d = flatten_response(data)
        if field_tokens:
            body.append({j: d[j.lower()] for j in head})
        else:
            body.append(d)
            [head.append(k) for k in d if k not in head]

    update_table(head, body)
    return val


async def get_author_feed(tokens: Tree) -> dict:
    """Get a given actors feed."""
    user = extract_actor(tokens)
    fields = extract_fields(tokens)
    field_tokens = [i.children[0] for i in fields if i.kind != TokenKind.STAR]
    feed = await window.session.get_author_feed(user)
    val = feed["feed"]
    tb = document.getElementById("table-body")
    tb.innerHTML = ""
    head = []
    if field_tokens:
        head = [j.text for j in field_tokens]
    body = []
    for i in val:
        data = i

        # Extract any embedded images from the post and put their link in data
        # This throws an error if post_images is used
        # as a field and no posts returned have any images...
        post = data["post"]
        if "embed" in post:
            embed_type = post["embed"]["$type"]
            images = None
            if embed_type == "app.bsky.embed.images#view":
                images = post["embed"]["images"]
            image_links = []
            if images:
                for image in images:
                    image_link = image["thumb"]
                    image_links.append(image_link)
            if image_links:
                post["images"] = " | ".join(image_links)

        d = flatten_response(data)
        if field_tokens:
            body.append({j: d[j.lower()] for j in head})
        else:
            body.append(d)
            [head.append(k) for k in d if k not in head]

    update_table(head, body)
    return val


EXECUTE_BUTTON.addEventListener("click", create_proxy(parse_input))
CLEAR_BUTTON.addEventListener("click", create_proxy(clear_interface))
