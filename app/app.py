import os
import mimetypes

from flask import Flask, request, render_template_string, redirect, url_for, Response
import boto3
from botocore.exceptions import ClientError


S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

app = Flask(__name__)


def get_s3_client():
  return boto3.client("s3", region_name=AWS_REGION)


BASE_CSS = """
<style>
  * { box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    margin: 0;
    min-height: 100vh;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: #e8e8e8;
    padding: 2rem;
    line-height: 1.5;
  }
  .container { max-width: 560px; margin: 0 auto; }
  h1 {
    font-size: 1.75rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #fff;
  }
  .subtitle { color: #94a3b8; font-size: 0.95rem; margin-bottom: 1.5rem; }
  .card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
  }
  .card h2 {
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0 0 1rem 0;
    color: #cbd5e1;
  }
  .bucket-name { font-family: monospace; color: #7dd3fc; font-size: 0.9rem; }
  a {
    color: #38bdf8;
    text-decoration: none;
  }
  a:hover { text-decoration: underline; }
  .btn {
    display: inline-block;
    padding: 0.6rem 1.2rem;
    background: #0ea5e9;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    margin-top: 0.75rem;
  }
  .btn:hover { background: #0284c7; }
  .btn-link {
    background: transparent;
    color: #38bdf8;
    padding: 0.5rem 0;
  }
  .btn-link:hover { background: transparent; text-decoration: underline; }
  input[type="file"] {
    display: block;
    margin: 0.5rem 0 0 0;
    color: #cbd5e1;
    font-size: 0.9rem;
  }
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  .file-item {
    padding: 0.75rem;
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    margin-bottom: 0.6rem;
  }
  .file-item .name { font-family: monospace; font-size: 0.9rem; color: #cbd5e1; }
  .file-item img {
    max-width: 100%;
    max-height: 280px;
    border-radius: 6px;
    margin-top: 0.5rem;
    display: block;
  }
  .file-item a.view-link { font-size: 0.9rem; margin-top: 0.4rem; display: inline-block; }
  .back { margin-top: 1.25rem; }
</style>
"""


@app.route("/")
def index():
  return render_template_string(
    BASE_CSS
    + """
    <div class="container">
      <h1>Flask + S3</h1>
      <p class="subtitle">Upload et liste des fichiers dans le bucket</p>
      <div class="card">
        <p>Bucket utilisé : <span class="bucket-name">{{ bucket }}</span></p>
        <a href="{{ url_for('list_files') }}">Voir les fichiers</a>
      </div>
      <div class="card">
        <h2>Upload d'un fichier</h2>
        <form action="{{ url_for('upload_file') }}" method="post" enctype="multipart/form-data">
          <input type="file" name="file" required>
          <button type="submit" class="btn">Envoyer</button>
        </form>
      </div>
    </div>
    """,
    bucket=S3_BUCKET_NAME,
  )


def is_image_key(key):
  ext = key.lower().split(".")[-1] if "." in key else ""
  return ext in ("jpg", "jpeg", "png", "gif", "webp", "bmp", "svg")


@app.route("/files")
def list_files():
  s3 = get_s3_client()
  files = []
  try:
    response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)
    for obj in response.get("Contents", []):
      key = obj["Key"]
      files.append({"key": key, "is_image": is_image_key(key)})
  except ClientError as e:
    return f"Erreur lors de la lecture du bucket S3: {e}", 500

  return render_template_string(
    BASE_CSS
    + """
    <div class="container">
      <h1>Fichiers dans le bucket</h1>
      <p class="subtitle">{{ bucket }}</p>
      <div class="card">
        <h2>Objets stockés</h2>
        <ul>
        {% for f in files %}
          <li class="file-item">
            <span class="name">{{ f.key }}</span>
            {% if f.is_image %}
              <img src="{{ url_for('get_file', key=f.key) }}" alt="{{ f.key }}">
            {% endif %}
            <a href="{{ url_for('get_file', key=f.key) }}" target="_blank" class="view-link">Ouvrir / Télécharger</a>
          </li>
        {% else %}
          <li class="file-item">Aucun fichier pour l'instant.</li>
        {% endfor %}
        </ul>
        <p class="back"><a href="{{ url_for('index') }}" class="btn btn-link">← Retour</a></p>
      </div>
    </div>
    """,
    bucket=S3_BUCKET_NAME,
    files=files,
  )


@app.route("/file/<path:key>")
def get_file(key: str):
  s3 = get_s3_client()
  try:
    obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=key)
    data = obj["Body"].read()
    content_type = obj.get("ContentType") or mimetypes.guess_type(key)[0] or "application/octet-stream"
    return Response(data, mimetype=content_type)
  except ClientError as e:
    return f"Erreur lors de la récupération du fichier: {e}", 500


@app.route("/upload", methods=["POST"])
def upload_file():
  if "file" not in request.files:
    return "Aucun fichier dans la requête", 400

  file = request.files["file"]
  if file.filename == "":
    return "Nom de fichier vide", 400

  s3 = get_s3_client()
  try:
    s3.upload_fileobj(file, S3_BUCKET_NAME, file.filename)
  except ClientError as e:
    return f"Erreur lors de l'upload vers S3: {e}", 500

  return redirect(url_for("list_files"))


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=80)

