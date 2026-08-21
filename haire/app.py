import os
import sys

# Ensure haire/ root is in Python path when executed from Hackathon/ folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from routes.upload_rank import upload_bp
from routes.view_routes import view_bp

app = Flask(__name__)

app.register_blueprint(upload_bp)
app.register_blueprint(view_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)