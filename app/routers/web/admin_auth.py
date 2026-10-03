import segno
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api.admin_auth import (
    require_admin_web,
    verify_admin_csrf,
)
from app.config import settings
from app.core.ui_language import resolve_ui_language
from app.services.admin_auth_service import (
    AdminAuthService,
    TOTP_CHALLENGE_MAX_AGE,
    TOTP_ENROLLMENT_MAX_AGE,
)
from app.services.setup_service import SetupService


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)

admin_auth_service = AdminAuthService()
setup_service = SetupService()

SESSION_COOKIE = "garminsupla_admin_session"
CSRF_COOKIE = "garminsupla_csrf"
TOTP_CHALLENGE_COOKIE = "garminsupla_totp_challenge"
TOTP_ENROLLMENT_COOKIE = "garminsupla_totp_enrollment"

SESSION_MAX_AGE = 8 * 60 * 60


def _resolve_login_language(
    request: Request,
) -> str:
    """Resolve dashboard language for authentication pages."""

    current = setup_service.load_settings()

    return resolve_ui_language(
        request,
        current.ui.language,
    )


def _resolve_ui_theme() -> str:
    """Return the saved dashboard theme for authentication pages."""

    current = setup_service.load_settings()

    return current.ui.theme


def _login_title(
    language: str,
) -> str:
    return (
        "Logowanie"
        if language == "pl"
        else "Login"
    )


def _render_login(
    request: Request,
    language: str,
    *,
    error: str | None = None,
    status_code: int = 200,
):
    """Render administrator password login page."""

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "title": _login_title(
                language
            ),
            "version": settings.app_version,
            "language": language,
            "ui_theme": _resolve_ui_theme(),
            "error": error,
        },
        status_code=status_code,
    )


def _render_totp_login(
    request: Request,
    language: str,
    *,
    recovery_available: bool = False,
    recovery_mode: bool = False,
    error: str | None = None,
    status_code: int = 200,
):
    """Render administrator second-factor verification page."""

    page_title = (
        "Weryfikacja dwuetapowa"
        if language == "pl"
        else "Two-factor authentication"
    )

    return templates.TemplateResponse(
        request=request,
        name="login_totp.html",
        context={
            "title": page_title,
            "version": settings.app_version,
            "language": language,
            "ui_theme": _resolve_ui_theme(),
            "recovery_available":
                recovery_available,
            "recovery_mode":
                recovery_mode,
            "error": error,
        },
        status_code=status_code,
    )


def _create_totp_qr_data_uri(
    provisioning_uri: str,
) -> str:
    """Create a local SVG QR code for TOTP enrollment."""

    if (
        not isinstance(provisioning_uri, str)
        or not provisioning_uri
    ):
        raise ValueError(
            "TOTP provisioning URI must not be empty."
        )

    qr = segno.make_qr(
        provisioning_uri
    )

    return qr.svg_data_uri(
        scale=5,
    )


def _render_two_factor_settings(
    request: Request,
    language: str,
    *,
    totp_enabled: bool,
    provisioning_uri: str | None = None,
    enrollment_pending: bool = False,
    recovery_codes: list[str] | None = None,
    totp_disabled: bool = False,
    error: str | None = None,
    status_code: int = 200,
):
    """Render administrator two-factor settings page."""

    page_title = (
        "Uwierzytelnianie dwuskładnikowe"
        if language == "pl"
        else "Two-factor authentication"
    )

    csrf_token = request.cookies.get(
        CSRF_COOKIE
    )

    qr_data_uri = None

    if provisioning_uri is not None:
        enrollment_pending = True

        qr_data_uri = (
            _create_totp_qr_data_uri(
                provisioning_uri
            )
        )

    response = templates.TemplateResponse(
        request=request,
        name="security_2fa.html",
        context={
            "title": page_title,
            "version": settings.app_version,
            "language": language,
            "ui_theme": _resolve_ui_theme(),
            "csrf_token": csrf_token,
            "totp_enabled": totp_enabled,
            "totp_disabled": totp_disabled,
            "provisioning_uri": provisioning_uri,
            "qr_data_uri": qr_data_uri,
            "enrollment_pending":
                enrollment_pending,
            "recovery_codes": recovery_codes,
            "error": error,
        },
        status_code=status_code,
    )

    if (
        enrollment_pending
        or recovery_codes is not None
        or totp_disabled
    ):
        response.headers["Cache-Control"] = (
            "no-store, max-age=0"
        )

        response.headers["Pragma"] = "no-cache"

    return response


