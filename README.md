# clinvar-civic-sql-database

Python parsers that load [ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/) and [CIViC](https://civicdb.org) data into SQLite databases, plus a set of SQL queries to explore them.

Final project of the SQL module (Master's programme), developed together with [sandra-pinel](https://github.com/sandra-pinel). The project report is in [docs/report.pdf](docs/report.pdf).

## Repository structure

| Folder | Content |
|---|---|
| `civic/scripts/` | Parser that builds the CIViC SQLite database |
| `civic/querys/` | SQL queries on the CIViC database |
| `clinvar/scripts/` | Parser that builds the ClinVar SQLite database, plus scripts for statistics and article data |
| `clinvar/querys/` | SQL queries on the ClinVar database |
| `docs/` | Project report (PDF) |

## Requirements

- Python 3
- SQLite >= 3.37.0 (the scripts check this, because they use `STRICT` tables)

The raw input files and the generated databases are not included in this repository.

## Project goal

The assignment consisted of three loading programs, using the course's example `clinvar_parser.py` as inspiration:

1. Load the scientific articles linked to ClinVar variants.
2. Load ClinVar variant statistics per gene.
3. Load CIViC variant data into a database similar to the ClinVar one.

SQL queries were then written on both databases. The ClinVar parser is based on the example parser provided in the course.

## Input data (December 2025)

| Source | File | URL |
|---|---|---|
| ClinVar | `variant_summary_2025-12.txt.gz` | https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/archive/variant_summary_2025-12.txt.gz |
| ClinVar | `gene_specific_summary_2025-12.txt.gz` | https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/archive/gene_specific_summary_2025-12.txt.gz |
| ClinVar | `var_citations.txt` | https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/var_citations.txt |
| CIViC | `01-Dec-2025-VariantSummaries.tsv` | https://civicdb.org/downloads/01-Dec-2025/01-Dec-2025-VariantSummaries.tsv |
| CIViC | `01-Dec-2025-ClinicalEvidenceSummaries.tsv` | https://civicdb.org/downloads/01-Dec-2025/01-Dec-2025-ClinicalEvidenceSummaries.tsv |
| CIViC | `01-Dec-2025-MolecularProfileSummaries.tsv` | https://civicdb.org/downloads/01-Dec-2025/01-Dec-2025-MolecularProfileSummaries.tsv |

## Usage

Build the ClinVar variant database:

    python3 clinvar/scripts/clinvar_parser_fixed.py clinvar.db variant_summary_2025-12.txt.gz

Build the CIViC database:

    python3 civic/scripts/civic_parser.py civic.db 01-Dec-2025-VariantSummaries.tsv 01-Dec-2025-ClinicalEvidenceSummaries.tsv 01-Dec-2025-MolecularProfileSummaries.tsv

The queries in the `querys/` folders can then be run on the resulting databases, for example:

    sqlite3 civic.db < civic/querys/1.query_civic.sql

## Additional ClinVar loaders

Load the ClinVar gene-level statistics into the ClinVar database:

    python3 clinvar/scripts/clinvar_stats.py clinvar.db gene_specific_summary_2025-12.txt.gz

Load the ClinVar article citations into the ClinVar database (this loader expects a gzip-compressed file, so compress `var_citations.txt` first):

    gzip -k var_citations.txt
    python3 clinvar/scripts/clinvar_articles.py clinvar.db var_citations.txt.gz
