from firepot.config import Config
from firepot.factory import create_app

application = create_app(Config(), testing=False)

if __name__ == "__main__":
    application.run()