def _create_authenticated_response(
    session: str,
) -> RedirectResponse:
    """Create authenticated dashboard response and cookies."""

    csrf_token = (
        admin_auth_service.create_csrf_token(
            session
        )
    )

    response = RedirectResponse(
        url="/dashboard",
        status_code=303,
    )

    response.set_cookie(
        key=SESSION_COOKIE,
        value=session,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
        path="/",
    )

    response.set_cookie(
        key=CSRF_COOKIE,
        value=csrf_token,
        httponly=False,
        secure=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
        path="/",
    )

    response.delete_cookie(
        key=TOTP_CHALLENGE_COOKIE,
        path="/login/totp",
        secure=True,
        httponly=True,
        samesite="lax",
    )

    return response


@router.get(
    "/login",
    response_class=HTMLResponse,
)
async def login_page(
    request: Request,
):
    """Display administrator login page."""

    language = _resolve_login_language(
        request
    )

    response = _render_login(
        request,
        language,
    )

    response.delete_cookie(
        key=TOTP_CHALLENGE_COOKIE,
        path="/login/totp",
        secure=True,
        httponly=True,
        samesite="lax",
    )

    return response


@router.post(
    "/login",
    response_class=HTMLResponse,
)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """Authenticate administrator password."""

    language = _resolve_login_language(
        request
    )

    admin = (
        admin_auth_service.verify_credentials(
            username,
            password,
        )
    )

    if admin is None:
        error = (
            "Nieprawidłowa nazwa użytkownika lub hasło."
            if language == "pl"
            else "Invalid username or password."
        )

        return _render_login(
            request,
            language,
            error=error,
            status_code=401,
        )

    if admin.totp_enabled:
        try:
            challenge = (
                admin_auth_service.create_totp_challenge(
                    admin
                )
            )

        except ValueError:
            error = (
                "Nie można rozpocząć weryfikacji dwuetapowej."
                if language == "pl"
                else "Unable to start two-factor authentication."
            )

            return _render_login(
                request,
                language,
                error=error,
                status_code=401,
            )

        response = RedirectResponse(
            url="/login/totp",
            status_code=303,
        )

        response.set_cookie(
            key=TOTP_CHALLENGE_COOKIE,
            value=challenge,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=TOTP_CHALLENGE_MAX_AGE,
            path="/login/totp",
        )

        response.delete_cookie(
            key=SESSION_COOKIE,
            path="/",
        )

        response.delete_cookie(
            key=CSRF_COOKIE,
            path="/",
        )

        return response

    try:
        session = (
            admin_auth_service.create_session(
                admin
            )
        )

    except ValueError:
        error = (
            "Stan uwierzytelniania uległ zmianie. Zaloguj się ponownie."
            if language == "pl"
            else "Authentication state changed. Please sign in again."
        )

        return _render_login(
            request,
            language,
            error=error,
            status_code=401,
        )

    return _create_authenticated_response(
        session
    )


@router.get(
    "/login/totp",
    response_class=HTMLResponse,
)
async def login_totp_page(
    request: Request,
):
    """Display TOTP verification page."""

    language = _resolve_login_language(
        request
    )

    challenge = request.cookies.get(
        TOTP_CHALLENGE_COOKIE
    )

    if not challenge:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    admin = (
        admin_auth_service.verify_totp_challenge(
            challenge
        )
    )

    if admin is None:
        response = RedirectResponse(
            url="/login",
            status_code=303,
        )

        response.delete_cookie(
            key=TOTP_CHALLENGE_COOKIE,
            path="/login/totp",
            secure=True,
            httponly=True,
            samesite="lax",
        )

        return response

    return _render_totp_login(
        request,
        language,
        recovery_available=bool(
            admin.recovery_code_hashes
        ),
    )


@router.post(
    "/login/totp",
    response_class=HTMLResponse,
)
async def login_totp(
    request: Request,
    code: str = Form(...),
):
    """Verify administrator TOTP code."""

    language = _resolve_login_language(
        request
    )

    challenge = request.cookies.get(
        TOTP_CHALLENGE_COOKIE
    )

    if not challenge:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    admin = (
        admin_auth_service.verify_totp_challenge(
            challenge
        )
    )

    if admin is None:
        response = RedirectResponse(
            url="/login",
            status_code=303,
        )

        response.delete_cookie(
            key=TOTP_CHALLENGE_COOKIE,
            path="/login/totp",
            secure=True,
            httponly=True,
            samesite="lax",
        )

        return response

    normalized_code = code.strip()

    try:
        session = (
            admin_auth_service.create_session(
                admin,
                totp_code=normalized_code,
            )
        )

    except ValueError:
        error = (
            "Nieprawidłowy lub wykorzystany kod uwierzytelniający."
            if language == "pl"
            else "Invalid or already used authentication code."
        )

        return _render_totp_login(
            request,
            language,
            recovery_available=bool(
                admin.recovery_code_hashes
            ),
            error=error,
            status_code=401,
        )

    return _create_authenticated_response(
        session
    )


