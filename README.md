# Mascarene Paleo Database

**Status:** Active development / preliminary database

Mascarene Paleo is a developing research infrastructure for documenting the palaeontological and subfossil record of the Mascarene Islands, with an initial focus on extinct vertebrates from Mauritius, Rodrigues, Réunion, and associated islands.

This repository is intended to provide a transparent, updateable, and citable record of specimens, taxa, localities, publications, historical sources, digital resources, and unresolved research questions.

## Current version

**v0.1.0 — Initial public working release**

This version should be treated as incomplete. Records may be added, corrected, merged, or reinterpreted as museum catalogues, literature, historical archives, and specimen data are checked.

## Repository contents

- `data/` — working database tables
- `documentation/` — methodology, data dictionary, and contribution guidance
- `sources/` — source register and provenance tracking
- `reports/` — database status and milestone summaries
- `media/` — optional figures, logos, diagrams, and permitted specimen images
- `CHANGELOG.md` — record of updates
- `CITATION.cff` — citation metadata for GitHub/Zenodo
- `LICENSE.md` — licensing information

## Core database tables

The recommended core tables are:

1. `specimens.csv`
2. `taxa.csv`
3. `localities.csv`
4. `publications.csv`
5. `unresolved_questions.csv`


## Scope

The database may include:

- fossil and subfossil vertebrate specimens;
- historical museum collections;
- published and unpublished catalogue records;
- locality records;
- taxonomic identifications and revisions;
- literature references and DOIs;
- available photographs and 3D models;
- unresolved provenance, identification, and collection questions.

## Data quality

Each record should retain enough provenance to determine where the information originated. Where possible, records should include a museum catalogue reference, publication, archive source, catalogue URL, or other traceable source.

Uncertain or unverified information should be explicitly marked rather than silently treated as confirmed.


## Citation

Citation information is provided in `CITATION.cff`. Update the author details, repository URL, DOI, and release date before creating a formal release.

## Contact

Mascarene Paleo  
Research infrastructure/community project for Mascarene palaeontology.

E-mail: mascarenepaleo@gmail.com
Instagram: @mascarenepaleo
LinkedIn: Mascarene Paleo
