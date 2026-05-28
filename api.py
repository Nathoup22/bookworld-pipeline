import os
import sqlite3
from flask import Flask, jsonify, request
 
app = Flask(__name__)
 
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
FINAL_DB_PATH = os.path.join(BASE_DIR, "bookworld_final.db")
API_TOKEN     = "bookworld-secret-token-2024"
 
 
def check_auth(req):
    auth_header = req.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    return auth_header.split(" ", 1)[1] == API_TOKEN
 
 
def get_db_connection():
    conn = sqlite3.connect(FINAL_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
 
 
@app.route("/", methods=["GET"])
def index():
    """Interface web de l'API."""
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BookWorld API</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: #0f1117; color: #e2e8f0; min-height: 100vh; }
 
    header {
      background: #1a1d27;
      border-bottom: 1px solid #2d3148;
      padding: 1.2rem 2rem;
      display: flex;
      align-items: center;
      gap: 12px;
    }
    header .logo { font-size: 1.4rem; font-weight: 700; color: #7c6af5; }
    header .sub  { font-size: 0.85rem; color: #64748b; margin-top: 2px; }
    .badge-live  { margin-left: auto; background: #16a34a22; color: #4ade80; border: 1px solid #4ade8033; padding: 4px 10px; border-radius: 20px; font-size: 12px; }
 
    main { max-width: 860px; margin: 2rem auto; padding: 0 1.5rem; }
 
    .token-box {
      background: #1a1d27;
      border: 1px solid #2d3148;
      border-radius: 10px;
      padding: 1rem 1.25rem;
      margin-bottom: 2rem;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .token-box label { font-size: 13px; color: #64748b; white-space: nowrap; }
    .token-box input {
      flex: 1;
      background: #0f1117;
      border: 1px solid #2d3148;
      border-radius: 6px;
      padding: 7px 12px;
      color: #a78bfa;
      font-family: monospace;
      font-size: 13px;
      outline: none;
    }
 
    h2 { font-size: 13px; font-weight: 600; color: #64748b; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 12px; }
 
    .endpoint-card {
      background: #1a1d27;
      border: 1px solid #2d3148;
      border-radius: 12px;
      margin-bottom: 12px;
      overflow: hidden;
    }
    .endpoint-header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 1rem 1.25rem;
    }
    .method { background: #16a34a22; color: #4ade80; border: 1px solid #4ade8033; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; }
    .route  { font-family: monospace; font-size: 14px; color: #e2e8f0; }
    .desc   { font-size: 12px; color: #64748b; margin-left: 4px; }
    .auth-badge { margin-left: auto; font-size: 11px; background: #7c3aed22; color: #a78bfa; border: 1px solid #7c3aed33; padding: 3px 9px; border-radius: 20px; }
    .no-auth-badge { margin-left: auto; font-size: 11px; background: #0f172a; color: #64748b; border: 1px solid #2d3148; padding: 3px 9px; border-radius: 20px; }
 
    .endpoint-footer {
      border-top: 1px solid #2d3148;
      padding: 0.75rem 1.25rem;
      display: flex;
      justify-content: flex-end;
    }
    .btn-test {
      background: #7c6af5;
      color: white;
      border: none;
      padding: 7px 18px;
      border-radius: 7px;
      font-size: 13px;
      cursor: pointer;
      transition: background 0.15s;
    }
    .btn-test:hover { background: #6c5ce7; }
    .btn-test:active { transform: scale(0.98); }
 
    .result-box {
      display: none;
      border-top: 1px solid #2d3148;
      padding: 1rem 1.25rem;
    }
    .result-box pre {
      background: #0f1117;
      border: 1px solid #2d3148;
      border-radius: 8px;
      padding: 12px;
      font-size: 12px;
      color: #a78bfa;
      overflow-x: auto;
      max-height: 320px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-all;
    }
    .status-ok    { color: #4ade80; font-size: 12px; margin-bottom: 8px; }
    .status-error { color: #f87171; font-size: 12px; margin-bottom: 8px; }
 
    footer { text-align: center; padding: 2rem; font-size: 12px; color: #2d3148; }
  </style>
</head>
<body>
 
<header>
  <div>
    <div class="logo">📚 BookWorld API</div>
    <div class="sub">Pipeline de données — Examen final DataBird</div>
  </div>
  <div class="badge-live">● Live</div>
</header>
 
<main>
 
  <div class="token-box">
    <label>🔑 Bearer Token</label>
    <input id="token" type="text" value="bookworld-secret-token-2024" />
  </div>
 
  <h2>Endpoints disponibles</h2>
 
  <div class="endpoint-card">
    <div class="endpoint-header">
      <span class="method">GET</span>
      <span class="route">/health</span>
      <span class="desc">— Statut de l'API</span>
      <span class="no-auth-badge">🔓 Sans auth</span>
    </div>
    <div class="result-box" id="res-health">
      <div id="status-health"></div>
      <pre id="pre-health"></pre>
    </div>
    <div class="endpoint-footer">
      <button class="btn-test" onclick="callApi('/health', false, 'health')">▶ Tester</button>
    </div>
  </div>
 
  <div class="endpoint-card">
    <div class="endpoint-header">
      <span class="method">GET</span>
      <span class="route">/sales-by-country</span>
      <span class="desc">— Ventes agrégées par pays</span>
      <span class="auth-badge">🔒 Auth requise</span>
    </div>
    <div class="result-box" id="res-sales">
      <div id="status-sales"></div>
      <pre id="pre-sales"></pre>
    </div>
    <div class="endpoint-footer">
      <button class="btn-test" onclick="callApi('/sales-by-country', true, 'sales')">▶ Tester</button>
    </div>
  </div>
 
</main>
 
<footer>BookWorld · Examen final DataBird · 2024</footer>
 
<script>
async function callApi(endpoint, requiresAuth, key) {
  const token = document.getElementById('token').value.trim();
  const resBox = document.getElementById('res-' + key);
  const statusEl = document.getElementById('status-' + key);
  const preEl = document.getElementById('pre-' + key);
 
  resBox.style.display = 'block';
  preEl.textContent = 'Chargement...';
  statusEl.textContent = '';
 
  const headers = { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': 'true' };
  if (requiresAuth) headers['Authorization'] = 'Bearer ' + token;
 
  try {
    const res = await fetch(endpoint, { headers });
    const data = await res.json();
    preEl.textContent = JSON.stringify(data, null, 2);
    statusEl.className = res.ok ? 'status-ok' : 'status-error';
    statusEl.textContent = res.ok ? '✓ ' + res.status + ' OK' : '✗ ' + res.status + ' Erreur';
  } catch (e) {
    preEl.textContent = 'Erreur : ' + e.message;
    statusEl.className = 'status-error';
    statusEl.textContent = '✗ Impossible de contacter l API';
  }
}
</script>
 
</body>
</html>"""
    return html
 
 
@app.route("/health", methods=["GET"])
def health():
    db_ok = os.path.exists(FINAL_DB_PATH)
    return jsonify({
        "status": "ok",
        "database": "available" if db_ok else "missing"
    }), 200
 
 
@app.route("/sales-by-country", methods=["GET"])
def sales_by_country():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized. Provide a valid Bearer token."}), 401
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT country_code, country_name, total_orders,
                   total_quantity, total_revenue_gbp, total_revenue_eur
            FROM sales_by_country
            ORDER BY total_revenue_gbp DESC
        """)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return jsonify({"data": rows, "count": len(rows)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
 
if __name__ == "__main__":
    print("BookWorld API — http://127.0.0.1:5000")
    print("Token : " + API_TOKEN)
    app.run(debug=True)
 