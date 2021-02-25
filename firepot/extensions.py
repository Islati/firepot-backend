from flask_cors import CORS
from flask_hashing import Hashing
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
hashing = Hashing()
cors = CORS()
migrate = Migrate()
