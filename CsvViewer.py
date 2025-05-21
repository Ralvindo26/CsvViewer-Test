from flask import Flask, render_template_string
import pandas as pd
import requests
from io import StringIO

app = Flask(__name__)

CSV_FILE_ID = '1aDVgRz6BEVb20armjOhwUE0Lyq0Q8zFB'
CSV_URL = f"https://drive.google.com/uc?id={CSV_FILE_ID}&export=download"

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
def show_csv():
    try:
        response = requests.get(CSV_URL)
        response.raise_for_status()
        csv_content = response.content.decode('utf-8')
        df = pd.read_csv(StringIO(csv_content)).fillna('')

        df = df.rename(columns={
            'JamMasuk': 'Jam Masuk',
            'JamKeluar': 'Jam Keluar'
        })

        def kendaraan_link(row):
            kendaraan = row['Kendaraan']
            if row['Keterangan'].lower().strip() == 'parkir khusus':
                img_url = get_drive_image_url(kendaraan)
                if img_url:
                    return f'<a href="{img_url}" target="_blank">{kendaraan}</a>'
            return kendaraan

        df['Kendaraan'] = df.apply(kendaraan_link, axis=1)

        df = df[['Nomor', 'Jam Masuk', 'Jam Keluar', 'Kendaraan', 'Tarif', 'Keterangan']]
        table_html = df.to_html(classes='table table-bordered text-center', escape=False, index=False)

        return render_template_string('''
            <html>
            <head>
                <title>Data Parkir</title>
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
                <style>
                    th { text-align: center; vertical-align: middle; }
                </style>
            </head>
            <body>
                <div class="container mt-5">
                    <h2 class="mb-4">Data Parkir</h2>
                    {{table|safe}}
                </div>
            </body>
            </html>
        ''', table=table_html)

    except Exception as e:
        return f"Terjadi error: {e}"

if __name__ == '__main__':
    app.run(debug=True, port=5050)
