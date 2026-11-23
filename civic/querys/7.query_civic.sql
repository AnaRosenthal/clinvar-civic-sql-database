-- Consulta 7 CIViC
-- Número variantes en GRCh37 en el cromosoma 13
-- entre las coordenadas 10,000,000 y 20,000,000 en CIViC

SELECT COUNT(*)
FROM variant
WHERE reference_build = 'GRCh37'
AND chromosome = '13'
AND start <= 20000000
AND stop >= 10000000;

-- El nº de variantes en GRCh37 en el cromosoma 13 entre las coordenadas 10M y 20M en CIViC es 0
-- Esto puede deberse al limitado número de variantes disponibles en esta base de datos para dicha región