@router.post(
    "/login/totp/recovery",
    response_class=HTMLResponse,
)
async def login_recovery_code(
    request: Request,
    recovery_code: str = Form(...),
):
    """Verify a one-time administrator recovery code."""

    language = _resolve_login_language(
        request
    )

    challenge = request.cookies.get(
        TOTP_CHALLENGE_COOKIE
    )

    if not challenge:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    admin = (
        admin_auth_service.verify_totp_challenge(
            challenge
        )
    )

    if admin is None:
        response = RedirectResponse(
            url="/login",
            status_code=303,
        )

        response.delete_cookie(
            key=TOTP_CHALLENGE_COOKIE,
            path="/login/totp",
            secure=True,
            httponly=True,
            samesite="lax",
        )

        return response

    normalized_recovery_code = (
        recovery_code.strip()
    )

    try:
        session = (
            admin_auth_service.create_session(
                admin,
                recovery_code=(
                    normalized_recovery_code
                ),
            )
        )

    except ValueError:
        error = (
            "Nieprawidłowy lub wykorzystany kod odzyskiwania."
            if language == "pl"
            else
            "Invalid or already used recovery code."
        )

        return _render_totp_login(
            request,
            language,
            recovery_available=bool(
                admin.recovery_code_hashes
            ),
            recovery_mode=True,
            error=error,
            status_code=401,
        )

    return _create_authenticated_response(
        session
    )


@router.get(
    "/security/2fa",
    response_class=HTMLResponse,
)
async def two_factor_settings(
    request: Request,
):
    """Display administrator two-factor settings."""

    admin = require_admin_web(
        request
    )

    language = _resolve_login_language(
        request
    )

    return _render_two_factor_settings(
        request,
        language,
        totp_enabled=admin.totp_enabled,
    )


@router.post(
    "/security/2fa/verify-password",
    response_class=HTMLResponse,
)
async def verify_two_factor_password(
    request: Request,
    password: str = Form(...),
    csrf_token: str = Form(...),
):
    """Confirm administrator password and start 2FA enrollment."""

    admin = require_admin_web(
        request
    )

    verify_admin_csrf(
        request,
        csrf_token,
    )

    language = _resolve_login_language(
        request
    )

    if admin.totp_enabled:
        response = _render_two_factor_settings(
            request,
            language,
            totp_enabled=True,
        )

        response.delete_cookie(
            key=TOTP_ENROLLMENT_COOKIE,
            path="/security/2fa",
            secure=True,
            httponly=True,
            samesite="lax",
        )

        return response

    verified_admin = (
        admin_auth_service.verify_credentials(
            admin.username,
            password,
        )
    )

    if verified_admin is None:
        error = (
            "Nieprawidłowe hasło."
            if language == "pl"
            else "Invalid password."
        )

        response = _render_two_factor_settings(
            request,
            language,
            totp_enabled=False,
            error=error,
            status_code=401,
        )

        response.delete_cookie(
            key=TOTP_ENROLLMENT_COOKIE,
            path="/security/2fa",
            secure=True,
            httponly=True,
            samesite="lax",
        )

        return response

    try:
        (
            enrollment_token,
            provisioning_uri,
        ) = admin_auth_service.create_totp_enrollment(
            verified_admin,
            password,
        )

    except ValueError:
        error = (
            "Nie można rozpocząć konfiguracji 2FA. "
            "Odśwież stronę i spróbuj ponownie."
            if language == "pl"
            else
            "Unable to start 2FA setup. "
            "Refresh the page and try again."
        )

        response = _render_two_factor_settings(
            request,
            language,
            totp_enabled=False,
            error=error,
            status_code=409,
        )

        response.delete_cookie(
            key=TOTP_ENROLLMENT_COOKIE,
            path="/security/2fa",
            secure=True,
            httponly=True,
            samesite="lax",
        )

        return response

    response = _render_two_factor_settings(
        request,
        language,
        totp_enabled=False,
        provisioning_uri=provisioning_uri,
    )

    response.set_cookie(
        key=TOTP_ENROLLMENT_COOKIE,
        value=enrollment_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=TOTP_ENROLLMENT_MAX_AGE,
        path="/security/2fa",
    )

    return response


