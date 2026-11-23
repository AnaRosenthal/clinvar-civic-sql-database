-- Consulta 10 CliVar

SELECT
    chro,
    assembly,
    COUNT(*) AS num_variants
FROM variant
WHERE assembly IN ('GRCh37', 'GRCh38')
  AND chro IN ('1', '22', 'X')
GROUP BY assembly, chro;