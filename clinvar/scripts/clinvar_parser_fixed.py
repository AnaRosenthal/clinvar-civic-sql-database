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

CLINVAR_TABLE_DEFS = [
"""
CREATE TABLE IF NOT EXISTS gene (
    gene_id INTEGER NOT NULL,
    gene_symbol TEXT NOT NULL,
    hgnc_id TEXT,
    PRIMARY KEY (gene_id)
) STRICT
""",
"""
CREATE TABLE IF NOT EXISTS variant (
    ventry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    allele_id INTEGER NOT NULL,
    variation_id INTEGER NOT NULL,
    name TEXT,
    type TEXT NOT NULL,
    dbsnp_id INTEGER,
    phenotype_list TEXT,
    assembly TEXT NOT NULL,
    chro TEXT NOT NULL,
    chro_start INTEGER NOT NULL,
    chro_stop INTEGER NOT NULL,
    ref_allele TEXT,
    alt_allele TEXT,
    cytogenetic TEXT
) STRICT
""",
"""
CREATE INDEX IF NOT EXISTS coords_variant_idx
ON variant(chro, chro_start, chro_stop)
""",
"""
CREATE INDEX IF NOT EXISTS assembly_variant_idx
ON variant(assembly)
""",
"""
CREATE TABLE IF NOT EXISTS gene2variant (
    gene_id INTEGER NOT NULL,
    ventry_id INTEGER NOT NULL,
    PRIMARY KEY (ventry_id, gene_id),
    FOREIGN KEY (gene_id) REFERENCES gene(gene_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (ventry_id) REFERENCES variant(ventry_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) STRICT
""",
"""
CREATE TABLE IF NOT EXISTS clinical_sig (
    ventry_id INTEGER NOT NULL,
    significance TEXT NOT NULL,
    PRIMARY KEY (ventry_id, significance),
    FOREIGN KEY (ventry_id) REFERENCES variant(ventry_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) STRICT
""",
"""
CREATE TABLE IF NOT EXISTS review_status (
    ventry_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    PRIMARY KEY (ventry_id, status),
    FOREIGN KEY (ventry_id) REFERENCES variant(ventry_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) STRICT
""",
"""
CREATE TABLE IF NOT EXISTS variant_phenotypes (
    ventry_id INTEGER NOT NULL,
    phen_group_id INTEGER NOT NULL,
    phen_ns TEXT NOT NULL,
    phen_id TEXT NOT NULL,
    PRIMARY KEY (ventry_id, phen_group_id, phen_ns, phen_id),
    FOREIGN KEY (ventry_id) REFERENCES variant(ventry_id)
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

        for tableDecl in CLINVAR_TABLE_DEFS:
            cur.execute(tableDecl)
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
        headerMapping = None
        newVCFCoords = False

        cur = db.cursor()

        with db:
            for line in cf:
                wline = line.rstrip("\n")

                if not wline:
                    continue

                if (headerMapping is None) and (wline[0] == '#'):
                    wline = wline.lstrip("#")
                    columnNames = re.split(r"\t", wline)

                    headerMapping = {}
                    for columnId, columnName in enumerate(columnNames):
                        headerMapping[columnName] = columnId

                    newVCFCoords = 'PositionVCF' in headerMapping
                    if newVCFCoords:
                        refAlleleCol = headerMapping["ReferenceAlleleVCF"]
                        altAlleleCol = headerMapping["AlternateAlleleVCF"]
                    else:
                        refAlleleCol = headerMapping["ReferenceAllele"]
                        altAlleleCol = headerMapping["AlternateAllele"]
                else:
                    columnValues = re.split(r"\t", wline)

                    for iCol, vCol in enumerate(columnValues):
                        if len(vCol) == 0 or vCol == "-":
                            columnValues[iCol] = None

                    allele_id = int(columnValues[headerMapping["AlleleID"]])
                    name = columnValues[headerMapping["Name"]]
                    allele_type = columnValues[headerMapping["Type"]]
                    dbsnp_id = columnValues[headerMapping["RS# (dbSNP)"]]
                    phenotype_list = columnValues[headerMapping["PhenotypeList"]]
                    assembly = columnValues[headerMapping["Assembly"]]
                    chro = columnValues[headerMapping["Chromosome"]]
                    chro_start = int(columnValues[headerMapping["Start"]])
                    chro_stop = int(columnValues[headerMapping["Stop"]])
                    ref_allele = columnValues[refAlleleCol]
                    alt_allele = columnValues[altAlleleCol]
                    cytogenetic = columnValues[headerMapping["Cytogenetic"]]
                    variation_id = int(columnValues[headerMapping["VariationID"]])

                    gene_val = columnValues[headerMapping["GeneID"]]
                    gene_id = int(gene_val) if gene_val is not None else None
                    gene_symbol = columnValues[headerMapping["GeneSymbol"]]
                    hgnc_id = columnValues[headerMapping["HGNC_ID"]]

                    cur.execute("""
                        INSERT INTO variant(
                            allele_id,
                            variation_id,
                            name,
                            type,
                            dbsnp_id,
                            phenotype_list,
                            assembly,
                            chro,
                            chro_start,
                            chro_stop,
                            ref_allele,
                            alt_allele,
                            cytogenetic)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        allele_id,
                        variation_id,
                        name,
                        allele_type,
                        dbsnp_id,
                        phenotype_list,
                        assembly,
                        chro,
                        chro_start,
                        chro_stop,
                        ref_allele,
                        alt_allele,
                        cytogenetic
                    ))

                    ventry_id = cur.lastrowid

                    if gene_id is not None and gene_id != -1:
                        cur.execute("""
                            INSERT OR IGNORE INTO gene(
                                gene_id,
                                gene_symbol,
                                hgnc_id)
                            VALUES(?,?,?)
                        """, (gene_id, gene_symbol, hgnc_id))

                        cur.execute("""
                            INSERT OR IGNORE INTO gene2variant(
                                gene_id,
                                ventry_id)
                            VALUES(?,?)
                        """, (gene_id, ventry_id))

                    significance = columnValues[headerMapping["ClinicalSignificance"]]
                    if significance is not None:
                        prep_sig = [
                            (ventry_id, sig.strip())
                            for sig in re.split(r"\s*[;/]\s*", significance)
                            if sig.strip()
                        ]

                        cur.executemany("""
                            INSERT OR IGNORE INTO clinical_sig(
                                ventry_id,
                                significance)
                            VALUES(?,?)
                        """, prep_sig)

                    status_str = columnValues[headerMapping["ReviewStatus"]]
                    if status_str is not None:
                        prep_status = [
                            (ventry_id, status.strip())
                            for status in re.split(r",\s*", status_str)
                            if status.strip()
                        ]
                        cur.executemany("""
                            INSERT OR IGNORE INTO review_status(
                                ventry_id,
                                status)
                            VALUES(?,?)
                        """, prep_status)

                    variant_pheno_str = columnValues[headerMapping["PhenotypeIDS"]]
                    if variant_pheno_str is not None:
                        variant_pheno_list = re.split(r"[;|]", variant_pheno_str)
                        prep_pheno = []
                        for phen_group_id, variant_pheno in enumerate(variant_pheno_list):
                            if len(variant_pheno) == 0:
                                continue
                            if re.search(r"^[1-9][0-9]* conditions$", variant_pheno):
                                print(
                                    "INFO: Long PhenotypeIDs {} {}: {}".format(
                                        allele_id, assembly, variant_pheno
                                    ),
                                    file=sys.stderr
                                )
                                continue
                            variant_annots = re.split(r",", variant_pheno)
                            for variant_annot in variant_annots:
                                variant_annot = variant_annot.strip()
                                if not variant_annot or variant_annot == "na":
                                    continue
                                phen = variant_annot.split(":", 1)
                                if len(phen) == 2:
                                    phen_ns, phen_id = phen
                                    prep_pheno.append((ventry_id, phen_group_id, phen_ns, phen_id))
                                else:
                                    print(
                                        "DEBUG: {} {} {}\n\t{}\n\t{}".format(
                                            allele_id, assembly, variant_annot, variant_pheno_str, line
                                        ),
                                        file=sys.stderr
                                    )

                        cur.executemany("""
                            INSERT OR IGNORE INTO variant_phenotypes(
                                ventry_id,
                                phen_group_id,
                                phen_ns,
                                phen_id)
                            VALUES(?,?,?,?)
                        """, prep_pheno)

        cur.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: {0} {{database_file}} {{compressed_clinvar_file}}".format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    db_file = sys.argv[1]
    clinvar_file = sys.argv[2]

    db = open_clinvar_db(db_file)

    try:
        store_clinvar_file(db, clinvar_file)
    finally:
        db.close()
