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

import logging
import sys
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

_APP_NAME = "bizman"

# ai: claude-sonnet-5 | 2026-09-12
# Sibling shared-infra repo (F:\Evan-F\Projects\infra), same pattern used by other local
# projects (e.g. JobHuntAssistant/app.py). Guarded import: this is a dev-convenience only,
# never a hard dependency — the app must run fine with ../infra absent or Caddy stopped.
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "infra"))
try:
    import caddy_registry as _caddy_registry
except ImportError:
    _caddy_registry = None


# ai: claude-sonnet-5 | 2026-09-12
def register_with_caddy() -> None:
    """Best-effort: makes the backend reachable at http://bizman.localhost during local dev.

    settings.port must match the --port passed on the uvicorn command line (see AGENTS.md) —
    nothing here can detect a mismatch automatically, since uvicorn has already bound the
    port before this (lifespan startup) runs.
    """
    if _caddy_registry is None:
        return
    if not _caddy_registry.register(_APP_NAME, settings.port):
        logger.warning(
            "Caddy registration failed - http://%s.localhost will not work; use "
            "http://127.0.0.1:%d directly, or start the infra stack "
            "(cd ../infra && docker-compose up -d).",
            _APP_NAME,
            settings.port,
        )


# ai: claude-sonnet-5 | 2026-09-12
def deregister_from_caddy() -> None:
    if _caddy_registry is not None:
        _caddy_registry.deregister(_APP_NAME)
