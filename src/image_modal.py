from io import BytesIO

from ascii_magic import AsciiArt
from js import Event, document, window
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch

IMAGE_MODAL = document.getElementById("image-modal")
ASCII_DISPLAY = document.getElementById("ascii-display")
CLOSE_BUTTON = document.getElementById("image-modal-close")


async def show_image_modal(link: str) -> None:
    """Show the image modal with the given link."""
    IMAGE_MODAL.style.display = "block"
    ascii = await load_image(link)
    ASCII_DISPLAY.textContent = ascii


def hide_image_modal(_: Event) -> None:
    """Hide the image modal."""
    IMAGE_MODAL.style.display = "none"
    ASCII_DISPLAY.textContent = ""


# TODO: Add alt text
# TODO: Fix styling ;)


async def load_image(url: str) -> str:
    """Load an image as monochrome ascii."""
    url = await window.session.get_blob(url)
    res = await pyfetch(url)
    bites = BytesIO(await res.bytes())
    ascii_image = AsciiArt.from_image(bites)
    return ascii_image.to_ascii(columns=100, monochrome=True)


CLOSE_BUTTON.addEventListener("click", create_proxy(hide_image_modal))
