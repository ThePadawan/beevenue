from io import BytesIO


class HelperBytesIO(BytesIO):
    filename: str

    def save(self, p: str) -> None:
        """
        Helper to enable BytesIO to save itself to a path.
        """
        with open(p, "wb") as out_file:
            out_file.write(self.read())
