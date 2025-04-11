import os
import pandas as pd
from flask import Flask, request, render_template_string, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

HTML_TEMPLATE = '''
<!doctype html>
<html>
<head>
  <title>Dividir Excel - FOR Human Capital</title>
  {{ style_block|safe }}
</head>
<body>
  <div class="container">
    <h2>Subir archivo Excel (.xlsx)</h2>
    <form method=post enctype=multipart/form-data class="file-upload">
      <input type=file name=file accept=".xlsx">
      <button type=submit>Subir y dividir</button>
    </form>

    {% if filename %}
      <h3>Archivo subido: {{ filename }}</h3>
      <h4>Archivos divididos:</h4>
      <ul>
        {% for part in parts %}
          <li><a class="btn-ver" href="{{ url_for('download_file', filename=part) }}">Descargar {{ part }}</a></li>
        {% endfor %}
      </ul>
    {% endif %}
  </div>
</body>
</html>
'''

STYLE_BLOCK = """
<style>
body {
    background: url('https://forhumancapital.mx/wp-content/uploads/2025/04/8.png') no-repeat center center fixed;
    background-size: cover;
    color: #FFFFFF;
    font-family: 'Segoe UI', Arial, sans-serif;
    margin: 0;
    padding: 0;
}
.container {
    max-width: 450px;
    margin: 80px auto;
    background-color: #1F1F1F;
    padding: 40px 30px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}
ul {
    padding-left: 0;
    list-style: none;
}
ul li {
    margin: 10px 0;
}
a.btn-ver {
    display: inline-block;
    padding: 6px 12px;
    background-color: #1E90FF;
    color: #fff;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
    transition: background-color 0.3s, transform 0.2s;
}
a.btn-ver:hover {
    background-color: #00BFFF;
    transform: scale(1.05);
}
input[type="file"] {
    border: 1px solid #FFFFFF;
    border-radius: 10px;
    padding: 6px 10px;
    background-color: #2A2A2A;
    color: #FFFFFF;
    cursor: pointer;
}
button {
    padding: 12px;
    border: none;
    border-radius: 12px;
    background-color: #1E90FF;
    color: #fff;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s, transform 0.2s;
}
button:hover {
    background-color: #00BFFF;
    transform: scale(1.02);
}
</style>
"""

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    parts = []
    filename = None

    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            df = pd.read_excel(filepath)
            total_rows = len(df)
            chunks = [df.iloc[i:i + 50] for i in range(0, total_rows, 50)]

            # Limpia archivos anteriores
            for f in os.listdir(app.config['UPLOAD_FOLDER']):
                if f.startswith("parte_") and f.endswith(".xlsx"):
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))

            for idx, chunk in enumerate(chunks):
                part_filename = f'parte_{idx + 1}.xlsx'
                part_path = os.path.join(app.config['UPLOAD_FOLDER'], part_filename)
                chunk.to_excel(part_path, index=False)
                parts.append(part_filename)

    return render_template_string(HTML_TEMPLATE, filename=filename, parts=parts, style_block=STYLE_BLOCK)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
