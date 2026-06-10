# Changelog

All notable changes to this project will be documented in this file.

---

## [2.2.0] - 2026-06-10

### Added

* **Batch email notifications** — Opt-in per-event email reminders for TOSNA nutrient additions (24h/48h/72h), gravity check (~day 4), racking to secondary, and bottling day. Configured per-user on the profile page. Delivered daily at 7am UTC via a management command (`send_batch_notifications`) scheduled by Docker cron.
* **Tasting log** — Record tasting notes per batch with aroma, flavor, overall impressions, and a 1–10 score. Notes appear in reverse-chronological order on the batch detail page with full create/edit/delete support.
* **Cellar tracker** — After bottling, set a bottle count and storage location on any batch. Log consumption events inline to track how many bottles remain. A dedicated `/cellar/` page lists all bottled batches at a glance with a "Last bottle!" warning when only one remains.

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
