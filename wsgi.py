from app import create_app
from app.settings import DEBUG, PROJECT_PORT

app = create_app()

if __name__ == "__main__":
    app.run(port=PROJECT_PORT, debug=DEBUG)
