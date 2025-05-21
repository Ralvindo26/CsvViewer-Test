from flask import Flask, render_template_string
import pandas as pd
import requests
from io import StringIO

app = Flask(__name__)

FILE_ID = '1aDVgRz6BEVb20armjOhwUE0Lyq0Q8zFB'
CSV_URL = f"https://drive.google.com/uc?id={FILE_ID}&export=download"

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
        df = df[['Nomor', 'Jam Masuk', 'Jam Keluar', 'Kendaraan', 'Tarif', 'Keterangan']]

        table_html = df.to_html(classes='table table-bordered text-center', index=False)

        return render_template_string('''
            <html>
            <head>
                <title>Data Parkir</title>
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
                <style>
                    th {
                        text-align: center;
                        vertical-align: middle;
                    }
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
    