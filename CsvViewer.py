from flask import Flask, render_template_string, request, jsonify
import pandas as pd
import requests
from io import StringIO

app = Flask(__name__)

CSV_FILE_ID = '1aDVgRz6BEVb20armjOhwUE0Lyq0Q8zFB'
CSV_URL = f"https://drive.google.com/uc?id={CSV_FILE_ID}&export=download"

CSV_KARYAWAN_FILE_ID = '1r1clq7vLPdMw5nQ0fto4zLBbrhnbnoZ-'
CSV_KARYAWAN_URL = f"https://drive.google.com/uc?id={CSV_KARYAWAN_FILE_ID}&export=download"

FOTO_FOLDER_ID = '1SsQPURPWZ-FzfIJOZWFumY5XTBrNEQiO'
API_KEY = 'AIzaSyDszO0AB7zcrqeMasdB0lCCzqAUfMxn9xk'


def get_drive_image_url(nama_file):
    query = f"name='{nama_file}.jpg' and '{FOTO_FOLDER_ID}' in parents"
    url = f"https://www.googleapis.com/drive/v3/files?q={query}&key={API_KEY}&fields=files(id,name)"
    response = requests.get(url)
    if response.ok:
        files = response.json().get('files')
        if files:
            file_id = files[0]['id']
            return f"https://drive.google.com/uc?id={file_id}"
    return None


@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Parkir & Karyawan</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <style>
            body {
                padding-bottom: 50px;
            }
            .menu-bar button {
    flex: 1;
    min-width: 120px;
    white-space: nowrap;
}
@media (max-width: 400px) {
    .menu-bar {
        flex-direction: column;
        align-items: stretch;
    }
}
            
            .menu-bar button {
                background-color: white;
                color: #007bff;
                border: none;
                padding: 6px 16px;
                border-radius: 5px;
                font-weight: bold;
                transition: background 0.3s;
            }
            .menu-bar button:hover {
                background-color: #e6e6e6;
            }
            th, td { text-align: center; vertical-align: middle; }
            .table-responsive { overflow-x: auto; }
            @media (max-width: 576px) {
                h2 { font-size: 1.5rem; }
                .form-group label { font-size: 0.9rem; }
                .btn { width: 100%; margin-bottom: 10px; }
                .menu-bar { flex-direction: column; }
            }
        </style>
    </head>
    <body>
        <div class="container mt-4 mb-4">
           <div class="d-flex flex-column align-items-start mb-3">
    <h2 class="mb-2">Data Parkir</h2>
    <div class="menu-bar w-100 justify-content-start">
        <button onclick="toggleFilter()">Filter Data</button>
        <button onclick="toggleKaryawan()">Tabel Karyawan</button>
    </div>
