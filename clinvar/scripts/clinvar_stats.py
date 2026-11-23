#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import sys, os

import sqlite3
try:
    import pysqlite3
    if pysqlite3.sqlite_version_info > sqlite3.sqlite_version_info:
        del sqlite3
        import pysqlite3 as sqlite3
    else:
        del pysqlite3
except:
    pass

if sqlite3.sqlite_version_info < (3, 37, 0):
    raise AssertionError("Este programa necesita una versión de SQLite igual o superior a 3.37.0")

import gzip
import re


STATS_TABLE_DEFS = [
"""
CREATE TABLE IF NOT EXISTS gene_stats (
    gene_id INTEGER NOT NULL,
    total_submissions INTEGER,
    total_alleles INTEGER,
    submissions_reporting_this_gene INTEGER,
    alleles_reported_pathogenic_likely_pathogenic INTEGER,
    gene_mim_number TEXT,
    number_uncertain INTEGER,
    number_with_conflicts INTEGER,
    PRIMARY KEY (gene_id),
    FOREIGN KEY (gene_id) REFERENCES gene(gene_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) STRICT
"""
]


def open_clinvar_db(db_file):
    if not os.path.exists(db_file):
        db = sqlite3.connect(db_file, isolation_level=None)
        cur = db.cursor()
        try:
            cur.execute("PRAGMA journal_mode=WAL")
        except sqlite3.Error as e:
            print("An error occurred: {}".format(str(e)), file=sys.stderr)
        finally:
            cur.close()
            db.close()

    db = sqlite3.connect(db_file)

    cur = db.cursor()
    try:
        cur.execute("PRAGMA synchronous = normal;")
        cur.execute("PRAGMA FOREIGN_KEYS=ON")

        for tableDecl in STATS_TABLE_DEFS:
            cur.execute(tableDecl)

        cur.execute("PRAGMA table_info(gene)")
        gene_columns = [row[1] for row in cur.fetchall()]

        if "gene_mim_number" not in gene_columns:
            cur.execute("ALTER TABLE gene ADD COLUMN gene_mim_number TEXT")

    except sqlite3.Error as e:
        print("An error occurred: {}".format(str(e)), file=sys.stderr)
    finally:
        cur.close()

    return db


def store_clinvar_file(db, clinvar_file):
    if clinvar_file.endswith(".gz"):
        opener = gzip.open
    else:
        opener = open

    with opener(clinvar_file, "rt", encoding="utf-8") as cf:
        cur = db.cursor()

        # Primera línea: overview
        cf.readline()

        # Segunda línea: cabecera real
        header_line = cf.readline().rstrip("\n").lstrip("#")
        columnNames = re.split(r"\t", header_line)
        headerMapping = {columnName: columnId for columnId, columnName in enumerate(columnNames)}

        with db:
            for line in cf:
                wline = line.rstrip("\n")

                if not wline:
                    continue

                columnValues = re.split(r"\t", wline)

                for iCol, vCol in enumerate(columnValues):
                    if len(vCol) == 0 or vCol == "-":
                        columnValues[iCol] = None

                gene_id = int(columnValues[headerMapping["GeneID"]])
                gene_symbol = columnValues[headerMapping["Symbol"]]

                total_submissions = columnValues[headerMapping["Total_submissions"]]
                total_alleles = columnValues[headerMapping["Total_alleles"]]
                submissions_reporting_this_gene = columnValues[headerMapping["Submissions_reporting_this_gene"]]
                alleles_reported_pathogenic_likely_pathogenic = columnValues[headerMapping["Alleles_reported_Pathogenic_Likely_pathogenic"]]
                gene_mim_number = columnValues[headerMapping["Gene_MIM_number"]]
                number_uncertain = columnValues[headerMapping["Number_uncertain"]]
                number_with_conflicts = columnValues[headerMapping["Number_with_conflicts"]]

                total_submissions = int(total_submissions) if total_submissions is not None else None
                total_alleles = int(total_alleles) if total_alleles is not None else None
                submissions_reporting_this_gene = int(submissions_reporting_this_gene) if submissions_reporting_this_gene is not None else None
                alleles_reported_pathogenic_likely_pathogenic = (
                    int(alleles_reported_pathogenic_likely_pathogenic)
                    if alleles_reported_pathogenic_likely_pathogenic is not None else None
                )
                number_uncertain = int(number_uncertain) if number_uncertain is not None else None
                number_with_conflicts = int(number_with_conflicts) if number_with_conflicts is not None else None

                # Asegurar que el gen existe en gene
                cur.execute("""
                    INSERT OR IGNORE INTO gene(
                        gene_id,
                        gene_symbol,
                        hgnc_id,
                        gene_mim_number
                    )
                    VALUES(?,?,?,?)
                """, (
                    gene_id,
                    gene_symbol,
                    None,
                    gene_mim_number
                ))

                # Completar gene_mim_number si faltaba
                cur.execute("""
                    UPDATE gene
                    SET gene_symbol = COALESCE(gene_symbol, ?),
                        gene_mim_number = COALESCE(gene_mim_number, ?)
                    WHERE gene_id = ?
                """, (
                    gene_symbol,
                    gene_mim_number,
                    gene_id
                ))

                # Insertar/actualizar estadísticas
                cur.execute("""
                    INSERT OR REPLACE INTO gene_stats(
                        gene_id,
                        total_submissions,
                        total_alleles,
                        submissions_reporting_this_gene,
                        alleles_reported_pathogenic_likely_pathogenic,
                        gene_mim_number,
                        number_uncertain,
                        number_with_conflicts
                    )
                    VALUES(?,?,?,?,?,?,?,?)
                """, (
                    gene_id,
                    total_submissions,
                    total_alleles,
                    submissions_reporting_this_gene,
                    alleles_reported_pathogenic_likely_pathogenic,
                    gene_mim_number,
                    number_uncertain,
                    number_with_conflicts
                ))

        cur.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: {0} {{database_file}} {{gene_specific_summary_file}}".format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    db_file = sys.argv[1]
    clinvar_file = sys.argv[2]

    db = open_clinvar_db(db_file)

    try:
        store_clinvar_file(db, clinvar_file)
    finally:
        db.close()