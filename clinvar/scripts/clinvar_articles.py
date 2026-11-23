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

ARTICLES_TABLE_DEFS = [
"""
CREATE TABLE IF NOT EXISTS article (
    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
    citation_source TEXT NOT NULL,
    citation_id TEXT NOT NULL,
    UNIQUE (citation_source, citation_id)
) STRICT
"""
,
"""
CREATE TABLE IF NOT EXISTS variant_article (
    ventry_id INTEGER NOT NULL,
    article_id INTEGER NOT NULL,
    PRIMARY KEY (ventry_id, article_id),
    FOREIGN KEY (ventry_id) REFERENCES variant(ventry_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (article_id) REFERENCES article(article_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) STRICT
"""
,
"""
CREATE INDEX IF NOT EXISTS variant_article_article_idx
ON variant_article(article_id)
"""
,
"""
CREATE INDEX IF NOT EXISTS variation_variant_idx
ON variant(variation_id)
"""
,
"""
CREATE INDEX IF NOT EXISTS allele_variant_idx
ON variant(allele_id)
"""
,
"""
CREATE INDEX IF NOT EXISTS article_source_idx
ON article(citation_source)
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

        for tableDecl in ARTICLES_TABLE_DEFS:
            cur.execute(tableDecl)
    except sqlite3.Error as e:
        print("An error occurred: {}".format(str(e)), file=sys.stderr)
    finally:
        cur.close()

    return db


def store_articles_file(db, clinvar_file):
    if clinvar_file.endswith(".gz"):
        opener = gzip.open
    else:
        opener = open

    with opener(clinvar_file, "rt", encoding="utf-8") as cf:
        headerMapping = None
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

                else:
                    columnValues = re.split(r"\t", wline)

                    for iCol, vCol in enumerate(columnValues):
                        if len(vCol) == 0 or vCol == "-":
                            columnValues[iCol] = None

                    allele_val = columnValues[headerMapping["AlleleID"]]
                    variation_val = columnValues[headerMapping["VariationID"]]

                    allele_id = int(allele_val) if allele_val is not None else None
                    variation_id = int(variation_val) if variation_val is not None else None

                    cit_source = columnValues[headerMapping["citation_source"]]
                    cit_id = columnValues[headerMapping["citation_id"]]

                    if cit_source is None or cit_id is None:
                        continue

                    cur.execute("""
                        INSERT OR IGNORE INTO article(
                            citation_source,
                            citation_id
                        )
                        VALUES(?,?)
                    """, (
                        cit_source,
                        cit_id
                    ))

                    cur.execute("""
                        SELECT article_id
                        FROM article
                        WHERE citation_source = ?
                        AND citation_id = ?
                    """, (cit_source, cit_id))

                    article_id = cur.fetchone()[0]

                    matched_ventry_ids = set()

                    if variation_id is not None:
                        cur.execute("""
                            SELECT ventry_id
                            FROM variant
                            WHERE variation_id = ?
                        """, (variation_id,))
                        matched_ventry_ids.update(row[0] for row in cur.fetchall())

                    if allele_id is not None:
                        cur.execute("""
                            SELECT ventry_id
                            FROM variant
                            WHERE allele_id = ?
                        """, (allele_id,))
                        matched_ventry_ids.update(row[0] for row in cur.fetchall())

                    prep_links = [
                        (ventry_id, article_id)
                        for ventry_id in matched_ventry_ids
                    ]

                    cur.executemany("""
                        INSERT OR IGNORE INTO variant_article(
                            ventry_id,
                            article_id
                        )
                        VALUES(?,?)
                    """, prep_links)

        cur.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: {0} {{database_file}} {{compressed_var_citations_file}}".format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    db_file = sys.argv[1]
    clinvar_file = sys.argv[2]

    db = open_clinvar_db(db_file)

    try:
        store_articles_file(db, clinvar_file)
    finally:
        db.close()