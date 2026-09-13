from fastapi import APIRouter, Depends, HTTPException, status

from app.models.api import SetupStatus, GateSummary, SelectGateRequest, WatchStatus

from app.models.settings import (
    SelectedGate,
    WatchItem,
)

from app.services.setup_service import SetupService

from app.api.admin_auth import require_admin_csrf
from app.models.admin import AdminAccount

from app.models.api.pairing import PairingApproveRequest
from app.services.pairing_service import PairingService

from app.models.api.setup import (
    SuplaAvailableItem,
    UILanguageSettings,
    UIThemeSettings,
    WatchApplicationLanguageUpdate,
    WatchItemsUpdateRequest,
    WatchNameUpdate,
)

router = APIRouter(
    prefix="/setup",
    tags=["Setup"],
)

setup_service = SetupService()
pairing_service = PairingService()

@router.get(
    "",
    response_model=SetupStatus,
)

def get_status() -> SetupStatus:
    """Return the current setup status."""

    return setup_service.get_status()


@router.get(
    "/ui/language",
    response_model=UILanguageSettings,
)
def get_ui_language() -> UILanguageSettings:
    """Return the current dashboard language preference."""

    settings = setup_service.load_settings()

    return UILanguageSettings(
        language=settings.ui.language,
    )


@router.get(
    "/ui/theme",
    response_model=UIThemeSettings,
)
def get_ui_theme() -> UIThemeSettings:
    """Return the current dashboard theme preference."""

    settings = setup_service.load_settings()

    return UIThemeSettings(
        theme=settings.ui.theme,
    )


@router.put(
    "/ui/theme",
    response_model=UIThemeSettings,
)
def update_ui_theme(
    request: UIThemeSettings,
    admin: AdminAccount = Depends(
        require_admin_csrf
    ),
) -> UIThemeSettings:
    """Save the dashboard theme preference."""

    theme = setup_service.save_ui_theme(
        request.theme
    )

    return UIThemeSettings(
        theme=theme,
    )


@router.put(
    "/ui/language",
    response_model=UILanguageSettings,
)
def update_ui_language(
    request: UILanguageSettings,
    admin: AdminAccount = Depends(
        require_admin_csrf
    ),
) -> UILanguageSettings:
    """Save the dashboard language preference."""

    language = setup_service.save_ui_language(
        request.language
    )

    return UILanguageSettings(
        language=language,
    )


@router.get(
    "/gates",
    response_model=list[GateSummary],
    responses={
        401: {
            "description": "OAuth authorization expired",
            "content": {
                "application/json": {
                    "example": {
                        "error": "oauth_expired",
                        "message": "Authorization has expired. Please authorize GarminSupla again.",
                    }
                }
            },
        },
        502: {
            "description": "SUPLA API error",
        },
    },
)

def get_available_gates() -> list[GateSummary]:
    """Return available gate channels."""

    return setup_service.get_available_gates()

@router.post(
    "/gate",
    response_model=SelectedGate,
)
def select_gate(
    request: SelectGateRequest,
    admin: AdminAccount = Depends(require_admin_csrf),
) -> SelectedGate:
    """Save the selected gate."""

    return setup_service.save_selected_gate(
        request.channel_id,
    )

@router.get(
    "/watch",
    response_model=WatchStatus,
)
def get_watch_status() -> WatchStatus:
    """Return Garmin watch setup status."""

    return setup_service.get_watch_status()

@router.get(
    "/watches",
    response_model=list[WatchStatus],
)
def get_watch_statuses() -> list[WatchStatus]:
    """Return all configured Garmin watches."""

    return setup_service.get_watch_statuses()


@router.get(
    "/watches/{watch_id}",
    response_model=WatchStatus,
)
def get_watch_status_by_id(
    watch_id: str,
) -> WatchStatus:
    """Return one configured Garmin watch."""

    watch = setup_service.get_watch_status(
        watch_id
    )

    if not watch.configured:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garmin watch not found.",
        )

    return watch

@router.patch(
    "/watches/{watch_id}",
    response_model=WatchStatus,
)
def update_watch_name_by_id(
    watch_id: str,
    request: WatchNameUpdate,
    admin: AdminAccount = Depends(
        require_admin_csrf
    ),
) -> WatchStatus:
    """Update one Garmin watch user-defined name."""

    watch = setup_service.save_watch_name(
        request.name,
        watch_id=watch_id,
    )

    if watch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garmin watch not found.",
        )

    return watch

