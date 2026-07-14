# TaskFlow — System Architecture

## 1. Overview

TaskFlow is a project-management SaaS backend (Jira/Trello-style) built with Django + Django REST Framework + PostgreSQL. Organizations create **Workspaces**, invite **Members** with **Roles**, and manage work through **Projects → Boards → Tasks**.

This document describes how the system is actually structured — not the feature wishlist (see `TaskFlow_Project_Blueprint.md` for that), but how the pieces that exist today fit together, and why.

---

## 2. Tech Stack

| Layer | Technology | Status |
|---|---|---|
| Language | Python 3.14 | In use |
| Framework | Django | In use |
| API layer | Django REST Framework | In use |
| Database | PostgreSQL | In use |
| Auth | JWT (`djangorestframework-simplejwt`) | In use |
| Async / background jobs | Celery + Redis | Planned (v3) |
| File storage | Local disk (dev) → S3/Cloudinary | Decision pending |
| Containerization | Docker + docker-compose | Planned (v3) |
| CI/CD | GitHub Actions | Planned (v3) |
| Deployment | Render / Railway / AWS | Planned (v3) |

---

## 3. App Structure

TaskFlow deliberately uses a **2-app structure**, not one-app-per-model. This was a conscious tradeoff for a solo build on a tight timeline — more apps buy you reusability and team-boundary clarity, which don't matter much here.

```
taskflow_backend/
├── accounts/           # Identity & auth — everything tied to "who is this user"
│   ├── models.py       # CustomUser, Profile
│   ├── signals.py      # post_save -> auto-create Profile
│   ├── apps.py         # wires signals.py into startup via ready()
│   ├── serializers.py  # RegisterSerializer, ProfileSerializer
│   ├── views.py        # Register_api, ProfileAPi
│   └── urls.py
│
├── core/                # Everything else — the actual product domain
│   ├── models.py        # Workspace, WorkspaceMembers, Project, Board (Task/Comment/etc. to come)
│   ├── serializers.py
│   ├── permissions.py   # IsWorkspaceAdminOrOwner
│   ├── views.py
│   └── urls.py
│
└── config/               # settings.py, root urls.py, wsgi/asgi
```

**Why `accounts` is split out from `core`:** `AUTH_USER_MODEL` and everything that touches login/identity benefits from being isolated — it's the one part of the system every other app depends on (`settings.AUTH_USER_MODEL` is referenced from `core.models` repeatedly), so keeping it separate makes that dependency direction obvious.

**Why everything else is one `core` app:** Workspace, Project, Board, and future Task/Comment/Notification models are all tightly coupled to each other (see the ownership chain in §5) — splitting them into separate apps would mean constant cross-app imports for no real benefit at this project's scale.

---

## 4. Data Ownership Chain

Almost every permission and query decision in this system flows from one core hierarchy:

```
Workspace
   │
   ├── WorkspaceMembers (user + role, many per workspace)
   │
   └── Project
          │
          └── Board
                 │
                 └── (Task — not yet built)
                        │
                        └── (Comment / Attachment — not yet built)
```

Everything under a `Workspace` is reachable from it via foreign keys, which is what makes the `__` ORM-chain filtering pattern (§7) work consistently at every level.

---

## 5. Models

### 5.1 `CustomUser` (`accounts`)
Extends `AbstractUser`. Login stays **username-based** (not email) — a deliberate decision made early, before the first migration, since switching after real data exists is a painful manual data migration.

| Field | Note |
|---|---|
| `email` | `unique=True` — enforced even though login is by username |
| `USERNAME_FIELD` | `'username'` |
| `REQUIRED_FIELDS` | `['email']` |

### 5.2 `Profile` (`accounts`)
One-to-one identity data, separate from login credentials. Auto-created via a `post_save` signal the moment a `CustomUser` is created (see §6).

| Field | Type | `on_delete` |
|---|---|---|
| `user` | `OneToOneField(AUTH_USER_MODEL)` | `CASCADE` — profile has no meaning without its user |
| `bio`, `phone_number`, `profile_image` | optional fields | — |

