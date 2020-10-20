DEBUG = True
TESTING = True

SQLALCHEMY_DATABASE_URI = "POTATO"  # is being set at initialization time
SQLALCHEMY_TRACK_MODIFICATIONS = False

COMMIT_ID = "TESTING"
SENTRY_DSN = "https://examplePublicKey@o0.ingest.sentry.io/0"

BEEVENUE_STORAGE = "./test"

BEEVENUE_ALLOWED_CORS_ORIGINS = ["http://localhost:*"]

BEEVENUE_THUMBNAIL_SIZES = {"s": 240, "l": 600}
BEEVENUE_TINY_THUMBNAIL_SIZE = 8
BEEVENUE_MINIMUM_ASPECT_RATIO = 0.5

BEEVENUE_RULES_FILE = "test/resources/testing_rules.json"

SECRET_KEY = "TESTING_ONLY"

CACHE_DIR = "./test-cache"
