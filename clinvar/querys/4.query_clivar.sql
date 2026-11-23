-- Consulta 4 CliVar

SELECT
    v.assembly,
    v.ref_allele,
    v.alt_allele,
    COUNT(*) AS total
FROM variant v
WHERE v.type = 'Deletion'
  AND v.phenotype_list LIKE '%breast%'
  AND (
       v.phenotype_list LIKE '%susceptibility%'
    OR v.phenotype_list LIKE '%familial%'
    OR v.phenotype_list LIKE '%inherited%'
    OR v.phenotype_list LIKE '%hereditary%'
  )
  AND v.ref_allele IS NOT NULL
  AND v.alt_allele IS NOT NULL
  AND v.ref_allele != 'na'
  AND v.alt_allele != 'na'
GROUP BY v.assembly, v.ref_allele, v.alt_allele
ORDER BY total DESC
LIMIT 1;
