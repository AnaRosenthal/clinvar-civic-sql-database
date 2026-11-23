#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-


#Manejar argumentos de entrada #Interactuar con sistema operativo
import sys, os
import sqlite3 #Manejar bases de datos SQLite3 en python
import re


#Fuerza que el script se ejecute solo si SQLite es al menos la versión 3.37.0. 
#Si no, detiene el programa y avisa al usuario.
if sqlite3.sqlite_version_info < (3, 37, 0):
    raise AssertionError("Se necesita SQLite >= 3.37.0")



CIVIC_TABLE_DEFS = [

"""
CREATE TABLE IF NOT EXISTS variant (
    variant_id INTEGER PRIMARY KEY,
    gene TEXT,
    entrez_id INTEGER,
    chromosome TEXT,
    start INTEGER,
    stop INTEGER,
    reference_bases TEXT,
    variant_bases TEXT,
    variant_types TEXT,
    reference_build TEXT,
    molecular_profile_id INTEGER
) STRICT
""",

"""
CREATE INDEX IF NOT EXISTS coords_variant ON variant(chromosome, start, stop)
""",

"""
CREATE INDEX IF NOT EXISTS gene_variant ON variant(gene)
""",

"""
CREATE INDEX IF NOT EXISTS build_variant ON variant(reference_build)
""",

"""
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id INTEGER PRIMARY KEY,
    molecular_profile_id INTEGER,
    disease TEXT,
    evidence_type TEXT,
    evidence_level TEXT,
    significance TEXT
) STRICT
""",

"""
CREATE TABLE IF NOT EXISTS variant_evidence (
    variant_id INTEGER,
    evidence_id INTEGER,
    PRIMARY KEY (variant_id, evidence_id)
) STRICT
""",

"""
CREATE TABLE IF NOT EXISTS molecular_profile (
    molecular_profile_id INTEGER PRIMARY KEY,
    name TEXT,
    summary TEXT
) STRICT
"""
]





def open_civic_db(db_file):
    """
        Abre una base de datos SQLite para CIViC
        
        Si el archivo no existe, lo crea e inicializa en modo WAL
        Configura PRAGMA para rendimiento e integridad
        Crea las tablas definidas en CIVIC_TABLE_DEFS si no existen
        
        Devuelve la conexión abierta a la base de datos
    """

    if not os.path.exists(db_file):
        db = sqlite3.connect(db_file, isolation_level=None)
        cur = db.cursor()
        try:
            cur.execute("PRAGMA journal_mode=WAL")
        except sqlite3.Error as e:
            print(f"Error: {e}", file=sys.stderr)
        finally:
            cur.close()
            db.close()

    db = sqlite3.connect(db_file)

    cur = db.cursor()
    try:
        cur.execute("PRAGMA synchronous = normal;")
        cur.execute("PRAGMA FOREIGN_KEYS=ON")

        for tableDecl in CIVIC_TABLE_DEFS:
            cur.execute(tableDecl)

    except sqlite3.Error as e:
        print(f"Error: {e}", file=sys.stderr)
    finally:
        cur.close()
    return db





