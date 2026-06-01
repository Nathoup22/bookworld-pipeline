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
      <span class="desc">— Dashboard ventes par pays</span>
      <span class="auth-badge">🔒 Auth requise</span>
    </div>
    <div style="padding:0.6rem 1.25rem;border-top:1px solid #2d3148;font-size:12px;color:#64748b;">
      Retourne un dashboard HTML. Ajouter <code style="background:#0f1117;padding:1px 5px;border-radius:4px;color:#a78bfa">?format=json</code> pour le JSON brut.
    </div>
    <div id="dashboard-container" style="display:none; border-top:1px solid #2d3148;">
      <iframe id="dashboard-frame" style="width:100%; height:600px; border:none; display:block;"></iframe>
    </div>
    <div class="result-box" id="res-sales">
      <div id="status-sales"></div>
      <pre id="pre-sales"></pre>
    </div>
    <div class="endpoint-footer" style="gap:8px">
      <button class="btn-test" onclick="openDashboard()">&#9654; Afficher le dashboard</button>
      <button class="btn-test" onclick="callApi('/sales-by-country?format=json', true, 'sales')" style="opacity:.75">{ } JSON</button>
    </div>
  </div>
 
</main>
 
<footer>BookWorld · Examen final DataBird · 2024</footer>
 
<script>
function openDashboard() {
  const token = document.getElementById('token').value.trim();
  const container = document.getElementById('dashboard-container');
  const frame = document.getElementById('dashboard-frame');
  const btn = event.currentTarget;

  if (container.style.display !== 'none') {
    container.style.display = 'none';
    btn.textContent = '▶ Afficher le dashboard';
    return;
  }

  btn.textContent = 'Chargement…';
  fetch('/sales-by-country', { headers: { 'Authorization': 'Bearer ' + token } })
    .then(r => r.text())
    .then(html => {
      const blob = new Blob([html], { type: 'text/html' });
      frame.src = URL.createObjectURL(blob);
      container.style.display = 'block';
      btn.textContent = '✕ Masquer le dashboard';
    })
    .catch(e => {
      btn.textContent = '▶ Afficher le dashboard';
      alert('Erreur : ' + e.message);
    });
}
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
 
 
def _query_sales(country_code=None, region=None, min_revenue=None, min_orders=None):
    """Exécute la requête filtrée et retourne (rows, filters_applied)."""
    query = """
        SELECT s.country_code, s.country_name, s.total_orders,
               s.total_quantity, s.total_revenue_gbp, s.total_revenue_eur,
               c.region
        FROM sales_by_country s
        LEFT JOIN countries c ON s.country_code = c.country_code
        WHERE 1=1
    """
    params = []
    if country_code:
        query += " AND s.country_code = ?"
        params.append(country_code)
    if region:
        query += " AND c.region = ?"
        params.append(region)
    if min_revenue is not None:
        query += " AND s.total_revenue_gbp >= ?"
        params.append(min_revenue)
    if min_orders is not None:
        query += " AND s.total_orders >= ?"
        params.append(min_orders)
    query += " ORDER BY s.total_revenue_gbp DESC"

    conn = get_db_connection()
    rows = [dict(r) for r in conn.execute(query, params).fetchall()]
    conn.close()

    filters_applied = {k: v for k, v in {
        "country_code": country_code, "region": region,
        "min_revenue_gbp": min_revenue, "min_orders": min_orders,
    }.items() if v is not None}

    return rows, filters_applied


