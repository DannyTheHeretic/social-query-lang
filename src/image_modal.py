from io import BytesIO

from ascii_magic import AsciiArt
from js import Event, document, window
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch

IMAGE_MODAL = document.getElementById("image-modal")
ASCII_DISPLAY = document.getElementById("ascii-display")
ALT_TEXT = document.getElementById("image-alt-text")
FULL_SIZE_LINK = document.getElementById("image-modal-full-link")
CLOSE_BUTTON = document.getElementById("image-modal-close")

_image_cache = {}


async def show_image_modal(thumb_link: str, fullsize_link: str, alt: str) -> None:
    """Show the image modal with the given link."""
    IMAGE_MODAL.style.display = "block"
    FULL_SIZE_LINK.href = fullsize_link or thumb_link
    ALT_TEXT.textContent = alt
    ASCII_DISPLAY.textContent = ""
    ascii_img = await load_image(thumb_link)
    ASCII_DISPLAY.textContent = ascii_img


def hide_image_modal(_: Event) -> None:
    """Hide the image modal."""
    IMAGE_MODAL.style.display = "none"
    ASCII_DISPLAY.textContent = ""


# TODO: Fix styling ;)


async def load_image(url: str) -> str:
    """Load an image as monochrome ascii."""
    if url in _image_cache:  # "Cache" the images for speeding up things.
        return _image_cache[url]

    blob_url = await window.session.get_blob(url)
    res = await pyfetch(blob_url)
    bites = BytesIO(await res.bytes())
    ascii_image = AsciiArt.from_image(bites)
    ascii_image = AsciiArt.from_image(bites)
    ascii_str = ascii_image.to_ascii(columns=100, monochrome=True)
    _image_cache[url] = ascii_str
    return ascii_str


CLOSE_BUTTON.addEventListener("click", create_proxy(hide_image_modal))
