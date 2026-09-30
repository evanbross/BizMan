# =============================================================================
# Copyright (c) 2026 ZombieTech LLC. All rights reserved.
#
# LICENSE: Proprietary
# This source code is the confidential and proprietary property of
# ZombieTech LLC. It is provided for authorized development and operation of
# ZombieTech LLC products and services only.
# You may NOT:
#   - Use this code, in whole or in part, outside a ZombieTech LLC product or
#     service without express prior written permission
#   - Sell, sublicense, or otherwise monetize this code or derivatives of it
#     independent of a ZombieTech LLC product or service
#   - Redistribute this code without explicit written permission from
#     ZombieTech LLC
#
# No warranty is provided, express or implied. Use at your own risk.
#
# Licensing inquiries: license@zombietech.biz
# =============================================================================

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# ai: claude-sonnet-5 | 2026-09-12
# Resolved relative to this file (backend/app/core/config.py -> backend/.env), not the process cwd,
# so `.env` is found the same way whether the app is launched from the repo root or from backend/.
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _BACKEND_DIR / ".env"


# ai: claude-sonnet-5 | 2026-09-12
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding="utf-8")

    environment: str = "local"
    log_level: str = "INFO"

    # Single source of truth for both local dev bind ports - the `--port` passed to uvicorn (see
    # AGENTS.md) must match backend_port, and the frontend dev server must bind frontend_port,
    # since core/caddy.py registers both with the local Caddy proxy as one named
    # http://bizman.localhost host (path-split: /api/* -> backend, /* -> frontend). Deliberately
    # not 8000/5173 (FastAPI's/Vite's own defaults) - those are already claimed by other locally
    # running sibling projects (see AGENTS.md "Local Caddy registration").
    backend_port: int = 8610
    frontend_port: int = 8611

    database_url: str
    supabase_url: str
    supabase_service_role_key: str
    supabase_jwt_secret: str


settings = Settings()  # type: ignore[call-arg]
