# Changelog

All notable changes to this project will be documented in this file.

---


## \[2.0.0] - 2025-07-17

### Added

* Completely rewritten/revamped
* Complete recipe management (create, edit, delete, view)
* Batch tracking with primary/secondary/bottling dates and notes
* Image uploads and drag-and-drop galleries with reordering and captions
* ABV calculation based on supplied SG
* Estimated calorie calculation per 5 oz. glass
* Full authentication (login, registration, profiles)
* Theme toggle (light/dark) stored in user profile
* Gravatar support for profile picture
* Export options for PDF, JSON, CSV, TXT, and SQL
* Public/private visibility for recipes and batches
* Session-based authentication using cookies
* Centralized CSS for dark/light mode compatibility
* Responsive UI
* Yeast reference table with sorting, filtering, pagination

### Changed

* Moved inline styles to centralized stylesheet
* Separated yeast data logic and template rendering
* Restructured project layout for modularity

### Fixed

* SQL export now returns full data
* PDF exports include dynamic ABV and calorie values
* Fixed image upload preview and batch image sequencing

---

## \[1.0.0] - 2024-12-01

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

### Usage Notes

* Default login credentials and browser prompts added
* TiltPi linking instructions available in the app

---

