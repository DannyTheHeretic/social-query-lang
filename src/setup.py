"""The Setup Script for pyodide."""

from pathlib import Path

from pyodide.http import pyfetch


async def setup_pyodide_scripts() -> None:
    """Script to do everything for pyodide."""
    response = await pyfetch("./functions.py")
    with Path.open("functions.py", "wb") as f:
        f.write(await response.bytes())
    """
    # uncomment when you add the parser in
    # response = await pyfetch("./parser.py")
    # with open("parser.py", "wb") as f:
    #     f.write(await response.bytes())
    """

    response = await pyfetch("./frontend.py")
    with Path.open("frontend.py", "wb") as f:
        f.write(await response.bytes())
