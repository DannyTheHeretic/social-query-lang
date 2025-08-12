from js import Element, Event, document, window
from pyodide.ffi import create_proxy
from pyodide.ffi.wrappers import set_timeout

try:
    import frontend
except ImportError:
    frontend = None

# dom
AUTH_MODAL = None
LOGIN_BTN = None
STEALTH_BTN = None
USERNAME_INPUT = None
PASSWORD_INPUT = None
AUTH_FORM = None

# authentication data
auth_data = None
is_modal_visible = False


def init_auth_modal() -> None:
    """Initialize the authentication modal."""
    global AUTH_MODAL, LOGIN_BTN, STEALTH_BTN, USERNAME_INPUT, PASSWORD_INPUT, AUTH_FORM  # noqa: PLW0603

    AUTH_MODAL = document.getElementById("auth-modal")
    LOGIN_BTN = document.getElementById("login-btn")
    STEALTH_BTN = document.getElementById("stealth-btn")
    USERNAME_INPUT = document.getElementById("bluesky-username")
    PASSWORD_INPUT = document.getElementById("bluesky-password")
    AUTH_FORM = document.getElementById("auth-form")

    setup_event_listeners()
    print("Auth modal initialized")


def setup_event_listeners() -> None:
    """Configure event listeners for the modal."""
    USERNAME_INPUT.addEventListener("input", create_proxy(on_input_change))
    PASSWORD_INPUT.addEventListener("input", create_proxy(on_input_change))
    AUTH_FORM.addEventListener("submit", create_proxy(on_form_submit))
    STEALTH_BTN.addEventListener("click", create_proxy(on_stealth_click))
    document.addEventListener("keydown", create_proxy(on_keydown))


def on_input_change(event: Event) -> None:
    """Trigger visual effects on input change."""
    target = event.target
    target.style.borderColor = "#66ff66"

    def reset_border() -> None:
        target.style.borderColor = "#00ff00"

    set_timeout(create_proxy(reset_border), 300)


def on_form_submit(event: Event) -> None:
    """Handle form submission."""
    event.preventDefault()
    handle_authentication()


def on_stealth_click(_event: Event) -> None:
    """Handle click on stealth mode."""
    handle_stealth_mode()


def on_keydown(event: Event) -> None:
    """Keyboard shortcuts - not visually indicated *yet?."""
    if not is_modal_visible:
        return

    if event.key == "Escape":
        handle_stealth_mode()
    elif event.key == "Enter" and (event.ctrlKey or event.metaKey):
        handle_authentication()


def show_modal() -> None:
    """Show the modal."""
    global is_modal_visible  # noqa: PLW0603

    if AUTH_MODAL:
        AUTH_MODAL.classList.add("show")
        is_modal_visible = True

        def focus_username() -> None:
            if USERNAME_INPUT:
                USERNAME_INPUT.focus()

        set_timeout(create_proxy(focus_username), 500)
        print("Auth modal shown")


def hide_modal() -> None:
    """Hide the modal."""
    if AUTH_MODAL:
        AUTH_MODAL.style.opacity = "0"

        def complete_hide() -> None:
            global is_modal_visible  # noqa: PLW0603
            AUTH_MODAL.classList.remove("show")
            AUTH_MODAL.style.display = "none"
            is_modal_visible = False

        set_timeout(create_proxy(complete_hide), 500)
        print("Auth modal hidden")


def handle_authentication() -> None:
    """Capture authentication data."""
    username = USERNAME_INPUT.value.strip()
    password = PASSWORD_INPUT.value.strip()

    if not username or not password:
        show_input_error()
        return

    LOGIN_BTN.disabled = True
    LOGIN_BTN.innerHTML = 'AUTHENTICATING<span class="loading-dots"></span>'

    print(f"Capturing auth data for: {username}")

    def complete_auth() -> None:
        global auth_data  # noqa: PLW0603

        # catch and store authentication data
        auth_data = {"username": username, "password": password, "mode": "authenticated"}

        LOGIN_BTN.innerHTML = "AUTHENTICATED ✓"
        LOGIN_BTN.style.background = "#004400"

        def finish_auth() -> None:
            hide_modal()
            on_auth_complete(auth_data)

        set_timeout(create_proxy(finish_auth), 1000)

    set_timeout(create_proxy(complete_auth), 2000)


def handle_stealth_mode() -> None:
    """Enable stealth/anonymous mode."""
    STEALTH_BTN.disabled = True
    STEALTH_BTN.innerHTML = 'INITIALIZING STEALTH<span class="loading-dots"></span>'

    print("Entering stealth mode")

    def complete_stealth() -> None:
        global auth_data  # noqa: PLW0603

        # save stealth mode
        auth_data = {"mode": "stealth"}

        STEALTH_BTN.innerHTML = "STEALTH ACTIVE ✓"
        STEALTH_BTN.style.background = "#444400"

        def finish_stealth() -> None:
            hide_modal()
            on_auth_complete(auth_data)

        set_timeout(create_proxy(finish_stealth), 1000)

    set_timeout(create_proxy(complete_stealth), 1500)


def show_input_error() -> None:
    """Show visual error on empty fields."""
    for input_field in [USERNAME_INPUT, PASSWORD_INPUT]:
        if not input_field.value.strip():
            input_field.style.borderColor = "#ff0000"
            input_field.style.boxShadow = "inset 0 0 10px rgba(255, 0, 0, 0.3)"

            def reset_field_style(field: Element = input_field) -> None:
                field.style.borderColor = "#00ff00"
                field.style.boxShadow = ""

            set_timeout(create_proxy(reset_field_style), 1000)


def on_auth_complete(auth_result: dict) -> None:
    """Complete authentication and show interface."""
    print(f"Authentication completed: {auth_result}")

    # update global JavaScript state
    if hasattr(window, "AppState"):
        window.AppState.authData = auth_result
        window.AppState.isAuthenticated = auth_result["mode"] == "authenticated"

    # show main interface
    main_interface = document.querySelector(".interface")
    if main_interface:
        main_interface.style.transition = "opacity 0.5s ease"
        main_interface.style.opacity = "1"

    # update the frontend if it is available
    if frontend is not None:
        mode = "authenticated user" if auth_result["mode"] == "authenticated" else "stealth mode"
        frontend.update_status(f"Connected as {mode}", "success")
        frontend.update_connection_info(0, mode)
        frontend.trigger_electric_wave()
    else:
        print("Frontend module not available yet")


# functions to use in other modules


def get_auth_data() -> dict | None:
    """Get all authentication data."""
    return auth_data


def is_authenticated() -> bool:
    """Verify if the user is authenticated."""
    return auth_data is not None and auth_data.get("mode") == "authenticated"


def get_username() -> str | None:
    """Get username of authenticated user."""
    if is_authenticated():
        return auth_data.get("username")
    return None


def get_password() -> str | None:
    """Get password of authenticated user."""
    if is_authenticated():
        return auth_data.get("password")
    return None


def get_auth_mode() -> str:
    """Get mode: 'authenticated', 'stealth', 'none'."""
    if auth_data:
        return auth_data.get("mode", "none")
    return "none"


def is_stealth_mode() -> bool:
    """Verify if it is in stealth mode."""
    return auth_data is not None and auth_data.get("mode") == "stealth"


def show_auth_modal_after_boot() -> None:
    """Show modal after boot sequence."""
    print("Initializing authentication modal...")
    init_auth_modal()

    def delayed_show() -> None:
        show_modal()

    set_timeout(create_proxy(delayed_show), 200)


print("Auth modal module loaded")
