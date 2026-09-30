# AI Agent Instructions — BizMan

## Standards Files — Read These First

At the start of every session, re-read this file and each standards file below before making any changes.

- `../Dev-Standards/COMMON_CODING_STANDARDS.md`
- `../Dev-Standards/PYTHON_STANDARDS.md`
- `../Dev-Standards/DATABASE_STANDARDS.md`
- `../Dev-Standards/FASTAPI_STANDARDS.md`
- `../Dev-Standards/JAVASCRIPT_TYPESCRIPT_STANDARDS.md`
- `../Dev-Standards/REACT_STANDARDS.md`
- `../Dev-Standards/TESTING_STANDARDS.md`

`../Dev-Standards/INFRASTRUCTURE_STANDARDS.md` applies once Docker/CI work starts — deliberately
deferred past Phase 1, see below.

## File Headers

BizMan is a commercial ZombieTech LLC product (multi-tenant SaaS), not personal/non-commercial use.
Every new source file uses the **proprietary** header templates, not the Dev-Standards defaults:

- Python: `../Dev-Standards/Headers/FileHeader_Python_Proprietary.txt`
- JavaScript/TypeScript: `../Dev-Standards/Headers/FileHeader_JS_Proprietary.txt`

---

## Project Overview

Multi-tenant equipment-dealer management platform (initial vertical: Outdoor Power Equipment) —
inventory, sales/invoicing, service work orders, customer management, and reporting. Functional scope
was researched from a competitor's public marketing pages only — see `docs/dealer-ops-blueprint.md`
for the full spec, module catalog, and Phase 1 build scope. No code, text, or design from any
competitor product is to be reused; see that doc's "Legal boundary" section before implementing.

**Stack:** Python/FastAPI backend, React/TypeScript (Vite) frontend, Supabase (managed Postgres +
Auth). Multi-tenant from day one — every table carries `tenant_id`. **All data access goes through
the FastAPI backend**; the frontend never calls Supabase directly for CRUD. Row Level Security is
enabled on every table as a defense-in-depth backstop, but the backend connects with the Supabase
service-role key, so RLS is not the primary enforcement path — see `backend/app/repositories/base.py`
(`TenantScopedRepository`) and `backend/app/core/dependencies.py` for the actual enforcement
mechanism once they exist.

### Repo layout

```
backend/app/          FastAPI app: core/ (config, db, auth, tenant-context deps), models/, schemas/,
                       repositories/ (tenant-scoped data access), services/ (business logic),
                       routers/ (thin, no raw queries)
backend/alembic/       Migrations — the only schema-change tool (not Supabase's own migration CLI)
backend/tests/         pytest; integration/ (real local-Postgres DB), unit/
frontend/src/          React/Vite/TS; api/ (typed client, only place that calls fetch),
                       types/api.d.ts (generated from backend OpenAPI, never hand-duplicated)
supabase/              Supabase CLI local-stack config (`npx supabase start`)
docs/dealer-ops-blueprint.md   Authoritative Phase 1 feature spec
```

### Local dev

All commands below run from the repo root.

- `npx supabase start` — local Postgres + Auth via the Supabase CLI's own Docker stack (required
  because `memberships.user_id` FKs `auth.users`, which only exists on Supabase-provisioned Postgres).
  `npx supabase status` prints the local URL/keys needed for `backend/.env` (copy from
  `backend/.env.example`).
- `uv run alembic upgrade head` — apply migrations.
- `uv run uvicorn app.main:app --reload --app-dir backend --host 0.0.0.0 --port 8610` — backend.
  (`--app-dir backend` makes the `app` package importable; there's no root-level `app` directory.
  `--port 8610` must match `Settings.backend_port` in `core/config.py` — it's what the app
  registers with Caddy. `--host 0.0.0.0`, not `127.0.0.1`: Caddy runs in Docker and reaches host
  processes via `host.docker.internal`, which doesn't arrive on loopback.)
- `npm run dev --prefix frontend -- --port 8611` — frontend, once it exists. `--port 8611` must
  match `Settings.frontend_port` in `core/config.py` (`vite.config.ts` needs
  `server: { host: '0.0.0.0', port: 8611 }`) — `core/caddy.py` registers both ports as one named
  host with a path split; see "Local Caddy registration" below. `host: '0.0.0.0'`, not
  `'127.0.0.1'`, for the same Docker-reachability reason as the backend.
- `uv run pytest` — backend tests. Requires the local Supabase stack running (`npx supabase
  start`) - `backend/tests/conftest.py` auto-creates a sibling `<db>_test` database on that same
  Postgres instance (stubbing just enough of Supabase's `auth` schema for the Membership FK/RLS
  policies), runs `alembic upgrade head` against it, and wraps each test in a transaction that's
  rolled back at teardown - the dev database is never touched. (`pythonpath = ["backend"]` in
  `pyproject.toml` makes `app` importable for tests the same way.)

No Dockerfile/compose/CI yet for BizMan's own services — deliberately deferred until cloud deployment
is actually being scheduled (see the approved Phase 1 plan for reasoning).

### Local Caddy registration

The backend self-registers with the shared local Caddy proxy (`F:\Evan-F\Projects\infra`) on
startup via `backend/app/core/caddy.py`, giving the whole app one name — **http://bizman.localhost**
— instead of a raw port, via a path-based split:

- `http://bizman.localhost/api/*` → backend (`Settings.backend_port`, 8610). Every FastAPI route
  lives under `/api` (see `main.py`) specifically so this split works — a route registered outside
  `/api` would be unreachable through the named host, since only `/api/*` is routed to the backend.
- `http://bizman.localhost/*` (everything else) → frontend dev server (`Settings.frontend_port`,
  8611), once `frontend/` exists.

Both routes are registered together from the backend's own startup (order matters — `/api/*` must
be added before the catch-all, or the catch-all shadows it), matching the pattern used by sibling
local projects (see `../infra/caddy_registry.py`'s `register_route()`). Best-effort only: if
`../infra` isn't checked out or its Caddy container isn't running, the app logs a warning and still
works fine at `http://127.0.0.1:8610` directly. Start the shared stack with
`cd ../infra && docker-compose up -d` if needed.

**Ports are fixed and named, not the frameworks' own defaults** (FastAPI/Uvicorn's 8000, Vite's
5173) — those collide with other locally-running sibling projects on this machine. `backend_port`/
`frontend_port` in `core/config.py` (8610/8611) are the single source of truth; the `--port` flags
on the uvicorn/Vite commands above must match them. Before ever changing these, or picking a port
for a *new* local project, check what's already claimed to avoid a repeat of this: grep sibling
project `.env`/`.env.example`/`docker-compose.yml` files under `F:\Evan-F\Projects` for `PORT=`.

### Key patterns to preserve

- **Tenant isolation is structural, not conventional.** Routers never construct a repository or hold
  a raw DB session directly — they only receive tenant-bound repositories via FastAPI
  `Depends(get_<entity>_repo)`. Every repository requires `tenant_id` in its constructor and filters
  every query through one shared base method. Don't add a code path that queries the DB any other way.
- **Inventory/status changes that can race** (parts `qty_on_hand` decrement, a unit's `status` flip to
  `sold`) are single-statement conditional `UPDATE ... WHERE ... RETURNING`, never SELECT-then-write.
- **Alembic owns all schema changes**, including RLS policy DDL — never use Supabase's own migration
  CLI on this project, to avoid two migration systems drifting apart.
