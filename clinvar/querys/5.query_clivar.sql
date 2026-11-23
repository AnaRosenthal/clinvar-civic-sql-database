-- Consulta 5 CliVar

SELECT DISTINCT
    v.ventry_id,
    g.gene_id,
    v.chro,
    v.chro_start,
    v.chro_stop
FROM variant v
JOIN gene2variant gv ON gv.ventry_id = v.ventry_id
JOIN gene g ON g.gene_id = gv.gene_id
WHERE v.assembly = 'GRCh38'
AND v.phenotype_list LIKE '%Acute infantile liver failure due to synthesis defect of mtDNA-encoded proteins%';
