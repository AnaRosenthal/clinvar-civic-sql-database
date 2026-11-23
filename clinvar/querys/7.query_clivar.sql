-- Consulta 7 CliVar

SELECT COUNT(*) AS num_variantS
FROM variant v
WHERE v.assembly = 'GRCh37'
AND v.chro = '13'
AND v.chro_start >= 10000000
AND v.chro_stop <= 20000000;