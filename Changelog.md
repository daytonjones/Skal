# Changelog

All notable changes to this project will be documented in this file.

---

## [2.3.0] - 2026-09-21

### Added

* **Android app** — A native Android companion app (Expo / React Native, in `mobile/`) with recipes, batches (tasting notes, bottle consumption, photos), cellar, pantry, yeast reference, calculators, Bjorn AI chat, and profile/settings. Self-hosted friendly: on first launch it asks for your server address. Light and dark themes mirror the web palette and follow your per-user theme setting.
* **REST API** — New JWT-authenticated `/api/v1/` API used by the mobile app: token login/refresh/logout, registration (subject to admin approval), recipes (including clone), batches, tasting notes, bottle consumption, batch photos, pantry, yeast reference, and Bjorn chat with server-side history and save-recipe.
* **Version check** — Public `GET /api/v1/version/` endpoint. The mobile app compares its version to the server's on launch and shows a dismissible banner when the server is newer. The web and mobile versions are kept in step.
* `is_owner` field on recipe and batch API responses so clients can show Edit/Delete only on your own items.

### Changed

* The app version now lives in one place (`APP_VERSION` in `skal/settings.py`); the footer reads it instead of a hardcoded string.
* Dockerfile no longer runs `collectstatic` at build time (it needs runtime settings); the entrypoint already runs it on start.

### Database

* New migration `ai/0002_chatmessage` (server-side Bjorn chat history). Applied automatically on start by `entrypoint.sh`.

---

## [2.2.0] - 2026-06-10

### Added

* **Batch email notifications** — Opt-in per-event email reminders for TOSNA nutrient additions (24h/48h/72h), gravity check (~day 4), racking to secondary, and bottling day. Configured per-user on the profile page. Delivered daily at 7am UTC via a management command (`send_batch_notifications`) scheduled by Docker cron.
* **Tasting log** — Record tasting notes per batch with aroma, flavor, overall impressions, and a 1–10 score. Notes appear in reverse-chronological order on the batch detail page with full create/edit/delete support.
* **Cellar tracker** — After bottling, set a bottle count and storage location on any batch. Log consumption events inline to track how many bottles remain. A dedicated `/cellar/` page lists all bottled batches at a glance with a "Last bottle!" warning when only one remains.
* **Quick-consume** — Log a bottle directly from the cellar page without navigating away. An inline quantity field and "−" button per row posts and redirects back to `/cellar/`.
* **Consumption delete** — Remove individual consumption entries from the batch detail page with a per-entry "×" button (POST, login-required).
* **ABV display** — Bottled batches now show calculated ABV (alternate formula) instead of FG on the home dashboard, batch list, and cellar view. Active batches continue to show OG → FG.

### Changed

* Batch list page heading corrected from "Your Cellar" to "Your Batches"; cellar page heading updated to "Your Cellar".
* Same-day consumption entries are aggregated in the batch detail history: total quantity on the summary row, individual entries with delete buttons below.
* Cellar view automatically hides batches once `bottles_remaining` reaches zero.
* Bottle count and storage location fields are now visible in the batch edit form under a dedicated "Cellar" section.
* `install.sh` detects ports already in use and auto-suggests the next free one, looping until the user confirms.

---

## [2.1.0] - 2026-06-06

### Added

* **Bjorn AI assistant** — Viking-themed brewing guide powered by Anthropic Claude or OpenAI. Scoped to mead/homebrewing topics only. Accessible via sidebar when `AI_PROVIDER` is configured.
* **AI recipe saving** — Bjorn can suggest structured recipes using tool calling; a save card appears in chat with full ingredient details. One click saves to your recipe list.
* **AI usage tracking** — Per-user token usage recorded to the database; weekly summary emailed to Django admins via `send_ai_report` management command and scheduler service.
* **Batch image slideshow** — Home dashboard replaced static thumbnail strip with a 10-second auto-advancing slideshow of the user's own and public batch photos.
* **TOSNA 3.0 nutrient schedule** — Batch checklist updated to TOSNA 3.0 guidelines with manufacturer-recommended quantities. Added nutrient selector to batch builder.
* **SG/Brix calculator linking** — SG and Brix fields in the calculator now stay in sync; adjusting one updates the other.
* **Pagination** — Recipe and batch lists paginate at 20 per page. Search and stage filters are preserved across page changes.
* **Interactive install script** — `install.sh` walks through all configuration options including AI assistant setup, writes `.env`, builds containers, and reports status.

### Changed

* Removed redundant edit (pencil) buttons from recipe and batch list rows — click any row to navigate to the detail/edit view.
* Fixed N+1 query issues in recipe list, recipe detail, and batch list views (`select_related`, `prefetch_related`).
* Fixed AI system prompt builder using wrong field name (`volume_gallons` → `batch_size`) and incorrect M2M traversal on ingredients.
* Moved module-level imports (logger, PantryItem) out of method bodies.
* HTMX search/filter swaps now use `outerHTML` for correct DOM replacement.

---

## [2.0.0] - 2025-07-17

### Added

* Completely rewritten from FastAPI/SQLite to Django/PostgreSQL
* Complete recipe management (create, edit, delete, view, clone, export)
* Batch tracking with primary/secondary/bottling dates, checklist, and notes
* Image uploads and drag-and-drop galleries with reordering and captions
* ABV calculation using alternate formula; calorie estimation per 5 oz glass
* Full authentication (login, registration, profile, admin approval flow)
* Light/dark theme toggle stored in user profile
* Gravatar support for profile pictures
* Export options: PDF, JSON, CSV, TXT, SQL
* Public/private visibility for recipes and batches
* Ingredient pantry with recipe gap detection
* Yeast reference table with sorting, filtering, pagination
* Responsive UI with mobile support

### Changed

* Moved inline styles to centralized stylesheet with CSS custom properties
* Restructured project layout for modularity (per-app Django apps)

### Fixed

* SQL export returns complete data
* PDF exports include dynamic ABV and calorie values
* Image upload preview and batch image sequencing

---

## [1.0.0] - 2024-12-01

### Added

* FastAPI web app for managing brewing processes
* ABV% calculator and estimated calorie output
* SQLite database for persistent data storage
* SSL support for local secure access
* User creation at first login
* Backup/import commands for database maintenance
* TiltPi integration for gravity tracking (optional)
* Docker and virtual environment support for deployment
* Basic UI with recipe and ABV views

---
