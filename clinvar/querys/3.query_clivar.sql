-- Consulta 3 CliVar

SELECT
    g.gene_symbol,
    COUNT(DISTINCT v.ventry_id) AS num_variantes
FROM variant v
JOIN gene2variant gv ON gv.ventry_id = v.ventry_id
JOIN gene g ON g.gene_id = gv.gene_id
WHERE v.assembly = 'GRCh37'
  AND v.type IN ('Insertion', 'Deletion', 'Indel')
GROUP BY g.gene_id, g.gene_symbol
ORDER BY num_variantes DESC
LIMIT 3;