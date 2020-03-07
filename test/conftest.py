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
    "ignore",
    r"^Dialect sqlite\+pysqlite does \*not\* support Decimal objects "
    r"natively\, and SQLAlchemy must convert from floating point - "
    r"rounding errors and other issues may occur\. Please consider "
    r"storing Decimal numbers as strings or integers on this platform "
    r"for lossless storage\.$",
    SAWarning,
)


def _resource(fname):
    return os.path.join(
        os.path.join(os.path.dirname(__file__), "resources"), fname
    )


def _file(folder, fname):
    return os.path.join(os.path.dirname(__file__), "..", folder, fname)


def _thumbs_file(fname):
    return _file("thumbs", fname)


def _medium_file(fname):
    return _file("media", fname)


def _run_testing_sql(temp_path):
    with open(_resource("testing.sql"), "rb") as f:
        TESTING_SQL = f.read().decode("utf-8")

    escaped_temp_path = temp_path.replace("\\", "\\\\")
    conn = sqlite3.connect(escaped_temp_path)
    conn.executescript(TESTING_SQL)
    conn.commit()
    conn.close()


def _ensure_folder(fname):
    files_path = os.path.join(os.path.dirname(__file__), "..", fname)
    if not os.path.exists(files_path):
        os.mkdir(files_path)

    files_path = os.path.join(os.path.dirname(__file__), fname)
    if not os.path.exists(files_path):
        os.mkdir(files_path)


def _ensure_no_more_folder(fname):
    files_path = os.path.join(os.path.dirname(__file__), fname)
    if os.path.exists(files_path):
        shutil.rmtree(files_path)


RAN_ONCE = False


def _client():
    global RAN_ONCE
    temp_fd, temp_path = tempfile.mkstemp(suffix=".db")
    temp_nice_path = os.path.abspath(temp_path)
    connection_string = f"sqlite:///{temp_nice_path}"

    def extra_config(application):
        application.config["SQLALCHEMY_DATABASE_URI"] = connection_string
        application.config["TESTING"] = True

    def fill_db():
        _run_testing_sql(temp_nice_path)

    app = get_application(extra_config, fill_db)

    if not RAN_ONCE:
        _ensure_folder("media")
        _ensure_folder("thumbs")

        # TODO Don't do this, use CLI import instead. For that, find some actually distinct pictures.
        shutil.copy(_resource("placeholder.jpg"), _medium_file("hash1.jpg"))
        shutil.copy(_resource("placeholder.jpg"), _medium_file("hash2.jpg"))
        shutil.copy(_resource("placeholder.jpg"), _medium_file("hash3.jpg"))
        shutil.copy(_resource("placeholder.jpg"), _medium_file("hash4.jpg"))
        shutil.copy(_resource("placeholder.jpg"), _medium_file("hash5.jpg"))

        shutil.copy(_resource("placeholder.jpg"), _thumbs_file("hash1.s.jpg"))
        shutil.copy(_resource("placeholder.jpg"), _thumbs_file("hash1.l.jpg"))
        shutil.copy(_resource("placeholder.jpg"), _thumbs_file("hash2.s.jpg"))
        shutil.copy(_resource("placeholder.jpg"), _thumbs_file("hash2.l.jpg"))
        shutil.copy(_resource("placeholder.jpg"), _thumbs_file("hash3.s.jpg"))
        shutil.copy(_resource("placeholder.jpg"), _thumbs_file("hash3.l.jpg"))
        shutil.copy(_resource("placeholder.jpg"), _thumbs_file("hash4.s.jpg"))
        shutil.copy(_resource("placeholder.jpg"), _thumbs_file("hash4.l.jpg"))
        shutil.copy(_resource("placeholder.jpg"), _thumbs_file("hash5.s.jpg"))
        shutil.copy(_resource("placeholder.jpg"), _thumbs_file("hash5.l.jpg"))

    # Some tests ruin this file by overwriting it. So we restore it when we're done.
    with open(_resource("testing_rules.json"), "r") as rules_file:
        rules_file_contents = rules_file.read()

    c = app.test_client()
    c.app_under_test = app

    # Example code to run some arbitrary SQL query - e.g. to set
    # currently hardcoded constants like "what's the Id of the video medium"
    # dynamically:
    #
    # escaped_temp_path = temp_nice_path.replace("\\", "\\\\")
    # conn = sqlite3.connect(escaped_temp_path)
    # cur = conn.cursor()
    # cur.execute("SELECT * FROM medium")
    # rows = cur.fetchall()
    # c._rows = rows

    # conn.close()

    yield c

    with open(_resource("testing_rules.json"), "w") as rules_file:
        rules_file.write(rules_file_contents)

    os.close(temp_fd)
    os.unlink(temp_path)
    RAN_ONCE = True


@pytest.yield_fixture
def client():
    for c in _client():
        yield c


@pytest.yield_fixture
def nsfw(client):
    res = client.patch("/sfw", json={"sfwSession": False})
    assert res.status_code == 200
    return None


@pytest.yield_fixture
def asAdmin(client):
    res = client.post("/login", json={"username": "admin", "password": "admin"})
    assert res.status_code == 200


@pytest.yield_fixture
def withVideo(client):
    runner = client.app_under_test.test_cli_runner()
    runner.invoke(args=["import", _resource("tiny_video.mp4")])
    yield None


@pytest.yield_fixture
def asUser(client):
    res = client.post("/login", json={"username": "user", "password": "user"})
    assert res.status_code == 200