@app.route("/sales-by-country", methods=["GET"])
def sales_by_country():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized. Provide a valid Bearer token."}), 401

    country_code = request.args.get("country_code", "").upper() or None
    region       = request.args.get("region", "") or None
    min_revenue  = request.args.get("min_revenue_gbp", type=float)
    min_orders   = request.args.get("min_orders", type=int)
    fmt          = request.args.get("format", "html")

    try:
        rows, filters_applied = _query_sales(country_code, region, min_revenue, min_orders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if fmt == "json":
        return jsonify({"count": len(rows), "filters_applied": filters_applied, "data": rows}), 200

    # ── Dashboard HTML ────────────────────────────────────────────────────────
    import json as _json

    total_orders   = sum(r["total_orders"]   for r in rows)
    total_qty      = sum(r["total_quantity"]  for r in rows)
    total_gbp      = round(sum(r["total_revenue_gbp"] for r in rows), 2)
    total_eur      = round(sum(r["total_revenue_eur"] for r in rows), 2)
    data_json      = _json.dumps(rows)

    FLAGS = {"FR":"🇫🇷","DE":"🇩🇪","BE":"🇧🇪","ES":"🇪🇸","IT":"🇮🇹",
             "IE":"🇮🇪","GB":"🇬🇧","US":"🇺🇸","CA":"🇨🇦","PT":"🇵🇹",
             "NL":"🇳🇱","CH":"🇨🇭","AT":"🇦🇹","SE":"🇸🇪","DK":"🇩🇰",
             "NO":"🇳🇴","FI":"🇫🇮","PL":"🇵🇱","JP":"🇯🇵","AU":"🇦🇺"}

    rows_html = ""
    max_gbp = max((r["total_revenue_gbp"] for r in rows), default=1)
    max_eur = max((r["total_revenue_eur"] for r in rows), default=1)
    for r in rows:
        flag  = FLAGS.get(r["country_code"], "🌐")
        pctG  = round(r["total_revenue_gbp"] / max_gbp * 100, 1)
        pctE  = round(r["total_revenue_eur"] / max_eur * 100, 1)
        rows_html += f"""
        <tr>
          <td><span class="flag">{flag}</span>{r["country_name"]}
              <span class="cc">{r["country_code"]}</span></td>
          <td>{r["total_orders"]}</td>
          <td>{r["total_quantity"]}</td>
          <td>
            <div class="bar-cell">
              <div class="bar-bg"><div class="bar-fill" style="width:{pctG}%;background:#378ADD"></div></div>
              <span class="num">£{r["total_revenue_gbp"]:.2f}</span>
            </div>
          </td>
          <td>
            <div class="bar-cell">
              <div class="bar-bg"><div class="bar-fill" style="width:{pctE}%;background:#1D9E75"></div></div>
              <span class="num">€{r["total_revenue_eur"]:.2f}</span>
            </div>
          </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ventes par pays — BookWorld</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bg:#ffffff; --bg2:#f7f7f5; --bg3:#f0efe9;
      --border:rgba(0,0,0,.10); --border2:rgba(0,0,0,.18);
      --text:#1a1a18; --text2:#5f5e5a; --text3:#888780;
      --radius:8px; --radius-lg:12px;
      --mono:'Menlo','Consolas',monospace;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg:#1c1c1a; --bg2:#242422; --bg3:#2c2c2a;
        --border:rgba(255,255,255,.10); --border2:rgba(255,255,255,.20);
        --text:#e8e8e4; --text2:#888780; --text3:#5f5e5a;
      }}
    }}
    body {{ font-family: system-ui,-apple-system,sans-serif; background:var(--bg); color:var(--text); min-height:100vh; }}
    .topbar {{ border-bottom:0.5px solid var(--border); padding:1rem 2rem; display:flex; align-items:center; gap:10px; }}
    .back {{ font-size:13px; color:var(--text2); text-decoration:none; display:flex; align-items:center; gap:4px; margin-right:4px; }}
    .back:hover {{ color:var(--text); }}
    .page-title {{ font-size:15px; font-weight:500; }}
    .page-sub {{ font-size:12px; color:var(--text2); margin-top:1px; }}
    .json-link {{ margin-left:auto; font-size:12px; color:#185FA5; text-decoration:none; display:flex; align-items:center; gap:4px; border:0.5px solid var(--border2); padding:5px 12px; border-radius:var(--radius); }}
    .json-link:hover {{ background:var(--bg2); }}
    main {{ max-width:900px; margin:0 auto; padding:2rem 1.5rem; }}
    .filters-bar {{ background:var(--bg2); border-radius:var(--radius); padding:8px 14px; margin-bottom:1.5rem; font-size:12px; color:var(--text2); display:flex; align-items:center; gap:8px; }}
    .filter-tag {{ background:var(--bg); border:0.5px solid var(--border2); border-radius:4px; padding:2px 8px; color:var(--text); font-family:var(--mono); font-size:11px; }}
    .metrics {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:1.5rem; }}
    .metric {{ background:var(--bg2); border-radius:var(--radius); padding:12px 14px; }}
    .ml {{ font-size:12px; color:var(--text2); margin-bottom:4px; }}
    .mv {{ font-size:20px; font-weight:500; }}
    .ms {{ font-size:11px; color:var(--text3); margin-top:2px; }}
    .card {{ background:var(--bg); border:0.5px solid var(--border); border-radius:var(--radius-lg); margin-bottom:1.25rem; overflow:hidden; }}
    .card-head {{ display:flex; align-items:center; justify-content:space-between; padding:12px 16px; border-bottom:0.5px solid var(--border); }}
    .card-title {{ font-size:13px; font-weight:500; }}
    .legend {{ display:flex; gap:14px; }}
    .leg {{ display:flex; align-items:center; gap:5px; font-size:11px; color:var(--text2); }}
    .leg-sq {{ width:9px; height:9px; border-radius:2px; }}
    table {{ width:100%; border-collapse:collapse; table-layout:fixed; }}
    thead tr {{ border-bottom:0.5px solid var(--border); }}
    th {{ font-size:11px; font-weight:500; color:var(--text2); padding:9px 16px; text-align:left; letter-spacing:.04em; }}
    td {{ font-size:13px; padding:10px 16px; border-bottom:0.5px solid var(--border); }}
    tr:last-child td {{ border-bottom:none; }}
    tr:hover td {{ background:var(--bg2); }}
    .flag {{ font-size:16px; margin-right:6px; }}
    .cc {{ font-family:var(--mono); font-size:11px; color:var(--text2); background:var(--bg2); padding:1px 5px; border-radius:3px; margin-left:4px; }}
    .bar-cell {{ display:flex; align-items:center; gap:8px; }}
    .bar-bg {{ flex:1; height:6px; background:var(--bg3); border-radius:3px; overflow:hidden; }}
    .bar-fill {{ height:100%; border-radius:3px; }}
    .num {{ font-family:var(--mono); font-size:12px; min-width:60px; text-align:right; color:var(--text); }}
    footer {{ text-align:center; padding:2rem; font-size:12px; color:var(--text3); border-top:0.5px solid var(--border); margin-top:1rem; }}
  </style>
</head>
<body>

<div class="topbar">
  <a href="/" class="back">← Accueil</a>
  <div>
    <div class="page-title">Ventes par pays</div>
    <div class="page-sub">GET /sales-by-country · {len(rows)} résultats</div>
  </div>
  <a href="/sales-by-country?format=json" class="json-link">↗ JSON brut</a>
</div>

<main>

  {"" if not filters_applied else f'''<div class="filters-bar">Filtres actifs : {"".join(f'<span class="filter-tag">{k}={v}</span>' for k,v in filters_applied.items())}</div>'''}

  <div class="metrics">
    <div class="metric"><div class="ml">Pays</div><div class="mv">{len(rows)}</div><div class="ms">dans la sélection</div></div>
    <div class="metric"><div class="ml">Commandes</div><div class="mv">{total_orders}</div><div class="ms">total</div></div>
    <div class="metric"><div class="ml">Revenu GBP</div><div class="mv">£{total_gbp:,.2f}</div><div class="ms">livres sterling</div></div>
    <div class="metric"><div class="ml">Revenu EUR</div><div class="mv">€{total_eur:,.2f}</div><div class="ms">euros</div></div>
  </div>

  <div class="card">
    <div class="card-head">
      <span class="card-title">Revenu par pays</span>
      <div class="legend">
        <div class="leg"><div class="leg-sq" style="background:#378ADD"></div>GBP</div>
        <div class="leg"><div class="leg-sq" style="background:#1D9E75"></div>EUR</div>
      </div>
    </div>
    <div style="padding:16px">
      <div style="position:relative;width:100%;height:220px">
        <canvas id="barChart" role="img" aria-label="Graphique revenu GBP et EUR par pays"></canvas>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="card-head"><span class="card-title">Détail par pays</span></div>
    <table>
      <thead><tr>
        <th style="width:28%">Pays</th>
        <th style="width:12%">Commandes</th>
        <th style="width:12%">Quantité</th>
        <th style="width:24%">Revenu GBP</th>
        <th style="width:24%">Revenu EUR</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
  </div>

</main>

<footer>BookWorld · Examen final DataBird · 2024</footer>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script>
const DATA = {data_json};
new Chart(document.getElementById("barChart"), {{
  type: "bar",
  data: {{
    labels: DATA.map(d => d.country_name),
    datasets: [
      {{ label:"GBP", data:DATA.map(d=>d.total_revenue_gbp), backgroundColor:"#378ADD", borderRadius:3 }},
      {{ label:"EUR", data:DATA.map(d=>d.total_revenue_eur), backgroundColor:"#1D9E75", borderRadius:3 }}
    ]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ grid: {{ display:false }}, ticks: {{ font:{{size:11}}, color:"#888780", autoSkip:false, maxRotation:0 }} }},
      y: {{ grid: {{ color:"rgba(128,128,128,.15)" }}, ticks: {{ font:{{size:11}}, color:"#888780", callback: v => "£"+v }} }}
    }}
  }}
}});
</script>
</body>
</html>"""
    return html
 
 
if __name__ == "__main__":
    print("BookWorld API — http://127.0.0.1:5000")
    print("Token : " + API_TOKEN)
    app.run(debug=True)