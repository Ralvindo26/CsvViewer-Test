from flask import Flask, render_template_string, request
import pandas as pd
import requests
from io import StringIO

app = Flask(__name__)

CSV_FILE_ID = '1xsbXo_xoc0pa2JYX4wMpvY9eML4VfKo1'
CSV_URL = f"https://drive.google.com/uc?id={CSV_FILE_ID}&export=download"

CSV_LOG_FILE_ID = '19iFxkZaQxvla8mwZSBGX7pSt5v_Ws9DM'
CSV_LOG_URL = f"https://drive.google.com/uc?id={CSV_LOG_FILE_ID}&export=download"

API_KEY = 'AIzaSyDszO0AB7zcrqeMasdB0lCCzqAUfMxn9xk'
FOLDER_ID = '1vho3OqCxglBW2QSS4wuDAgm_ccdN1y2z'  # Ganti dengan ID folder fotobarang

def cari_id_gambar(nama_barang):
    nama_file = nama_barang.lower().replace(' ', '_')
    query = f"'{FOLDER_ID}' in parents and name contains '{nama_file}' and mimeType contains 'image/' and trashed = false"
    url = f"https://www.googleapis.com/drive/v3/files?q={query}&key={API_KEY}&fields=files(id,name)"
    response = requests.get(url)
    data = response.json()
    if 'files' in data and data['files']:
        return f"https://drive.google.com/uc?id={data['files'][0]['id']}"
    else:
        return None

    # --- Ambil semua gambar dari folder hanya sekali ---
def ambil_semua_gambar_dari_folder():
    query = f"'{FOLDER_ID}' in parents and mimeType contains 'image/' and trashed = false"
    url = f"https://www.googleapis.com/drive/v3/files?q={query}&key={API_KEY}&fields=files(id,name)"
    response = requests.get(url)
    data = response.json()
    gambar_map = {}

    if 'files' in data:
        for f in data['files']:
            nama = f['name'].lower().replace(' ', '_')
            gambar_map[nama] = f"https://drive.google.com/uc?id={f['id']}"
    return gambar_map

# --- Fungsi bantu untuk mencocokkan gambar ke nama barang ---
def cari_gambar_dari_map(nama_barang, gambar_map):
    nama_file = nama_barang.lower().replace(' ', '_')
    for key in gambar_map:
        if key.startswith(nama_file):  # Cek awalan
            return gambar_map[key]
    return ''

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
                background-color: Skyblue; color: white; padding: 6px 12px;
                text-decoration: none; border-radius: 4px; font-weight: 500;
            }
            .menu-link:hover, .menu-link.active { background-color: skyblue; }

            table {
                table-layout: fixed;
                width: 100%;
                word-wrap: break-word;
                font-size: 0.75rem;
            }
            th, td {
                word-break: break-word;
                white-space: normal;
                padding: 6px !important;
                text-align: center;
                vertical-align: middle;
            }
            table thead th {
                background-color: #d2e3fc;
                color: #000;
                font-weight: bold;
                cursor: pointer;
            }
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
                    <button class="btn btn-sm btn-secondary" onclick="resetLog()">Reset</button>
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

            function resetLog() {
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

            const sortStates = { id: 'default', stock: 'default' };

            document.addEventListener('click', function (e) {
                const table = document.querySelector('#stok-barang table');
                const rows = Array.from(table.tBodies[0].rows);
                let colIndex = -1;

                if (e.target.id === 'sort-id') {
                    colIndex = 0;
                    const key = 'id';
                    toggleSort(rows, colIndex, key);
                }

                if (e.target.id === 'sort-stock') {
                    colIndex = Array.from(table.tHead.rows[0].cells).findIndex(cell => cell.textContent.includes('Stock Barang'));
                    const key = 'stock';
                    toggleSort(rows, colIndex, key);
                }
            });

            function toggleSort(rows, colIndex, key) {
                const tbody = document.querySelector('#stok-barang table tbody');

                if (sortStates[key] === 'default' || sortStates[key] === 'desc') {
                    rows.sort((a, b) => Number(a.cells[colIndex].textContent) - Number(b.cells[colIndex].textContent));
                    sortStates[key] = 'asc';
                } else {
                    rows.sort((a, b) => Number(b.cells[colIndex].textContent) - Number(a.cells[colIndex].textContent));
                    sortStates[key] = 'desc';
                }

                tbody.innerHTML = '';
                rows.forEach(row => tbody.appendChild(row));
            }

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
        df.columns = ['ID', 'Nama Barang', 'Stock Barang', 'Harga Beli', 'Harga Jual Umum', 'Harga Jual Reseller', 'Gambar']

        # Ambil semua gambar hanya sekali
        gambar_map = ambil_semua_gambar_dari_folder()

        # Tambahkan kolom Gambar (URL gambar) ke dataframe, tapi tidak ditampilkan di HTML
        df['Gambar'] = df['Nama Barang'].apply(lambda nama: cari_gambar_dari_map(nama, gambar_map) or '')

        # Ubah Nama Barang jadi hyperlink jika ada gambar
        df['Nama Barang'] = df.apply(
            lambda row: (
                f"<a href='{row['Gambar']}' target='_blank'>{row['Nama Barang']}</a>"
                if row['Gambar'] else row['Nama Barang']
            ), axis=1
        )

        # Drop kolom Gambar dari tampilan HTML (tapi tetap ada di df jika dibutuhkan)
        df_to_show = df.drop(columns=['Gambar'])

        # Konversi ke HTML
        html = df_to_show.to_html(classes='table table-bordered table-sm text-center w-100', index=False, border=0, escape=False)
        html = html.replace('<th>ID</th>', '<th id="sort-id" style="cursor:pointer;">ID</th>')
        html = html.replace('<th>Stock Barang</th>', '<th id="sort-stock" style="cursor:pointer;">Stock Barang</th>')

        return html

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
        {df.to_html(classes='table table-bordered table-sm text-center w-100', index=False, border=0)}
        '''
        return table_html
    except Exception as e:
        return f"<div class='alert alert-danger'>Gagal memuat log penjualan: {e}</div>"

if __name__ == '__main__':
    app.run(debug=True, port=5050)
