# Release Notes

## v1.0.0 - 2026-08-06

This release prepares ThesisMate for public publication and self-hosted reuse.

### Highlights

- removed hardcoded API credentials and personal branding
- moved configuration to environment variables with a checked-in `.env.example`
- moved runtime data to ignored local storage under `data/`
- replaced unsafe history parsing with JSON Lines storage
- trimmed dependencies to the packages the app actually uses
- refreshed project documentation for clean public setup
- added an MIT license and generic CI workflow

### Security and Privacy

- deleted tracked user uploads, cached chat history, and generated evaluation files
- removed local machine paths and personal references from source and docs
- stopped committing runtime-generated content by default via `.gitignore`

### Operational Notes

- set `PERPLEXITY_API_KEY` before running the app
- the app now supports `.pdf`, `.txt`, and `.docx` uploads
- URL analysis works by pasting a full `http://` or `https://` link into the prompt field
