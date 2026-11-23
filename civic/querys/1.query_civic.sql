-- Consulta 1 CIViC
-- Número de variantes en TP53 en GRCh38 en CIViC

SELECT COUNT(*)
FROM variant
WHERE gene = 'TP53'
AND reference_build = 'GRCh38';

-- Hay 0 variantes en TP53 en GRCh38 en CIViC. Ya que CIViC está mayoritariamente en GRCh37
-- Hay 111 variantes en TP53 en GRCh37 en CIViC.