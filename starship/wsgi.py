if __name__ == "__main__":
    from dotenv import load_dotenv

    import os
    import starship
    import pyruvate

    load_dotenv()

    SERVER_FALLBACK_PORT = 80
    SERVER_PORT = os.getenv("SERVER_PORT", SERVER_FALLBACK_PORT)
    WORKERS = 2

    pyruvate.serve(starship.make_app(), f"0.0.0.0:{SERVER_PORT}", WORKERS)