@router.put(
    "/watches/{watch_id}/language",
    response_model=WatchStatus,
)
def update_watch_application_language_by_id(
    watch_id: str,
    request: WatchApplicationLanguageUpdate,
    admin: AdminAccount = Depends(
        require_admin_csrf
    ),
) -> WatchStatus:
    """Update one Garmin watch application language preference."""

    watch = (
        setup_service.save_watch_application_language(
            request.language,
            watch_id=watch_id,
        )
    )

    if watch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garmin watch not found.",
        )

    return watch

@router.get(
    "/watches/{watch_id}/items",
    response_model=list[WatchItem],
)
def get_watch_items_by_id(
    watch_id: str,
) -> list[WatchItem]:
    """Return one Garmin watch item configuration."""

    items = setup_service.get_watch_items(
        watch_id=watch_id,
    )

    if items is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garmin watch not found.",
        )

    return items


@router.put(
    "/watches/{watch_id}/items",
    response_model=list[WatchItem],
)
def update_watch_items_by_id(
    watch_id: str,
    request: WatchItemsUpdateRequest,
    admin: AdminAccount = Depends(
        require_admin_csrf
    ),
) -> list[WatchItem]:
    """Replace one Garmin watch item configuration."""

    items = [
        WatchItem.model_validate(
            item.model_dump()
        )
        for item in request.items
    ]

    saved_items = setup_service.save_watch_items(
        items,
        watch_id=watch_id,
    )

    if saved_items is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garmin watch not found.",
        )

    return saved_items

@router.post(
    "/watches/{watch_id}/re-pair",
    status_code=status.HTTP_204_NO_CONTENT,
)
def start_watch_repair(
    watch_id: str,
    admin: AdminAccount = Depends(
        require_admin_csrf
    ),
) -> None:
    """Invalidate one Garmin watch token to start re-pairing."""

    started = pairing_service.start_repair(
        watch_id
    )

    if not started:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garmin watch not found.",
        )

@router.delete(
    "/watches/{watch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_watch_by_id(
    watch_id: str,
    admin: AdminAccount = Depends(
        require_admin_csrf
    ),
) -> None:
    """Delete one registered Garmin watch."""

    deleted = setup_service.delete_watch(
        watch_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garmin watch not found.",
        )

@router.patch(
    "/watch",
    response_model=WatchStatus,
)
def update_watch_name(
    request: WatchNameUpdate,
    admin: AdminAccount = Depends(
        require_admin_csrf
    ),
) -> WatchStatus:
    """Update the user-defined Garmin watch name."""

    watch = setup_service.save_watch_name(
        request.name
    )

    if watch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garmin watch is not configured.",
        )

    return watch

@router.get(
    "/watch/items",
    response_model=list[WatchItem],
)
def get_watch_items() -> list[WatchItem]:
    """Return Garmin watch item configuration."""

    return setup_service.get_watch_items()

@router.put(
    "/watch/items",
    response_model=list[WatchItem],
)
def update_watch_items(
    request: WatchItemsUpdateRequest,
    admin: AdminAccount = Depends(
        require_admin_csrf
    ),
) -> list[WatchItem]:
    """Replace Garmin watch item configuration."""

    items = [
        WatchItem.model_validate(
            item.model_dump()
        )
        for item in request.items
    ]

    return setup_service.save_watch_items(
        items
    )

@router.post(
    "/watch/pair",
    status_code=status.HTTP_204_NO_CONTENT,
)
def approve_watch_pairing(
    request: PairingApproveRequest,
    admin: AdminAccount = Depends(
        require_admin_csrf
    ),
) -> None:
    """Approve Garmin watch pairing using its six-digit code."""

    session = pairing_service.approve_pairing(
        request.code,
        watch_id=request.watch_id,
        copy_from_watch_id=(
            request.copy_from_watch_id
        ),
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pairing code not found or expired.",
        )

@router.get(
    "/supla/items",
    response_model=list[SuplaAvailableItem],
)
def get_available_supla_items() -> list[SuplaAvailableItem]:
    """Return currently available executable SUPLA items."""

    return setup_service.get_available_supla_items()
