-- transform.sql — STAGING → MARTS deskriptif (SQL murni).

-- ===========================================================================
-- 1. METRIK PER VARIAN
-- ===========================================================================
DELETE FROM mart_variant_metrics;
INSERT INTO mart_variant_metrics
SELECT 'retention_1' AS metric, version AS variant, count(*) AS n,
       round(avg(CASE WHEN retention_1 THEN 1.0 ELSE 0 END), 6) AS nilai_rata,
       round(stddev_pop(CASE WHEN retention_1 THEN 1.0 ELSE 0 END), 6) AS nilai_std
FROM stg_cookie_cats GROUP BY version
UNION ALL
SELECT 'retention_7', version, count(*),
       round(avg(CASE WHEN retention_7 THEN 1.0 ELSE 0 END), 6),
       round(stddev_pop(CASE WHEN retention_7 THEN 1.0 ELSE 0 END), 6)
FROM stg_cookie_cats GROUP BY version
UNION ALL
SELECT 'sum_gamerounds', version, count(*),
       round(avg(sum_gamerounds), 4), round(stddev_pop(sum_gamerounds), 4)
FROM stg_cookie_cats GROUP BY version;

-- ===========================================================================
-- 2. SRM (Sample Ratio Mismatch) — proporsi alokasi
-- ===========================================================================
DELETE FROM mart_srm;
INSERT INTO mart_srm
SELECT version AS variant, count(*) AS n,
       round(count(*)::DOUBLE / (SELECT count(*) FROM stg_cookie_cats), 6) AS proporsi,
       0.5 AS expected
FROM stg_cookie_cats GROUP BY version;