@router.post(
    "/security/2fa/confirm",
    response_class=HTMLResponse,
)
async def confirm_two_factor_enrollment(
    request: Request,
    code: str = Form(...),
    csrf_token: str = Form(...),
):
    """Confirm TOTP enrollment and display recovery codes once."""

    admin = require_admin_web(
        request
    )

    verify_admin_csrf(
        request,
        csrf_token,
    )

    language = _resolve_login_language(
        request
    )

    enrollment_token = request.cookies.get(
        TOTP_ENROLLMENT_COOKIE
    )

    if not enrollment_token:
        response = RedirectResponse(
            url="/security/2fa",
            status_code=303,
        )

        response.delete_cookie(
            key=TOTP_ENROLLMENT_COOKIE,
            path="/security/2fa",
            secure=True,
            httponly=True,
            samesite="lax",
        )

        return response

    normalized_code = code.strip()

    try:
        (
            confirmed_admin,
            recovery_codes,
        ) = admin_auth_service.confirm_totp_enrollment(
            enrollment_token,
            normalized_code,
        )

    except ValueError:
        error = (
            "Nieprawidłowy lub wygasły kod uwierzytelniający. "
            "Spróbuj ponownie. Jeśli konfiguracja wygasła, "
            "rozpocznij ją od początku."
            if language == "pl"
            else
            "Invalid or expired authentication code. "
            "Try again. If the setup has expired, "
            "start the setup again."
        )

        return _render_two_factor_settings(
            request,
            language,
            totp_enabled=False,
            enrollment_pending=True,
            error=error,
            status_code=401,
        )

    response = _render_two_factor_settings(
        request,
        language,
        totp_enabled=confirmed_admin.totp_enabled,
        recovery_codes=recovery_codes,
    )

    # Enabling TOTP rotates session_version, therefore
    # the current administrator session is no longer valid.
    # Remove all authentication and enrollment cookies
    # explicitly before requiring a fresh login.

    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/",
    )

    response.delete_cookie(
        key=CSRF_COOKIE,
        path="/",
    )

    response.delete_cookie(
        key=TOTP_CHALLENGE_COOKIE,
        path="/login/totp",
        secure=True,
        httponly=True,
        samesite="lax",
    )

    response.delete_cookie(
        key=TOTP_ENROLLMENT_COOKIE,
        path="/security/2fa",
        secure=True,
        httponly=True,
        samesite="lax",
    )

    return response


@router.post(
    "/security/2fa/disable",
    response_class=HTMLResponse,
)
async def disable_two_factor(
    request: Request,
    password: str = Form(...),
    csrf_token: str = Form(...),
):
    """Disable administrator two-factor authentication."""

    admin = require_admin_web(
        request
    )

    verify_admin_csrf(
        request,
        csrf_token,
    )

    language = _resolve_login_language(
        request
    )

    try:
        disabled_admin = (
            admin_auth_service.disable_totp(
                admin,
                password,
            )
        )

    except ValueError:
        error = (
            "Nie można wyłączyć 2FA. "
            "Sprawdź hasło i spróbuj ponownie."
            if language == "pl"
            else
            "Unable to disable 2FA. "
            "Check your password and try again."
        )

        return _render_two_factor_settings(
            request,
            language,
            totp_enabled=True,
            error=error,
            status_code=401,
        )

    response = _render_two_factor_settings(
        request,
        language,
        totp_enabled=disabled_admin.totp_enabled,
        totp_disabled=True,
    )

    # Disabling TOTP rotates session_version.
    # Remove all authentication-related cookies so the
    # administrator must authenticate again.

    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/",
    )

    response.delete_cookie(
        key=CSRF_COOKIE,
        path="/",
    )

    response.delete_cookie(
        key=TOTP_CHALLENGE_COOKIE,
        path="/login/totp",
        secure=True,
        httponly=True,
        samesite="lax",
    )

    response.delete_cookie(
        key=TOTP_ENROLLMENT_COOKIE,
        path="/security/2fa",
        secure=True,
        httponly=True,
        samesite="lax",
    )

    return response


@router.post(
    "/logout"
)
async def logout(
    request: Request,
    csrf_token: str = Form(...),
):
    """Destroy administrator session."""

    verify_admin_csrf(
        request,
        csrf_token,
    )

    response = RedirectResponse(
        url="/login",
        status_code=303,
    )

    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/",
    )

    response.delete_cookie(
        key=CSRF_COOKIE,
        path="/",
    )

    response.delete_cookie(
        key=TOTP_CHALLENGE_COOKIE,
        path="/login/totp",
        secure=True,
        httponly=True,
        samesite="lax",
    )

    response.delete_cookie(
        key=TOTP_ENROLLMENT_COOKIE,
        path="/security/2fa",
        secure=True,
        httponly=True,
        samesite="lax",
    )

    return response
