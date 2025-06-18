from flask import Flask, render_template_string, request
import pandas as pd
import requests
from io import StringIO
from datetime import datetime

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
        <title>Data Stok & Log Penjualan</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <style>
            body { padding-bottom: 50px; font-size: 0.85rem; }
            .menu-bar { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px; }
            .menu-link {
                background-color: skyblue; color: white; padding: 6px 12px;
                text-decoration: none; border-radius: 4px; font-weight: 500;
            }
            .menu-link:hover, .menu-link.active { background-color: skyblue; }
            table { font-size: 0.75rem; }
            th, td { text-align: center; vertical-align: middle; padding: 6px !important; }
        </style>
    </head>
    <body>
        <div class="container mt-4 mb-4">
            <h4 class="mb-3">Data Stock Barang</h4>
            <div class="menu-bar">
                <a href="javascript:void(0);" class="menu-link active" onclick="showTab('stok')">Tabel Stok Barang</a>
                <a href="javascript:void(0);" class="menu-link" onclick="showTab('log')">Tabel Log Penjualan</a>
            </div>

            <div id="search-container">
                <input type="text" class="form-control form-control-sm mb-2" id="search-barang" placeholder="Cari Nama Barang..." onkeyup="filterStok()">
            </div>
            <div class="form-row mb-2" id="log-filter" style="display: none;">
                <div class="col"><input type="date" id="from-date" class="form-control form-control-sm" /></div>
                <div class="col"><input type="date" id="to-date" class="form-control form-control-sm" /></div>
                <div class="col-auto">
                    <button class="btn btn-sm btn-primary" onclick="filterLog()">Filter</button>
                    <button class="btn btn-sm btn-secondary ml-1" onclick="resetFilter()">Reset</button>
                </div>
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

            function filterStok() {
                const input = document.getElementById('search-barang').value.toLowerCase();
                const rows = document.querySelectorAll('#stok-barang table tbody tr');
                rows.forEach(row => {
                    const text = row.cells[1].textContent.toLowerCase();
                    row.style.display = text.includes(input) ? '' : 'none';
                });
            }

            function filterLog() {
                const fromDate = document.getElementById('from-date').value;
                const toDate = document.getElementById('to-date').value;

                fetch(`/data_log?from=${fromDate}&to=${toDate}`)
                    .then(response => response.text())
                    .then(html => {
                        document.getElementById('log-penjualan').innerHTML = html;
                    });
            }

            function resetFilter() {
                document.getElementById('from-date').value = '';
                document.getElementById('to-date').value = '';
                loadLogPenjualan();
            }

            function showTab(tab) {
                document.querySelectorAll('.menu-link').forEach(el => el.classList.remove('active'));
                if (tab === 'stok') {
                    document.querySelector('.menu-link:nth-child(1)').classList.add('active');
                    document.getElementById('stok-barang').style.display = 'block';
                    document.getElementById('log-penjualan').style.display = 'none';
                    document.getElementById('search-container').style.display = 'block';
                    document.getElementById('log-filter').style.display = 'none';
                } else {
                    document.querySelector('.menu-link:nth-child(2)').classList.add('active');
                    document.getElementById('stok-barang').style.display = 'none';
                    document.getElementById('log-penjualan').style.display = 'block';
                    document.getElementById('search-container').style.display = 'none';
                    document.getElementById('log-filter').style.display = 'flex';
                    if (!document.getElementById('log-penjualan').innerHTML.trim()) {
                        loadLogPenjualan();
                    }
                }
            }

            loadStokBarang(); // default load
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

        return df.to_html(classes='table table-bordered table-sm text-center w-100', index=False)
    except Exception as e:
        return f"<div class='alert alert-danger'>Gagal memuat data stok: {e}</div>"

@app.route('/data_log')
def get_log_data():
    try:
        from_date = request.args.get('from')
        to_date = request.args.get('to')

        response = requests.get(CSV_LOG_URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.content.decode('utf-8'))).fillna('')
        df.columns = ['Tanggal', 'Nama', 'Keterangan', 'Jumlah', 'Harga', 'Total Harga', 'Penerima', 'Keuntungan']

        if from_date and to_date:
            df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
            df = df[(df['Tanggal'] >= from_date) & (df['Tanggal'] <= to_date)]

        total_untung = 0
        for col in ['Harga', 'Total Harga', 'Keuntungan']:
            df[col] = df[col].apply(lambda x: str(x).replace(' ', '').replace(',', '').strip())
            df[col] = df[col].apply(lambda x: float(x) if x.replace('.', '', 1).isdigit() else 0)
            if col == 'Keuntungan':
                total_untung = df[col].sum()
            df[col] = df[col].apply(lambda x: f"{x:,.2f}")

        table_html = f'''
        <div class="mt-2 font-weight-bold text-right">Total Keuntungan: Rp {total_untung:,.2f}</div>
        <div class="table-responsive mt-2">
            {df.to_html(classes='table table-bordered table-sm text-center w-100', index=False)}
        </div>
        '''
        return table_html
    except Exception as e:
        return f"<div class='alert alert-danger'>Gagal memuat log penjualan: {e}</div>"

if __name__ == '__main__':
    app.run(debug=True, port=5050)