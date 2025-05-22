from flask import Flask, render_template_string, request, jsonify
import pandas as pd
import requests
from io import StringIO

app = Flask(__name__)

# File CSV dan Foto
CSV_FILE_ID = '1aDVgRz6BEVb20armjOhwUE0Lyq0Q8zFB'
CSV_KARYAWAN_FILE_ID = '1r1clq7vLPdMw5nQ0fto4zLBbrhnbnoZ-'
FOTO_FOLDER_ID = '1SsQPURPWZ-FzfIJOZWFumY5XTBrNEQiO'
API_KEY = 'AIzaSyDszO0AB7zcrqeMasdB0lCCzqAUfMxn9xk'

CSV_URL = f"https://drive.google.com/uc?id={CSV_FILE_ID}&export=download"
CSV_KARYAWAN_URL = f"https://drive.google.com/uc?id={CSV_KARYAWAN_FILE_ID}&export=download"

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
            th, td { text-align: center; vertical-align: middle; word-break: break-word; }
            .table-responsive { overflow-x: auto; }
            @media (max-width: 576px) {
                h2 { font-size: 1.5rem; }
                .form-group label { font-size: 0.9rem; }
                .btn { width: 100%; margin-bottom: 10px; }
                .table { font-size: 0.8rem; }
            }
        </style>
    </head>
    <body>
        <div class="container mt-4 mb-4">
            <h2>Data Parkir</h2>
            <form method="get" class="mb-4">
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
                    <div class="col-sm-3 mb-2">
                        <button type="submit" class="btn btn-primary btn-block">Terapkan Filter</button>
                    </div>
                    <div class="col-sm-3 mb-2">
                        <button type="submit" name="hitung" value="1" class="btn btn-success btn-block">Hitung Total Tarif</button>
                    </div>
                    <div class="col-sm-3 mb-2">
                        <a href="/" class="btn btn-secondary btn-block">Reset Filter</a>
                    </div>
                    <div class="col-sm-3 mb-2">
                        <button id="btn-karyawan" type="button" class="btn btn-info btn-block">Tampil Tabel Karyawan</button>
                    </div>
                </div>
            </form>

            <div id="tabel-karyawan" class="mb-4" style="display: none;"></div>
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
                    document.getElementById('total-tarif').innerHTML =
                        data.total_tarif !== '' ?
                        `<div class="alert alert-info text-center"><strong>Total Tarif:</strong> ${data.total_tarif}</div>` : '';
                });
        }

        function toggleKaryawanTable() {
            const container = document.getElementById('tabel-karyawan');
            if (container.style.display === 'none') {
                fetch('/data_karyawan')
                    .then(response => response.text())
                    .then(html => {
                        container.innerHTML = html;
                        container.style.display = 'block';
                    });
            } else {
                container.style.display = 'none';
                container.innerHTML = '';
            }
        }

        document.getElementById('btn-karyawan').addEventListener('click', toggleKaryawanTable);
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
        table_html = f'''
        <div class="table-responsive">
            {df.to_html(classes='table table-bordered text-center', escape=False, index=False)}
        </div>
        '''
        return jsonify({'table': table_html, 'total_tarif': total_tarif})

    except Exception as e:
        return jsonify({'table': f"<div class='alert alert-danger'>Error: {e}</div>", 'total_tarif': ''})

@app.route('/data_karyawan')
def get_karyawan_data():
    try:
        response = requests.get(CSV_KARYAWAN_URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.content.decode('utf-8'))).fillna('')
        table_html = f'''
        <div class="table-responsive">
            {df.to_html(classes='table table-bordered text-center', escape=False, index=False)}
        </div>
        '''
        return table_html
    except Exception as e:
        return f"<div class='alert alert-danger'>Gagal memuat data karyawan: {e}</div>"

if __name__ == '__main__':
    app.run(debug=True, port=5050)