### 5.3 `Workspace` (`core`)
The top-level container — represents a team/company.

| Field | Type | `on_delete` |
|---|---|---|
| `owner` | `ForeignKey(AUTH_USER_MODEL)` | `SET_NULL` + `null=True` — workspace survives even if the owner's account is deleted |
| `name`, `description`, `created_at` | — | — |

### 5.4 `WorkspaceMembers` (`core`)
Join table between `Workspace` and `User`, carrying a `role`. This is the model the entire RBAC system is built on.

| Field | Type | `on_delete` |
|---|---|---|
| `workspace` | `ForeignKey(Workspace, related_name='Members')` | `CASCADE` |
| `user` | `ForeignKey(AUTH_USER_MODEL)` | `CASCADE` |
| `role` | `CharField` with choices: `owner`, `admin`, `manager`, `developer`, `viewer` | — |
| `Meta.unique_together` | `('workspace', 'user')` | prevents duplicate membership rows |

**Business rule enforced in code, not the DB:** only one `role='owner'` allowed per workspace — checked in `WorkSpaceMemberSerializer.validate()`, not a database constraint, because the rule needs to express "at most one row *where role=owner*," which a simple `unique_together` can't do, and application-level logic gives room for better error messaging.

### 5.5 `Project` (`core`)

| Field | Type | `on_delete` |
|---|---|---|
| `workspace` | `ForeignKey(Workspace)` | `CASCADE` — project has no meaning without its workspace |
| `created_by` | `ForeignKey(AUTH_USER_MODEL, related_name='created_projects')` | `SET_NULL` + `null=True` — project survives if its creator leaves |
| `name`, `description`, `created_at` | — | — |

### 5.6 `Board` (`core`)

| Field | Type | `on_delete` |
|---|---|---|
| `project` | `ForeignKey(Project)` | `CASCADE` — board has no meaning without its project |
| `name`, `created_at` | — | — |

---

## 6. Authentication Flow

```
POST /api/accounts/register/
   │
   ▼
RegisterSerializer.create()
   │  -> CustomUser.objects.create_user(...)  (hashes password via set_password())
   ▼
post_save signal fires (created=True)
   │  -> Profile.objects.create(user=instance)
   ▼
Register_api issues JWT immediately
   │  -> RefreshToken.for_user(user)
   ▼
Response: { access_token, refresh_token }
```

Subsequent requests carry `Authorization: Bearer <access_token>`. `TokenRefreshView` (from `simplejwt`) handles issuing a new access token from the refresh token when it expires.

**Why the Profile is created via a signal, not inline in the view:** decouples "a user now exists" from "a profile must exist" — any code path that creates a `CustomUser` (admin panel, management command, future social-auth flow) gets a `Profile` automatically, not just the register endpoint.

---

## 7. Permission System (RBAC)

### 7.1 The core idea
Permissions are attached to a **role on a specific workspace membership**, not to the user globally. The same person can be `owner` in one workspace and `viewer` in another — this is why `role` lives on `WorkspaceMembers`, not on `CustomUser`.

### 7.2 `IsWorkspaceAdminOrOwner`
A single reusable `BasePermission` subclass, applied unchanged across `WorkspaceMemberView`, `ProjectView`, and `BoardView`:

- **Read (`GET`/`HEAD`/`OPTIONS`)** — allowed for any workspace member, any role
- **Write (`POST`/`PUT`/`PATCH`/`DELETE`)** — only allowed if the requesting user has a `WorkspaceMembers` row with `role in ['owner', 'admin']` for the relevant workspace

`has_permission()` covers list/create (no object exists yet — resolves the workspace from the URL or request body). `has_object_permission()` covers retrieve/update/delete on an existing row (resolves the workspace from `obj.workspace` directly).

### 7.3 Known limitation
`IsWorkspaceAdminOrOwner` currently expects a `workspace` field directly in the request/URL. `Board` doesn't naturally carry `workspace` (only `project`) — current workaround is the client sends both `project` and `workspace` on create. **Not yet fixed properly** — the correct fix is resolving `workspace` via `project.workspace` inside the permission class when `workspace` isn't directly present. Flagged as technical debt, not silently ignored.

