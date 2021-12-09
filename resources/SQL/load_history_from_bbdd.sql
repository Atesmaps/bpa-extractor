INSERT INTO bpa_history (created_at, zone_name, zone_id, danger_level, bpa_date)
SELECT DISTINCT
	TIMESTAMP '2021-01-01 00:00:00',
	zona,
	codi_zona,
	perill,
	date_time::date
FROM
	bpa_bbdd
WHERE
	perill IS NOT NULL
