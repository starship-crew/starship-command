import os
from flask import Flask
from db import connector


app = Flask(__name__)

if __name__ == "__main__":
    import pyruvate

    from dotenv import load_dotenv

    load_dotenv()

    SERVER_FALLBACK_PORT = 80
    SERVER_PORT = os.getenv("SERVER_PORT", SERVER_FALLBACK_PORT)
    WORKERS = 2

    pyruvate.serve(app, f"0.0.0.0:{SERVER_PORT}", WORKERS)
