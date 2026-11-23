-- Consulta 2 CIViC
-- SNP más frecuente. G>A o G>T en GRCh37 en CIViC

SELECT variant_bases, COUNT(*) as n
FROM variant
WHERE reference_build = 'GRCh37'
AND reference_bases = 'G'
AND variant_bases IN ('A','T')
AND LENGTH(reference_bases)=1
AND LENGTH(variant_bases)=1
GROUP BY variant_bases;

-- El SNP más frecuente en GRCh37 en CIViC es guanina por adenina 105 veces
-- G>A → 105 veces
-- G>T → 54 veces