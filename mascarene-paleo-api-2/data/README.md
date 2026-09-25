# Data snapshot

This directory contains the v0.4 source workbook, the generated SQLite database used by the API, static JSON serializations, summary statistics and a build report.

The workbook is the archival source supplied for this build. The generated files are derived views intended for machine access and web delivery.

- `mascarene_paleo.sqlite` — API database
- `specimens.json`, `taxa.json`, etc. — serialized canonical tables
- `darwin_core_occurrence.json` — Darwin Core occurrence view
- `stats.json` — summary counts
- `build_report.json` — integrity checks and build warnings

The packaged workbook is already cleaned: canonical primary IDs are unique, normalized publication DOIs have no duplicates, and generated API views are direct serializations of the validated source tables.
