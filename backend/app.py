from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Connexion à PostgreSQL
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

# Route 1 — Vérifier que l'API fonctionne
@app.route("/")
def index():
    return jsonify({"message": "API Prix Sénégal fonctionne ✅"})

# Route 2 — Récupérer tous les produits
@app.route("/produits")
def get_produits():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nom, categorie, prix, magasin, date FROM produits LIMIT 50;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    produits = []
    for row in rows:
        produits.append({
            "nom": row[0],
            "categorie": row[1],
            "prix": float(row[2]),
            "magasin": row[3],
            "date": str(row[4])
        })

    return jsonify(produits)

# Route 3 — Prix moyen par catégorie
@app.route("/stats/categories")
def stats_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT categorie,
               ROUND(AVG(prix)) as prix_moyen,
               MIN(prix) as prix_min,
               MAX(prix) as prix_max,
               COUNT(*) as nb_produits
        FROM produits
        GROUP BY categorie
        ORDER BY prix_moyen DESC;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    stats = []
    for row in rows:
        stats.append({
            "categorie": row[0],
            "prix_moyen": float(row[1]),
            "prix_min": float(row[2]),
            "prix_max": float(row[3]),
            "nb_produits": row[4]
        })

    return jsonify(stats)

# Route 4 — Prix par magasin
@app.route("/stats/magasins")
def stats_magasins():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT magasin,
               ROUND(AVG(prix)) as prix_moyen,
               COUNT(*) as nb_produits
        FROM produits
        GROUP BY magasin
        ORDER BY prix_moyen ASC;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    stats = []
    for row in rows:
        stats.append({
            "magasin": row[0],
            "prix_moyen": float(row[1]),
            "nb_produits": row[2]
        })

    return jsonify(stats)

if __name__ == "__main__":
    app.run(debug=True, port=5000)