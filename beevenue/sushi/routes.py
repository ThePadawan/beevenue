from io import BytesIO

from flask import Blueprint, current_app

from sashimmie import sashimmie

from ..core.model.file_upload import upload_file
from ..core.model import thumbnails

from .. import permissions

from .viewmodels import this_import_schema

bp = Blueprint("sushi", __name__)


class HelperBytesIO(BytesIO):
    def save(self, p):
        """
        Helper to enable BytesIO to save itself to a path.
        """
        with open(p, "wb") as out_file:
            out_file.write(self.read())


@bp.route("/sushi/next", methods=["POST"])
@permissions.is_owner
def run():
    saved = sashimmie.get_saved(current_app.config)
    response_dict = {"status": "done", "newIds": []}

    for id, files in saved:
        print(f"Submission {id} consists of {len(files)} files")
        for file_tuple in files:
            stream = HelperBytesIO(file_tuple[1])
            stream.filename = file_tuple[2]
            success, medium_result = upload_file(stream)

            sashimmie.acknowledge(id)
            response_dict["status"] = "continue"

            if success:
                newIds = response_dict["newIds"]
                newIds.append(medium_result.id)
                response_dict["newIds"] = newIds

                status = thumbnails.create(medium_result.id)
                if status == 400:
                    return "", 400

        return this_import_schema.dump(response_dict), 200
    else:
        return this_import_schema.dump(response_dict), 200
