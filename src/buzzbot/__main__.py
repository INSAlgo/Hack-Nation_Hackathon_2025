# This allows running 'python -m src.buzzbot' or 'python -m buzzbot' if PYTHONPATH=src
from .webserver import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
