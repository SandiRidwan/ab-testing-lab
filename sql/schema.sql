-- schema.sql — Skema database (DuckDB).
-- Lapisan: staging (mentah) → marts (statistik siap-analisis).

-- ===========================================================================
-- STAGING
-- ===========================================================================
CREATE TABLE IF NOT EXISTS stg_cookie_cats (
    userid          BIGINT NOT NULL,
    version         VARCHAR NOT NULL,      -- gate_30 (control) | gate_40 (treatment)
    sum_gamerounds  INTEGER,
    retention_1     BOOLEAN,
    retention_7     BOOLEAN
);

CREATE TABLE IF NOT EXISTS stg_udacity_ab (
    user_id       BIGINT,
    timestamp     TIMESTAMP,
    "group"       VARCHAR,                 -- control | treatment
    landing_page  VARCHAR,
    converted     INTEGER
);

-- ===========================================================================
-- MARTS — deskriptif
-- ===========================================================================

-- Metrik per varian (rata-rata + n) untuk tiap metrik eksperimen
CREATE TABLE IF NOT EXISTS mart_variant_metrics (
    metric       VARCHAR,
    variant      VARCHAR,
    n            INTEGER,
    nilai_rata   DOUBLE,
    nilai_std    DOUBLE,
    PRIMARY KEY (metric, variant)
);

-- Sanity: keseimbangan grup (SRM — Sample Ratio Mismatch)
CREATE TABLE IF NOT EXISTS mart_srm (
    variant       VARCHAR PRIMARY KEY,
    n             INTEGER,
    proporsi      DOUBLE,
    expected      DOUBLE
);

-- ===========================================================================
-- MARTS — hasil uji statistik (diisi oleh src/stats.py)
-- ===========================================================================
CREATE TABLE IF NOT EXISTS mart_test_results (
    metric          VARCHAR,
    kontrol         DOUBLE,
    treatment       DOUBLE,
    abs_lift        DOUBLE,       -- selisih absolut
    rel_lift_pct    DOUBLE,       -- selisih relatif (%)
    ci_low          DOUBLE,       -- batas bawah 95% CI (absolut)
    ci_high         DOUBLE,       -- batas atas 95% CI
    p_value         DOUBLE,
    p_value_adj     DOUBLE,       -- setelah koreksi multiple-testing
    signifikan_raw  BOOLEAN,
    signifikan_adj  BOOLEAN,
    test_used       VARCHAR,      -- uji yang dipakai
    PRIMARY KEY (metric)
);

-- Hasil power analysis
CREATE TABLE IF NOT EXISTS mart_power (
    metric            VARCHAR,
    baseline          DOUBLE,
    mde_rel           DOUBLE,
    n_per_group_req   INTEGER,    -- sampel dibutuhkan per grup
    n_actual_min      INTEGER,    -- sampel aktual (grup terkecil)
    power_achieved    DOUBLE,     -- power yang dicapai dgn n aktual
    cukup             BOOLEAN,
    PRIMARY KEY (metric)
);

-- Heterogeneous treatment effect per segmen (kuartil engagement)
CREATE TABLE IF NOT EXISTS mart_segment_effects (
    metric      VARCHAR,
    segmen      VARCHAR,
    kontrol     DOUBLE,
    treatment   DOUBLE,
    rel_lift_pct DOUBLE,
    n_kontrol   INTEGER,
    n_treatment INTEGER
);
