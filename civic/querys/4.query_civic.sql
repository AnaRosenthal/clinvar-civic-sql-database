-- Consulta 4 CIViC
-- La deleción más común en cáncer hereditario de mama en CIViC
-- Incluir: Genoma de referencia, número de ocurrencias, alelo de referencia y alelo observado


-- Primero vemos variantes en cancer de mama solo
-- SELECT COUNT(DISTINCT v.variant_id) AS total_variants_breast_cancer
-- FROM variant v
-- JOIN variant_evidence ve USING(variant_id)
-- JOIN evidence e USING(evidence_id)
-- WHERE LOWER(e.disease) LIKE '%breast%';

-- 129 variantes en cancer de mama


-- Variantes que son deleciones
-- SELECT COUNT(DISTINCT v.variant_id) AS total_deletion_variants
-- FROM variant v
-- JOIN variant_evidence ve USING(variant_id)
-- JOIN evidence e USING(evidence_id)
-- WHERE LOWER(v.variant_types) LIKE '%deletion%';

-- Hay 27 variantes deleterias


-- Variantes que son hereditarias
-- SELECT COUNT(DISTINCT v.variant_id) AS total_predisposing_variants
-- FROM variant v
-- JOIN variant_evidence ve USING(variant_id)
-- JOIN evidence e USING(evidence_id)
-- WHERE LOWER(e.evidence_type) LIKE '%predisposing%';

-- Hay 339 variantes hereditarias


-- Variantes que son deleciones en cancer de mama
-- SELECT COUNT(DISTINCT v.variant_id) AS total_deletion_variants_breast_cancer
-- FROM variant v
-- JOIN variant_evidence ve USING(variant_id)
-- JOIN evidence e USING(evidence_id)
-- WHERE LOWER(e.disease) LIKE '%breast%'
-- AND LOWER(v.variant_types) LIKE '%deletion%';

-- Hay 1 variante deleteria en cancer de mama
-- Genoma: GRCh37
-- Ocurrencias: 1
-- Alelo ref: TTGAGGGAAAACACA
-- Alelo observado: NULL (deleción)


-- Ahora buscamos si hay alguna variante que sea deleción, cancer de mama y hereditaria
SELECT 
    v.reference_build AS genoma_referencia,
    COUNT(DISTINCT v.variant_id) AS numero_ocurrencias,
    v.reference_bases AS alelo_referencia,
    COALESCE(v.variant_bases, '-') AS alelo_observado
FROM variant v
JOIN variant_evidence ve USING(variant_id)
JOIN evidence e USING(evidence_id)
WHERE LOWER(e.disease) LIKE '%breast%'
  AND LOWER(v.variant_types) LIKE '%deletion%'
  AND LOWER(e.evidence_type) LIKE '%predisposing%'
GROUP BY 
    v.reference_build,
    v.reference_bases,
    v.variant_bases
ORDER BY numero_ocurrencias DESC;

-- No hay ninguna variante que consista en una deleción en cáncer hereditario de mama en CIViC



