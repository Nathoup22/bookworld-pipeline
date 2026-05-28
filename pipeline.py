"""
pipeline.py
BookWorld - Pipeline de données complet
Extraction -> Nettoyage -> Enrichissement -> Aggregation -> Base finale
"""

import os
import sqlite3
import csv
import requests
from bs4 import BeautifulSoup

BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
CSV_PATH        = os.path.join(BASE_DIR, "sales_raw.csv")
SQL_PATH        = os.path.join(BASE_DIR, "bookworld_reference.sql")
REF_DB_PATH     = os.path.join(BASE_DIR, "bookworld_reference.db")
FINAL_DB_PATH   = os.path.join(BASE_DIR, "bookworld_final.db")


# ================================================================
# PARTIE 1 - EXTRACTION
# ================================================================

def extract_csv(path=CSV_PATH):
    """Lit le fichier CSV de ventes brutes."""
    sales = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sales.append(row)
        print(f"[CSV] {len(sales)} lignes chargees.")
    except FileNotFoundError:
        print(f"[CSV] Erreur : fichier introuvable ({path})")
    return sales


def create_reference_db(sql_path=SQL_PATH, db_path=REF_DB_PATH):
    """Cree la base de reference SQLite depuis le fichier .sql."""
    if not os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            with open(sql_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            conn.commit()
            conn.close()
            print("[SQLite] Base de reference creee.")
        except Exception as e:
            print(f"[SQLite] Erreur creation base : {e}")
    else:
        print("[SQLite] Base de reference deja existante.")


def extract_sqlite(db_path=REF_DB_PATH):
    """Extrait les donnees de reference depuis la base SQLite."""
    data = {"countries": [], "channels": [], "category_rules": []}
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Requete avec filtre : pays actifs seulement
        cursor.execute("""
            SELECT country_code, country_name, currency_code, vat_rate, region
            FROM countries
            WHERE is_active = 1
        """)
        data["countries"] = [dict(r) for r in cursor.fetchall()]

        # Canaux actifs
        cursor.execute("""
            SELECT channel_code, channel_name, acquisition_cost_gbp, channel_group
            FROM channels
            WHERE is_active = 1
        """)
        data["channels"] = [dict(r) for r in cursor.fetchall()]

        # Regles de categories actives (enrichissement)
        cursor.execute("""
            SELECT category_name, margin_rate, strategic_flag, default_channel_code
            FROM category_rules
            WHERE is_active = 1
        """)
        data["category_rules"] = [dict(r) for r in cursor.fetchall()]

        conn.close()
        print(f"[SQLite] {len(data['countries'])} pays, "
              f"{len(data['channels'])} canaux, "
              f"{len(data['category_rules'])} categories charges.")
    except Exception as e:
        print(f"[SQLite] Erreur extraction : {e}")
    return data


def scrape_books(url="https://books.toscrape.com/"):
    """Scrape la premiere page du catalogue books.toscrape.com."""
    books = []
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for article in soup.select("article.product_pod"):
            title = article.h3.a["title"]
            price_text = article.select_one(".price_color").text.strip()
            price_gbp = float("".join(c for c in price_text if c.isdigit() or c == "."))
            rating_word = article.p["class"][1]
            rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
            rating = rating_map.get(rating_word, 0)
            books.append({"title": title, "price_gbp": price_gbp, "rating": rating})

        print(f"[Scraping] {len(books)} livres recuperes.")
    except Exception as e:
        print(f"[Scraping] Erreur : {e}")
    return books


def fetch_exchange_rate(base="GBP", target="EUR"):
    """Recupere le taux de change GBP -> EUR via l'API Frankfurter."""
    try:
        url = f"https://api.frankfurter.app/latest?from={base}&to={target}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        rate = response.json()["rates"][target]
        print(f"[API Frankfurter] 1 {base} = {rate} {target}")
        return rate
    except Exception as e:
        print(f"[API Frankfurter] Erreur : {e}. Taux de repli 1.17 utilise.")
        return 1.17


# ================================================================
# PARTIE 2 - NETTOYAGE, ENRICHISSEMENT & AGREGATION
# ================================================================

def clean_sales(sales):
    """Nettoie les donnees de ventes.
    RGPD : suppression de customer_first_name et customer_last_name.
    """
    cleaned = []
    for row in sales:
        try:
            cleaned.append({
                "order_id":      row["order_id"].strip(),
                "order_date":    row["order_date"].strip(),
                "book_id":       row["book_id"].strip(),
                "book_name":     row["book_name"].strip(),
                "country_code":  row["country_code"].strip().upper(),
                "channel_code":  row["channel_code"].strip().upper(),
                "quantity":      int(row["quantity"]),
                "discount_rate": float(row["discount_rate"]),
                # customer_first_name et customer_last_name exclus (RGPD)
            })
        except (ValueError, KeyError) as e:
            print(f"[Nettoyage] Ligne ignoree ({e})")
    print(f"[Nettoyage] {len(cleaned)} lignes valides apres nettoyage.")
    return cleaned


def aggregate_sales_by_country(sales, ref_data, gbp_to_eur):
    """Produit l'agregation sales_by_country."""
    countries_index = {c["country_code"]: c for c in ref_data["countries"]}

    aggregated = {}
    for row in sales:
        code = row["country_code"]
        if code not in aggregated:
            country_info = countries_index.get(code, {})
            aggregated[code] = {
                "country_code":      code,
                "country_name":      country_info.get("country_name", "Unknown"),
                "total_orders":      0,
                "total_quantity":    0,
                "total_revenue_gbp": 0.0,
            }
        qty     = row["quantity"]
        revenue = qty * (1 - row["discount_rate"])
        aggregated[code]["total_orders"]      += 1
        aggregated[code]["total_quantity"]    += qty
        aggregated[code]["total_revenue_gbp"] += revenue

    result = []
    for row in aggregated.values():
        row["total_revenue_eur"] = round(row["total_revenue_gbp"] * gbp_to_eur, 2)
        row["total_revenue_gbp"] = round(row["total_revenue_gbp"], 2)
        result.append(row)

    print(f"[Agregation] {len(result)} pays agreges.")
    return result


# ================================================================
# PARTIE 3 - BASE FINALE
# ================================================================

def create_final_db(sales_clean, ref_data, sales_by_country, db_path=FINAL_DB_PATH):
    """Cree la base SQLite finale et l'alimente."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
        DROP TABLE IF EXISTS sales;
        DROP TABLE IF EXISTS sales_by_country;
        DROP TABLE IF EXISTS countries;
        DROP TABLE IF EXISTS channels;

        CREATE TABLE countries (
            country_code  TEXT PRIMARY KEY,
            country_name  TEXT NOT NULL,
            currency_code TEXT NOT NULL,
            vat_rate      REAL NOT NULL,
            region        TEXT NOT NULL
        );

        CREATE TABLE channels (
            channel_code         TEXT PRIMARY KEY,
            channel_name         TEXT NOT NULL,
            acquisition_cost_gbp REAL NOT NULL,
            channel_group        TEXT NOT NULL
        );

        CREATE TABLE sales (
            order_id      TEXT PRIMARY KEY,
            order_date    TEXT NOT NULL,
            book_id       TEXT NOT NULL,
            book_name     TEXT NOT NULL,
            country_code  TEXT NOT NULL,
            channel_code  TEXT NOT NULL,
            quantity      INTEGER NOT NULL,
            discount_rate REAL NOT NULL,
            FOREIGN KEY (country_code) REFERENCES countries(country_code),
            FOREIGN KEY (channel_code) REFERENCES channels(channel_code)
        );

        CREATE TABLE sales_by_country (
            country_code      TEXT PRIMARY KEY,
            country_name      TEXT NOT NULL,
            total_orders      INTEGER NOT NULL,
            total_quantity    INTEGER NOT NULL,
            total_revenue_gbp REAL NOT NULL,
            total_revenue_eur REAL NOT NULL
        );
    """)

    cursor.executemany(
        "INSERT OR IGNORE INTO countries VALUES (:country_code,:country_name,:currency_code,:vat_rate,:region)",
        ref_data["countries"]
    )
    cursor.executemany(
        "INSERT OR IGNORE INTO channels VALUES (:channel_code,:channel_name,:acquisition_cost_gbp,:channel_group)",
        ref_data["channels"]
    )
    cursor.executemany("""
        INSERT OR IGNORE INTO sales
        VALUES (:order_id,:order_date,:book_id,:book_name,
                :country_code,:channel_code,:quantity,:discount_rate)
    """, sales_clean)
    cursor.executemany("""
        INSERT OR REPLACE INTO sales_by_country
        VALUES (:country_code,:country_name,:total_orders,
                :total_quantity,:total_revenue_gbp,:total_revenue_eur)
    """, sales_by_country)

    conn.commit()
    conn.close()
    print(f"[Base finale] '{db_path}' creee et alimentee.")


# ================================================================
# POINT D'ENTREE
# ================================================================

def main():
    print("=" * 50)
    print("  BOOKWORLD - Pipeline de donnees")
    print("=" * 50)

    print("\n-- Extraction --")
    sales_raw  = extract_csv()
    create_reference_db()
    ref_data   = extract_sqlite()
    books      = scrape_books()
    gbp_to_eur = fetch_exchange_rate()

    print("\n-- Nettoyage & Agregation --")
    sales_clean      = clean_sales(sales_raw)
    sales_by_country = aggregate_sales_by_country(sales_clean, ref_data, gbp_to_eur)

    print("\n-- Base finale --")
    create_final_db(sales_clean, ref_data, sales_by_country)

    print("\n✓ Pipeline termine avec succes.")
    print(f"  Base finale : {FINAL_DB_PATH}")


if __name__ == "__main__":
    main()