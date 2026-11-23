-- Consulta 6 CliVar

SELECT DISTINCT
    v.ventry_id,
    cs.significance,
    v.chro,
    v.chro_start,
    v.chro_stop,
    v.ref_allele,
    v.alt_allele
FROM variant v
JOIN gene2variant gv ON gv.ventry_id = v.ventry_id
JOIN gene g ON g.gene_id = gv.gene_id
JOIN clinical_sig cs ON cs.ventry_id = v.ventry_id
WHERE g.gene_symbol = 'HBB'
  AND v.assembly = 'GRCh37'
  AND cs.significance IN ('Pathogenic', 'Likely pathogenic')
LIMIT 5; # mostrar solo 5 primeras filas de las 471 