---

## 8. Query Isolation Pattern (multi-hop ORM filtering)

Every list/detail endpoint scopes data to "things the requesting user actually has access to" using Django's `__` relationship-chain lookups, walking from the model being queried up to `WorkspaceMembers`:

| Model | `get_queryset()` filter |
|---|---|
| `Profile` | `filter(user=self.request.user)` |
| `WorkspaceMembers` | `filter(workspace__Members__user=self.request.user)` |
| `Project` | `filter(workspace__Members__user=self.request.user)` |
| `Board` | `filter(project__workspace__Members__user=self.request.user)` |

Each additional level of nesting adds one more `__` hop — the pattern is mechanical once the ownership chain (§4) is understood: walk the foreign keys up to `Workspace`, then across the `Members` reverse relation, then down to `user`.

**Why this matters architecturally:** without these overrides, `ModelViewSet`'s default `queryset = Model.objects.all()` would leak every user's data to every other authenticated user. This is the single most repeated security-critical pattern in the codebase.

---

## 9. Request Lifecycle (concrete example: creating a Project)

```
Client → POST /api/core/projects/  {workspace: 1, name: "...", description: "..."}
              │
              ▼
   IsAuthenticated check (must have valid JWT)
              │
              ▼
   IsWorkspaceAdminOrOwner.has_permission()
        → looks up WorkspaceMembers row for (workspace=1, user=request.user)
        → role must be 'owner' or 'admin', else 403
              │
              ▼
   ProjectSerializer validates input (created_by excluded — read-only)
              │
              ▼
   ProjectView.perform_create()
        → serializer.save(created_by=request.user)
              │
              ▼
   201 Created — full Project object returned, created_by auto-filled
```

---

## 10. Build Status

| Component | Status |
|---|---|
| Auth (Phase 1) | ✅ Complete, tested end-to-end |
| Workspace (Phase 2) | ✅ Complete |
| WorkspaceMembers + RBAC (Phase 3) | 🔨 ~90% — 403 test not yet re-confirmed |
| Project (Phase 4) | 🔨 Built, self-reported working, not independently verified |
| Board (Phase 5) | 🔨 Built, has a documented permission-class gap (see §7.3) |
| Task, Comment (Phase 6–7 — MVP finish line) | ⬜ Not started |
| Attachments, Notifications, Activity Log, Dashboard, Search (v2) | ⬜ Not started |
| AI features, Redis/Celery, Docker, CI/CD (v3) | ⬜ Not started |

---

## 11. Known Technical Debt

1. **Board's permission-class gap** (§7.3) — client sends `workspace` redundantly instead of the permission class resolving it via `project.workspace`.
2. **`on_delete=PROTECT` vs `SET_NULL` on `Workspace.owner`** — currently `SET_NULL`, meaning a workspace can end up with **no owner** if the owner's account is deleted. No mechanism yet exists to promote a new owner in that scenario — would need to be built before this is production-safe.
3. **Naming inconsistency during early development** (`Workplace`/`Workspace`, `Custom`/`CustomUser`) — resolved in current code, but worth a final grep across the codebase to confirm no stale references remain.
4. **No automated tests yet** — all verification so far has been manual (Postman). Worth adding pytest coverage before Phase 6 (Tasks), since that phase has the most business logic (assignment, status transitions).

---

## 12. Design Principles Followed So Far

- **Never hardcode the User model** — always `settings.AUTH_USER_MODEL`, never a direct import, so the app survives a future model rename.
- **Permissions scoped per-role-per-workspace**, not global roles on the user — required because the same user can hold different roles across different workspaces.
- **`get_queryset()` overridden on every `ModelViewSet`** — default "return everything" is never acceptable for user-owned data.
- **Auto-set fields (`owner`, `created_by`) are always `read_only` in the serializer** and filled server-side in `perform_create()` — never trust the client to supply who they are.
