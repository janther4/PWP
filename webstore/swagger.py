from flask import Blueprint, send_file, current_app, jsonify, render_template_string
from pathlib import Path

bp = Blueprint("swagger", __name__, url_prefix="")

SWAGGER_UI_HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Webstore API docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css" />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
    <script>
      const ui = SwaggerUIBundle({
        url: '/openapi.json',
        dom_id: '#swagger-ui',
      })
    </script>
  </body>
  </html>
"""


@bp.route('/openapi.json')
def openapi():
    p = Path(current_app.root_path) / 'openapi.json'
    if p.exists():
        return send_file(str(p), mimetype='application/json')
    return jsonify({}), 404


@bp.route('/docs/')
def docs():
    return render_template_string(SWAGGER_UI_HTML)
