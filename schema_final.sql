-- ============================================================
-- Table 1 : sales
-- Ventes nettoyées et enrichies, une ligne par commande.
-- ============================================================
CREATE TABLE IF NOT EXISTS sales (
    order_id        TEXT    NOT NULL,
    order_date      TEXT    NOT NULL,
    book_id         TEXT    NOT NULL,
    book_name       TEXT    NOT NULL,
    country_code    TEXT    NOT NULL,
    country_name    TEXT    NOT NULL,
    currency_code   TEXT    NOT NULL,
    vat_rate        REAL    NOT NULL,
    region          TEXT    NOT NULL,
    channel_code    TEXT    NOT NULL,
    quantity        INTEGER NOT NULL,
    discount_rate   REAL    NOT NULL DEFAULT 0.0,
    revenue_gbp     REAL    NOT NULL,
    revenue_eur     REAL    NOT NULL,

    PRIMARY KEY (order_id),
    FOREIGN KEY (country_code) REFERENCES countries(country_code),
    FOREIGN KEY (channel_code) REFERENCES channels(channel_code)
);


-- ============================================================
-- Table 2 : sales_by_country
-- Agrégation des ventes par pays.
-- ============================================================
CREATE TABLE IF NOT EXISTS sales_by_country (
    country_code        TEXT    NOT NULL,
    country_name        TEXT    NOT NULL,
    total_orders        INTEGER NOT NULL DEFAULT 0,
    total_quantity      INTEGER NOT NULL DEFAULT 0,
    total_revenue_gbp   REAL    NOT NULL DEFAULT 0.0,
    total_revenue_eur   REAL    NOT NULL DEFAULT 0.0,

    PRIMARY KEY (country_code)
);


-- ============================================================
-- Index utiles pour les requêtes fréquentes
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_sales_country   ON sales(country_code);
CREATE INDEX IF NOT EXISTS idx_sales_channel   ON sales(channel_code);
CREATE INDEX IF NOT EXISTS idx_sales_date      ON sales(order_date);
