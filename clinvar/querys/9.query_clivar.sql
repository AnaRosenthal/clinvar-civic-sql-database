-- Consulta 9 CliVar

SELECT DISTINCT a.citation_id AS pubmed_id
FROM article a
JOIN variant_article va ON va.article_id = a.article_id
WHERE a.citation_source = 'PubMed'
  AND va.ventry_id IN (
      SELECT v.ventry_id
      FROM variant v
      WHERE v.assembly = 'GRCh38'
        AND v.phenotype_list LIKE '%glioblastoma%');