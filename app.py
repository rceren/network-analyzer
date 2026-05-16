from flask import Flask, render_template_string
import sqlite3
import json

app = Flask(__name__)

def get_data():
    conn = sqlite3.connect("network_data.db")
    cursor = conn.cursor()

    # Protocol counts
    cursor.execute("SELECT protocol, COUNT(*) FROM packets GROUP BY protocol")
    protocols = cursor.fetchall()

    # Top 5 source IPs
    cursor.execute("SELECT src_ip, COUNT(*) as count FROM packets GROUP BY src_ip ORDER BY count DESC LIMIT 5")
    top_sources = cursor.fetchall()

    # Total packets
    cursor.execute("SELECT COUNT(*) FROM packets")
    total = cursor.fetchone()[0]

    # Total data transferred (bytes)
    cursor.execute("SELECT SUM(size) FROM packets")
    total_bytes = cursor.fetchone()[0]

    conn.close()
    return protocols, top_sources, total, total_bytes

@app.route("/")
def index():
    protocols, top_sources, total, total_bytes = get_data()

    protocol_labels = [p[0] for p in protocols]
    protocol_values = [p[1] for p in protocols]

    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Network Analyzer Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; }
            h1 { color: #38bdf8; text-align: center; }
            .cards { display: flex; gap: 20px; justify-content: center; margin: 30px 0; }
            .card { background: #1e293b; border-radius: 12px; padding: 20px 40px; text-align: center; }
            .card h2 { font-size: 2em; color: #38bdf8; margin: 0; }
            .card p { margin: 5px 0 0; color: #94a3b8; }
            .charts { display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; }
            .chart-box { background: #1e293b; border-radius: 12px; padding: 20px; width: 400px; }
            table { width: 100%%; border-collapse: collapse; margin-top: 10px; }
            th { color: #38bdf8; text-align: left; padding: 8px; border-bottom: 1px solid #334155; }
            td { padding: 8px; border-bottom: 1px solid #1e293b; }
        </style>
    </head>
    <body>
        <h1>🔌 Network Traffic Analyzer</h1>

        <div class="cards">
            <div class="card">
                <h2>''' + str(total) + '''</h2>
                <p>Total Packets</p>
            </div>
            <div class="card">
                <h2>''' + str(round(total_bytes / 1024, 1)) + ''' KB</h2>
                <p>Total Data</p>
            </div>
            <div class="card">
                <h2>''' + str(len(protocol_labels)) + '''</h2>
                <p>Protocol Types</p>
            </div>
        </div>

        <div class="charts">
            <div class="chart-box">
                <h3>Protocol Breakdown</h3>
                <canvas id="protocolChart"></canvas>
            </div>
            <div class="chart-box">
                <h3>Top 5 Source IPs</h3>
                <table>
                    <tr><th>IP Address</th><th>Packets</th></tr>
                    ''' + ''.join(f'<tr><td>{ip}</td><td>{count}</td></tr>' for ip, count in top_sources) + '''
                </table>
            </div>
        </div>

        <script>
            new Chart(document.getElementById("protocolChart"), {
                type: "doughnut",
                data: {
                    labels: ''' + json.dumps(protocol_labels) + ''',
                    datasets: [{
                        data: ''' + json.dumps(protocol_values) + ''',
                        backgroundColor: ["#38bdf8","#818cf8","#34d399","#fb923c","#f472b6"]
                    }]
                },
                options: { plugins: { legend: { labels: { color: "#e2e8f0" } } } }
            });
        </script>
    </body>
    </html>
    '''
    return html

if __name__ == "__main__":
    app.run(debug=True)