import os

from flask import Flask, request, render_template_string, redirect, url_for
import boto3
from botocore.exceptions import ClientError


S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

app = Flask(__name__)


def get_s3_client():
  return boto3.client("s3", region_name=AWS_REGION)


@app.route("/")
def index():
  return render_template_string(
    """
    <h1>Flask + S3 Demo</h1>
    <p>Bucket S3 utilisé : <strong>{{ bucket }}</strong></p>
    <p>
      <a href="{{ url_for('list_files') }}">Voir les fichiers</a>
    </p>
    <h2>Upload d'un fichier</h2>
    <form action="{{ url_for('upload_file') }}" method="post" enctype="multipart/form-data">
      <input type="file" name="file" required>
      <button type="submit">Uploader</button>
    </form>
    """,
    bucket=S3_BUCKET_NAME,
  )


@app.route("/files")
def list_files():
  s3 = get_s3_client()
  objects = []
  try:
    response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)
    for obj in response.get("Contents", []):
      objects.append(obj["Key"])
  except ClientError as e:
    return f"Erreur lors de la lecture du bucket S3: {e}", 500

  return render_template_string(
    """
    <h1>Fichiers dans le bucket {{ bucket }}</h1>
    <ul>
    {% for key in objects %}
      <li>{{ key }}</li>
    {% else %}
      <li>Aucun fichier</li>
    {% endfor %}
    </ul>
    <p><a href="{{ url_for('index') }}">Retour</a></p>
    """,
    bucket=S3_BUCKET_NAME,
    objects=objects,
  )


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

