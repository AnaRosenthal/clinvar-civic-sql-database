-- Consulta 1 CliVar

SELECT COUNT(*)
FROM variant v
JOIN gene2variant gv ON v.ventry_id = gv.ventry_id
JOIN gene g ON gv.gene_id = g.gene_id
WHERE g.gene_symbol = 'TP53'
AND v.assembly = 'GRCh38';