import os
from flask import Flask

def create_app():
    app = Flask(__name__)

    # Set upload folder and max upload size (200 MB)
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB
    app.secret_key = "supersecretkey"

    from .routes import main
    app.register_blueprint(main)

    return app
