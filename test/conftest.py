import os
import tempfile
import pytest
import sqlite3
import shutil

from beevenue.beevenue import get_application

# Ignore warning that SQLite + DECIMAL sucks.
import warnings
from sqlalchemy.exc import SAWarning
warnings.filterwarnings(
    'ignore',
    r"^Dialect sqlite\+pysqlite does \*not\* support Decimal objects "
    r"natively\, and SQLAlchemy must convert from floating point - "
    r"rounding errors and other issues may occur\. Please consider "
    r"storing Decimal numbers as strings or integers on this platform "
    r"for lossless storage\.$",
    SAWarning)


def _resource(fname):
    return os.path.join(
        os.path.join(
            os.path.dirname(__file__),
            'resources'),
        fname)


def _medium_file(fname):
    return os.path.join(
        os.path.dirname(__file__),
        'media',
        fname)


def _run_testing_sql(temp_path):
    with open(_resource('testing.sql'), 'rb') as f:
        TESTING_SQL = f.read().decode('utf-8')

    escaped_temp_path = temp_path.replace('\\', "\\\\")
    conn = sqlite3.connect(escaped_temp_path)
    conn.executescript(TESTING_SQL)
    conn.commit()
    conn.close()


def _ensure_folder(fname):
    files_path = os.path.join(os.path.dirname(__file__), fname)
    if not os.path.exists(files_path):
        os.mkdir(files_path)


def _client(extra=None):
    temp_fd, temp_path = tempfile.mkstemp(suffix=".db")
    print(f"Temp path: {temp_path}")
    temp_nice_path = os.path.abspath(temp_path)
    connection_string = f'sqlite:///{temp_nice_path}'
    print(f"connection_string: {connection_string}")

    def extra_config(application):
        application.config['SQLALCHEMY_DATABASE_URI'] = connection_string
        application.config['TESTING'] = True

    app = get_application(extra_config)

    _run_testing_sql(temp_nice_path)
    # TODO: Create actual hashes and files described in testing.sql
    # so we can test file access, update, upload, thumbnail creation etc.
    _ensure_folder('media')
    _ensure_folder('thumbs')

    shutil.copy(_resource("placeholder.jpg"), _medium_file('hash1.jpg'))
    shutil.copy(_resource("placeholder.jpg"), _medium_file('hash2.jpg'))
    shutil.copy(_resource("placeholder.jpg"), _medium_file('hash3.jpg'))

    c = app.test_client()

    if extra:
        extra(c)

    yield c

    # TODO: Remove testing media when done with them (doesn't work?)
    # _ensure_no_more_folder('files') # use shutil.rmtree

    os.close(temp_fd)
    os.unlink(temp_path)


@pytest.yield_fixture
def client():
    for c in _client():
        return c


@pytest.yield_fixture
def adminClient():
    def loginAsAdmin(c):
        res = c.post('/login', json={
            'username': 'admin',
            'password': 'admin'})
        assert res.status_code == 200

    for c in _client(loginAsAdmin):
        return c


@pytest.yield_fixture
def adminNsfwClient():
    def loginAsNsfwAdmin(c):
        res = c.post('/login', json={
            'username': 'admin',
            'password': 'admin'})
        assert res.status_code == 200

        res = c.patch('/sfw', json={
            'sfwSession': False
        })
        assert res.status_code == 200

    for c in _client(loginAsNsfwAdmin):
        return c


@pytest.yield_fixture
def userClient():
    def loginAsUser(c):
        res = c.post('/login', json={
            'username': 'user',
            'password': 'user'})
        assert res.status_code == 200

    for c in _client(loginAsUser):
        return c
