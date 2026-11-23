-- Consulta 8 CliVar

SELECT COUNT(DISTINCT v.ventry_id) AS num_variantes
FROM variant v
JOIN gene2variant gv ON gv.ventry_id = v.ventry_id
JOIN gene g ON g.gene_id = gv.gene_id
JOIN clinical_sig cs ON cs.ventry_id = v.ventry_id
WHERE g.gene_symbol = 'BRCA2'
  AND v.assembly = 'GRCh38'
  AND cs.significance != 'Uncertain significance';