</div>

            <form method="get" class="mb-4" id="filter-form" style="display: none;">
                <div class="form-row">
                    <div class="form-group col-sm-6">
                        <label>Dari Tanggal</label>
                        <input type="date" name="tgl_mulai" class="form-control" value="{{ request.args.get('tgl_mulai', '') }}">
                    </div>
                    <div class="form-group col-sm-6">
                        <label>Sampai Tanggal</label>
                        <input type="date" name="tgl_akhir" class="form-control" value="{{ request.args.get('tgl_akhir', '') }}">
                    </div>
                    <div class="form-group col-sm-6">
                        <label>Jenis Kendaraan</label>
                        <select name="kendaraan_jenis" class="form-control">
                            <option value="semua">Semua</option>
                            <option value="mobil" {% if request.args.get('kendaraan_jenis') == 'mobil' %}selected{% endif %}>Mobil</option>
                            <option value="motor" {% if request.args.get('kendaraan_jenis') == 'motor' %}selected{% endif %}>Motor</option>
                        </select>
                    </div>
                    <div class="form-group col-sm-6">
                        <label>Jenis Parkir</label>
                        <select name="keterangan" class="form-control">
                            <option value="semua">Semua</option>
                            <option value="parkir umum" {% if request.args.get('keterangan') == 'parkir umum' %}selected{% endif %}>Parkir Umum</option>
                            <option value="parkir khusus" {% if request.args.get('keterangan') == 'parkir khusus' %}selected{% endif %}>Parkir Khusus</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="col-sm-4 mb-2">
                        <button type="submit" class="btn btn-primary btn-block">Terapkan Filter</button>
                    </div>
                    <div class="col-sm-4 mb-2">
                        <button type="submit" name="hitung" value="1" class="btn btn-success btn-block">Hitung Total Tarif</button>
                    </div>
                    <div class="col-sm-4 mb-2">
                        <a href="/" class="btn btn-secondary btn-block">Reset Filter</a>
                    </div>
                </div>
            </form>

            <div id="tabel-karyawan" class="table-responsive mb-4"></div>
            <div id="total-tarif" class="mb-3"></div>
            <div class="table-responsive mb-5" id="tabel-parkir"></div>
        </div>

        <script>
            function loadTableData() {
                const params = new URLSearchParams(window.location.search);
                fetch('/data?' + params.toString())
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('tabel-parkir').innerHTML = data.table;
                        if (data.total_tarif !== '') {
                            document.getElementById('total-tarif').innerHTML =
                                `<div class="alert alert-info text-center"><strong>Total Tarif:</strong> ${data.total_tarif}</div>`;
                        } else {
                            document.getElementById('total-tarif').innerHTML = '';
                        }
                    });
            }

            function toggleKaryawan() {
                const div = document.getElementById('tabel-karyawan');
                if (div.innerHTML.trim() === '') {
                    fetch('/data_karyawan')
                        .then(response => response.text())
                        .then(html => {
                            document.getElementById('filter-form').style.display = 'none';
                            div.innerHTML = html;
                        });
                } else {
                    div.innerHTML = '';
                }
            }

            function toggleFilter() {
                const form = document.getElementById('filter-form');
                if (form.style.display === 'none' || form.style.display === '') {
                    form.style.display = 'block';
                    document.getElementById('tabel-karyawan').innerHTML = '';
                } else {
                    form.style.display = 'none';
                }
            }

            loadTableData();
            setInterval(loadTableData, 10000);
        </script>
    </body>
    </html>
    ''')


@app.route('/data')
def get_table_ajax():
    try:
        response = requests.get(CSV_URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.content.decode('utf-8'))).fillna('')
        df = df.rename(columns={'JamMasuk': 'Jam Masuk', 'JamKeluar': 'Jam Keluar'})

        tgl_mulai = request.args.get('tgl_mulai')
        tgl_akhir = request.args.get('tgl_akhir')
        kendaraan_jenis = request.args.get('kendaraan_jenis')
        jenis_parkir = request.args.get('keterangan')

        df['Jam Masuk'] = pd.to_datetime(df['Jam Masuk'], errors='coerce')

        if tgl_mulai:
            df = df[df['Jam Masuk'] >= pd.to_datetime(tgl_mulai)]
        if tgl_akhir:
            df = df[df['Jam Masuk'] <= pd.to_datetime(tgl_akhir)]
        if kendaraan_jenis and kendaraan_jenis.lower() != 'semua':
            df = df[df['Kendaraan'].str.lower() == kendaraan_jenis.lower()]
        if jenis_parkir and jenis_parkir.lower() != 'semua':
            df = df[df['Keterangan'].str.lower() == jenis_parkir.lower()]

        def kendaraan_link(row):
            kendaraan = row['Kendaraan']
            if row['Keterangan'].lower().strip() == 'parkir khusus':
                img_url = get_drive_image_url(kendaraan)
                if img_url:
                    return f'<a href="{img_url}" target="_blank">{kendaraan}</a>'
            return kendaraan

        df['Kendaraan'] = df.apply(kendaraan_link, axis=1)

        total_tarif = ''
        if request.args.get('hitung'):
            try:
                total_tarif = df['Tarif'].astype(float).sum()
            except:
                total_tarif = 'Tidak valid'

        df = df[['Nomor', 'Jam Masuk', 'Jam Keluar', 'Kendaraan', 'Tarif', 'Keterangan']]
        table_html = df.to_html(classes='table table-bordered text-center table-sm', escape=False, index=False)
        return jsonify({'table': table_html, 'total_tarif': total_tarif})

    except Exception as e:
        return jsonify({'table': f"<div class='alert alert-danger'>Error: {e}</div>", 'total_tarif': ''})


@app.route('/data_karyawan')
def get_karyawan_data():
    try:
        response = requests.get(CSV_KARYAWAN_URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.content.decode('utf-8'))).fillna('')
        table_html = df.to_html(classes='table table-bordered text-center table-sm', escape=False, index=False)
        return table_html
    except Exception as e:
        return f"<div class='alert alert-danger'>Gagal memuat data karyawan: {e}</div>"


if __name__ == '__main__':
    app.run(debug=True, port=5050)