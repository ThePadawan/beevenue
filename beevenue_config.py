DEBUG = True

SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost:5432/beevenue'
SQLALCHEMY_TRACK_MODIFICATIONS = False

BEEVENUE_ALLOWED_CORS_ORIGINS = ['http://localhost:*']

BEEVENUE_THUMBNAIL_SIZES = {
    's': 240,
    'l': 600
}

SENTRY_DSN = "CHANGE-ME_LATER"

SECRET_KEY = "CHANGE-ME_LATER"

def GET_RULES():
    return []
