import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:renoshan15@localhost:5432/casc_oil_spill"
)

APP_NAME = "CASC Oil Spill Attribution API"
APP_VERSION = "1.0.0"