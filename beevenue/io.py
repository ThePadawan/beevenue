"""Helper data structures for various use around the project."""
from io import BytesIO
import os


class HelperBytesIO(BytesIO):
    """Helper object that makes a BytesIO behave like a werkzeug FileStorage"""

    filename: str

    def save(self, path: str) -> None:
        """Helper to enable BytesIO to save itself to a path."""
        with open(path, "wb") as out_file:
            out_file.write(self.read())
            out_file.flush()
            os.fsync(out_file.fileno())
