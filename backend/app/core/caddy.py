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
# Pre-2026-09-15 versions of this module registered one whole-host route under this @id -
# deleted (best-effort) on every startup so a stale route from an old build never lingers
# alongside the two below once an app has been re-registered under the new scheme.
_LEGACY_ROUTE_ID = f"app-{_APP_NAME}"
_API_ROUTE_ID = f"app-{_APP_NAME}-api"
_APP_ROUTE_ID = f"app-{_APP_NAME}-app"

# ai: claude-sonnet-5 | 2026-09-12
# Sibling shared-infra repo (F:\Evan-F\Projects\infra), same pattern used by other local
# projects (e.g. JobHuntAssistant/app.py). Guarded import: this is a dev-convenience only,
# never a hard dependency — the app must run fine with ../infra absent or Caddy stopped.
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "infra"))
try:
    import caddy_registry as _caddy_registry
except ImportError:
    _caddy_registry = None


# ai: claude-sonnet-5 | 2026-09-15
def register_with_caddy() -> None:
    """Best-effort: makes the backend and (once it exists) the frontend reachable under one
    name, http://bizman.localhost, via a path-based split - /api/* to the backend
    (settings.backend_port), everything else to the frontend dev server (settings.frontend_port).
    Both ports must match what uvicorn/the frontend dev server actually bind (see AGENTS.md) -
    nothing here can detect a mismatch automatically, since those processes have already bound
    their ports before this (lifespan startup) runs.

    Registration order matters: the /api/* route must be added before the catch-all app route,
    or the catch-all would shadow it. Both are registered here, from the backend's own startup,
    rather than split across two processes racing to register first.
    """
    if _caddy_registry is None:
        return

    _caddy_registry.delete_route(_LEGACY_ROUTE_ID)

    api_route = {
        "@id": _API_ROUTE_ID,
        "match": [{"host": [f"{_APP_NAME}.localhost"], "path": ["/api", "/api/*"]}],
        "handle": [
            {
                "handler": "reverse_proxy",
                "upstreams": [{"dial": f"host.docker.internal:{settings.backend_port}"}],
            }
        ],
    }
    app_route = {
        "@id": _APP_ROUTE_ID,
        "match": [{"host": [f"{_APP_NAME}.localhost"]}],
        "handle": [
            {
                "handler": "reverse_proxy",
                "upstreams": [{"dial": f"host.docker.internal:{settings.frontend_port}"}],
            }
        ],
    }

    api_ok = _caddy_registry.register_route(api_route)
    app_ok = _caddy_registry.register_route(app_route)
    if not (api_ok and app_ok):
        logger.warning(
            "Caddy registration failed - http://%s.localhost will not work; use "
            "http://127.0.0.1:%d directly, or start the infra stack "
            "(cd ../infra && docker-compose up -d).",
            _APP_NAME,
            settings.backend_port,
        )


# ai: claude-sonnet-5 | 2026-09-15
def deregister_from_caddy() -> None:
    if _caddy_registry is not None:
        _caddy_registry.delete_route(_API_ROUTE_ID)
        _caddy_registry.delete_route(_APP_ROUTE_ID)
