# CHANGELOG.md — NBA Player Stat Viewer & Simulator

All notable changes to this project will be documented in this file. This project follows semantic versioning and incremental, AI-guided development. Please update this file after each major change.

---

## [0.4.0] — 2025-05-27
### Added
- Created AI_ENHANCEMENTS.md with comprehensive AI integration plan
- Documented 10+ potential AI features with implementation details
- Added player archetype classification system
- Implemented player similarity finder based on statistical profiles
- Added context-aware commentary generation in simulations

### Changed
- Updated repository remote URL to new GitHub location
- Improved documentation structure and organization
- Enhanced error handling for AI features

### Security
- Added caching strategy for AI-generated content to reduce API costs
- Implemented rate limiting for AI API calls
- Added fallback mechanisms for AI service unavailability

---

## [0.3.0] — 2025-05-26
### Added
- Implemented advanced 1-on-1 basketball simulation with Gemini API integration
- Created basketball_sim.py module for realistic game simulation
- Added player_enhancer.py to derive additional player attributes from existing stats
- Enhanced the simulation UI with player cards and VS styling
- Integrated Google Gemini API for AI-generated play-by-play commentary
- Added game customization options (target score)
- Implemented fatigue system and position-based gameplay adjustments

### Changed
- Updated simulate.html template with modern, responsive design
- Improved AI commentary formatting with HTML structure and styling
- Enhanced player comparison visuals

### Fixed
- Fixed syntax error in basketball_sim.py
- Added proper error handling for API calls

---

## [0.2.0] — 2025-05-20
### Added
- Created basic Flask application structure
- Implemented player data loading from JSON
- Added player profile viewing functionality
- Created player comparison feature
- Added basic simulation page
- Implemented error_test endpoint for SQL injection demonstration
- Added initial styling and responsive design

### Security
- Created config.py for secure API key storage
- Added .gitignore to exclude sensitive information

---

## [0.1.0] — 2025-05-13
### Added
- Created `PRD.md` as the single source of truth for requirements, features, and technology stack.
- Updated `PRD.md` to use a JSON file (`players.json`) for data storage instead of SQLite/SQLAlchemy.
- Created `ROADMAP.md` for incremental development planning and progress tracking.
- Created `RULES.md` to summarize core coding standards, project rules, and persistent context for the AI assistant.
- Updated `RULES.md` to reflect JSON-based data storage, roadmap-driven development, and to align with `PRD.md` and `ROADMAP.md`.

### Notes
- All project documentation and planning files are now in place.
- The next steps will focus on project structure, initial sample data, and Flask app skeleton.

---

<!-- Add new entries above this line as the project evolves. -->