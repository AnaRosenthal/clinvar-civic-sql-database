-- Consulta 2 CliVar

SELECT
    ref_allele,
    alt_allele,
    COUNT(*) AS total_variantes
FROM variant
WHERE assembly = 'GRCh37'
  AND type = 'single nucleotide variant'
  AND ref_allele = 'G'
  AND alt_allele IN ('A', 'T')
GROUP BY ref_allele, alt_allele
ORDER BY total_variantes DESC;