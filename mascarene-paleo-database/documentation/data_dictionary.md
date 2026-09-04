# Data Dictionary

This document defines the meaning of fields used in the Mascarene Paleo Database.

## General conventions

- Blank cell = information not currently recorded.
- `unknown` = explicitly known to be unknown.
- `uncertain` = information exists but its interpretation is uncertain.
- Dates should preferably use ISO format: `YYYY-MM-DD`.
- Boolean fields should preferably use `TRUE` / `FALSE`.
- Multiple values in one field should use a consistent separator, preferably `;`.
- Each major record should have a stable ID that does not change when a taxonomic interpretation changes.

## specimens.csv

**specimen_id** — Internal stable Mascarene Paleo identifier.  
**repository_code** — Museum/institution abbreviation.  
**catalogue_number** — Repository catalogue number exactly as used by the institution.  
**taxon_id** — Link to `taxa.csv`.  
**taxon_name_as_catalogued** — Identification used by the source catalogue.  
**current_taxon_name** — Current working identification used by Mascarene Paleo.  
**locality_id** — Link to `localities.csv`.  
**material / element / side** — Anatomical information.  
**age_or_context** — Geological, archaeological, or subfossil context.  
**collector** — Named collector if known.  
**collection_date** — Date or approximate date of collection.  
**type_status** — Holotype, paratype, referred specimen, etc., where applicable.  
**identification_status** — Working confidence/status of taxonomic identification.  
**verification_status** — Whether the record has been independently checked.  
**source_id** — Link to `sources/source_register.csv`.  
**photo_available / 3d_model_available** — Whether a digital representation is known.  
**notes** — Free-text clarification.

## taxa.csv

Use one row per taxonomic concept used by the project. Preserve historical/synonym information rather than overwriting it.

## localities.csv

Use stable locality IDs even where coordinates remain uncertain. Coordinate precision should be documented.

## publications.csv

Use stable publication IDs. Prefer DOI where available, but retain stable URLs for historical literature and repositories.

## unresolved_questions.csv

Use this table for provenance problems, taxonomic uncertainty, catalogue conflicts, missing repository information, locality ambiguity, and other research questions.

## sources/source_register.csv

Each source should receive a unique `source_id`, allowing the provenance of database records to be traced.
