"""The Setup Script for pyodide."""

from pathlib import Path

import micropip
from pyodide.http import pyfetch


async def setup_pyodide_scripts() -> None:
    """Script to do everything for pyodide."""
    response = await pyfetch("./core/functions.py")
    with Path.open("functions.py", "wb") as f:
        f.write(await response.bytes())

    response = await pyfetch("./core/parser.py")
    with Path.open("parser.py", "wb") as f:
        f.write(await response.bytes())

    response = await pyfetch("./ui/image_modal.py")
    with Path.open("image_modal.py", "wb") as f:
        f.write(await response.bytes())

    response = await pyfetch("./ui/frontend.py")
    with Path.open("frontend.py", "wb") as f:
        f.write(await response.bytes())
    await micropip.install("ascii_magic")

    response = await pyfetch("./api/auth_session.py")
    with Path.open("auth_session.py", "wb") as f:
        f.write(await response.bytes())

    response = await pyfetch("./ui/auth_modal.py")
    with Path.open("auth_modal.py", "wb") as f:
        f.write(await response.bytes())
