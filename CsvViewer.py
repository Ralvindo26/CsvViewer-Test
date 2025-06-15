from flask import Flask, render_template_string, request, jsonify
import pandas as pd
import requests
from io import StringIO

app = Flask(__name__)

# Ganti dengan ID file Google Drive Anda
CSV_FILE_ID = '1xsbXo_xoc0pa2JYX4wMpvY9eML4VfKo1'
CSV_URL = f"https://drive.google.com/uc?id={CSV_FILE_ID}&export=download"

CSV_LOG_FILE_ID = '19iFxkZaQxvla8mwZSBGX7pSt5v_Ws9DM'
CSV_LOG_URL = f"https://drive.google.com/uc?id={CSV_LOG_FILE_ID}&export=download"

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Stok Barang & Log Penjualan</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <style>
            body { padding-bottom: 50px; }
            .menu-bar { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px; }
            .menu-link {
                background-color: #007bff;
                color: white;
                padding: 8px 12px;
                text-decoration: none;
                border-radius: 4px;
                font-weight: 500;
            }
            .menu-link:hover, .menu-link.active {
                background-color: #0056b3;
            }
            table { table-layout: fixed; width: 100%; word-wrap: break-word; }
            th, td { text-align: center; vertical-align: middle; }
        </style>
    </head>
    <body>
        <div class="container mt-4 mb-4">
            <h2 class="mb-3">Data Stock Barang</h2>
            <div class="menu-bar">
                <a href="javascript:void(0);" class="menu-link active" onclick="showTab('stok')">Tabel Stok Barang</a>
                <a href="javascript:void(0);" class="menu-link" onclick="showTab('log')">Tabel Log Penjualan</a>
            </div>

            <div id="stok-barang"></div>
            <div id="log-penjualan" style="display: none;"></div>
        </div>

        <script>
            function loadStokBarang() {
                fetch('/data_stok')
                    .then(response => response.text())
                    .then(html => {
                        document.getElementById('stok-barang').innerHTML = html;
                    });
            }

            function loadLogPenjualan() {
                fetch('/data_log')
                    .then(response => response.text())
                    .then(html => {
                        document.getElementById('log-penjualan').innerHTML = html;
                    });
            }

            function showTab(tab) {
                document.querySelectorAll('.menu-link').forEach(el => el.classList.remove('active'));
                if (tab === 'stok') {
                    document.querySelector('.menu-link:nth-child(1)').classList.add('active');
                    document.getElementById('stok-barang').style.display = 'block';
                    document.getElementById('log-penjualan').style.display = 'none';
                } else {
                    document.querySelector('.menu-link:nth-child(2)').classList.add('active');
                    document.getElementById('stok-barang').style.display = 'none';
                    document.getElementById('log-penjualan').style.display = 'block';
                    if (!document.getElementById('log-penjualan').innerHTML.trim()) {
                        loadLogPenjualan();
                    }
                }
            }

            // Load stok barang by default
            loadStokBarang();
        </script>
    </body>
    </html>
    ''')

@app.route('/data_stok')
def get_stok_data():
    try:
        response = requests.get(CSV_URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.content.decode('utf-8'))).fillna('')

        df.columns = ['ID', 'Nama Barang', 'Stock Barang', 'Harga Beli', 'Harga Jual Umum', 'Harga Jual Reseller']

        table_html = df.to_html(classes='table table-bordered table-sm text-center w-100', index=False)
        return table_html
    except Exception as e:
        return f"<div class='alert alert-danger'>Gagal memuat data stok: {e}</div>"

@app.route('/data_log')
def get_log_data():
    try:
        response = requests.get(CSV_LOG_URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.content.decode('utf-8'))).fillna('')

        df.columns = ['Tanggal', 'Nama', 'Keterangan', 'Jumlah', 'Harga', 'Total', 'Untung']

        for col in ['Harga', 'Total', 'Untung']:
            df[col] = df[col].apply(
                lambda x: '0' if float(str(x).replace(' ', '').replace(',', '').strip()) == 0 
                else f"{float(str(x).replace(' ', '').replace(',', '').strip()):,.2f}"
            )

        table_html = f'''
        <div class="table-responsive">
            {df.to_html(classes='table table-bordered table-sm text-center w-100', index=False)}
        </div>
        '''
        return table_html
    except Exception as e:
        return f"<div class='alert alert-danger'>Gagal memuat log penjualan: {e}</div>"

if __name__ == '__main__':
    app.run(debug=True, port=5050)