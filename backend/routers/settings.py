"""
Router — GET/POST /api/settings
"""
from fastapi import APIRouter

from config import settings
from models.schemas import SettingsRead, SettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsRead)
async def get_settings():
    d = settings.as_dict(mask_token=True)
    return SettingsRead(**d)


@router.post("", response_model=SettingsRead)
async def update_settings(body: SettingsUpdate):
    settings.update(
        llm_base_url=body.llm_base_url,
        llm_token=body.llm_token,
        llm_model=body.llm_model,
    )
    d = settings.as_dict(mask_token=True)
    return SettingsRead(**d)
