import os
import tempfile
import pytest
import sqlite3

from beevenue.beevenue import get_application

TESTING_SQL = ''
with open(os.path.join(os.path.dirname(__file__), 'testing.sql'), 'rb') as f:
    TESTING_SQL = f.read().decode('utf-8')


@pytest.fixture
def client():
    temp_fd, temp_path = tempfile.mkstemp(suffix=".db")
    print(f"Temp path: {temp_path}")
    temp_nice_path = os.path.abspath(temp_path)
    connection_string = f'sqlite:///{temp_nice_path}'
    print(f"connection_string: {connection_string}")


    def extra_config(application):
        application.config['SQLALCHEMY_DATABASE_URI'] = connection_string
        application.config['TESTING'] = True

    app = get_application(extra_config)

    # escaped_temp_path = temp_nice_path.replace('\\', "\\\\")
    # conn = sqlite3.connect(escaped_temp_path)
    # conn.executescript(TESTING_SQL)
    # conn.commit()
    # conn.close()

    client = app.test_client()

    yield client

    os.close(temp_fd)
    os.unlink(temp_path)