def store_variant_file(db, variant_file):

    headerMapping = None
    cur = db.cursor()

    with db:
        with open(variant_file, "rt", encoding="utf-8") as vf:
            for line in vf:
                wline = line.rstrip("\n")

                if headerMapping is None:
                    columnNames = re.split(r"\t", wline)
                    headerMapping = {}

                    for i, col in enumerate(columnNames):
                        headerMapping[col] = i
                else:
                    columnValues = re.split(r"\t", wline)

                    for i, v in enumerate(columnValues):
                        if len(v) == 0 or v == "-":
                            columnValues[i] = None

                    variant_id = int(columnValues[headerMapping["variant_id"]])
                    gene = columnValues[headerMapping["gene"]]
                    entrez_id = int(columnValues[headerMapping["entrez_id"]]) if columnValues[headerMapping["entrez_id"]] is not None else None
                    chromosome = columnValues[headerMapping["chromosome"]]
                    start = int(columnValues[headerMapping["start"]]) if columnValues[headerMapping["start"]] is not None else None
                    stop = int(columnValues[headerMapping["stop"]]) if columnValues[headerMapping["stop"]] is not None else None
                    ref = columnValues[headerMapping["reference_bases"]]
                    alt = columnValues[headerMapping["variant_bases"]]
                    vtype = columnValues[headerMapping["variant_types"]]
                    build = columnValues[headerMapping["reference_build"]]
                    mp_id = int(columnValues[headerMapping["single_variant_molecular_profile_id"]]) if columnValues[headerMapping["single_variant_molecular_profile_id"]] is not None else None

                    cur.execute("""
						INSERT INTO variant VALUES (?,?,?,?,?,?,?,?,?,?,?)
					""", (variant_id, gene, entrez_id, chromosome,
						start, stop, ref, alt, vtype, build, mp_id))

    cur.close()



def store_evidence_file(db, evidence_file):

    headerMapping = None
    cur = db.cursor()

    with db:
        with open(evidence_file, "rt", encoding="utf-8") as ef:
            for line in ef:
                wline = line.rstrip("\n")

                if headerMapping is None:
                    columnNames = re.split(r"\t", wline)
                    headerMapping = {}

                    for i, col in enumerate(columnNames):
                        headerMapping[col] = i
                else:
                    columnValues = re.split(r"\t", wline)

                    for i, v in enumerate(columnValues):
                        if len(v) == 0:
                            columnValues[i] = None

                    evidence_id = int(columnValues[headerMapping["evidence_id"]])
                    mp_id = columnValues[headerMapping["molecular_profile_id"]]
                    disease = columnValues[headerMapping["disease"]]
                    ev_type = columnValues[headerMapping["evidence_type"]]
                    ev_level = columnValues[headerMapping["evidence_level"]]
                    sig = columnValues[headerMapping["significance"]]

                    cur.execute("""
                        INSERT INTO evidence VALUES (?,?,?,?,?,?)
                    """, (evidence_id, mp_id, disease, ev_type, ev_level, sig))

    cur.close()



def store_molecular_profile_file(db, mp_file):

    headerMapping = None
    cur = db.cursor()

    with db:
        with open(mp_file, "rt", encoding="utf-8") as mf:
            for line in mf:
                wline = line.rstrip("\n")

                if headerMapping is None:
                    columnNames = re.split(r"\t", wline)
                    headerMapping = {}

                    for i, col in enumerate(columnNames):
                        headerMapping[col] = i
                else:
                    columnValues = re.split(r"\t", wline)

                    for i, v in enumerate(columnValues):
                        if len(v) == 0:
                            columnValues[i] = None

                    mp_id = int(columnValues[headerMapping["molecular_profile_id"]])
                    name = columnValues[headerMapping["name"]]
                    summary = columnValues[headerMapping["summary"]]

                    cur.execute("""
                        INSERT INTO molecular_profile VALUES (?,?,?)
                    """, (mp_id, name, summary))

    cur.close()
    


def link_variant_evidence(db):
    """
    Conecta variantes con evidencias vía molecular_profile_id
    """

    cur = db.cursor()

    with db:
        cur.execute("""
            INSERT INTO variant_evidence (variant_id, evidence_id)
            SELECT v.variant_id, e.evidence_id
            FROM variant v
            JOIN evidence e
            ON v.molecular_profile_id = e.molecular_profile_id
        """)

    cur.close()




if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: {} <db_file> <variant_file> <evidence_file> <molecular_profile_file>".format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    db_file = sys.argv[1]
    variant_file = sys.argv[2]
    evidence_file = sys.argv[3]
    mp_file = sys.argv[4]

    db = open_civic_db(db_file)

    try:
        store_variant_file(db, variant_file)
        store_evidence_file(db, evidence_file)
        store_molecular_profile_file(db, mp_file)
        link_variant_evidence(db)
    finally:
        db.close()