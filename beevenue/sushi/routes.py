from io import BytesIO

from flask import Blueprint, current_app, request

from sashimmie import sashimmie

from ..core.model.file_upload import upload_file
from ..core.model import thumbnails

from ..decorators import requires_permission
from .. import permissions

from .viewmodels import this_import_schema

bp = Blueprint('sushi', __name__)


class HelperBytesIO(BytesIO):
    def save(self, p):
        """
        Helper to enable BytesIO to save itself to a path.
        """
        with open(p, "wb") as out_file:
            out_file.write(self.read())


@bp.route('/sushi/next', methods=["POST"])
@requires_permission(permissions.is_owner)
def run():
    saved = sashimmie.get_saved(current_app.config)

    result_dict = {"status": "done", "newIds": []}

    for id, files in saved:
        session = request.beevenue_context.session()

        print(f"Submission {id} consists of {len(files)} files")
        for file_tuple in files:
            stream = HelperBytesIO(file_tuple[1])
            stream.filename = file_tuple[2]
            success, result = upload_file(session, stream)

            sashimmie.acknowledge(id)
            result_dict["status"] = "continue"

            if success:
                newIds = result_dict["newIds"]
                newIds.append(result.id)
                result_dict["newIds"] = newIds

                maybe_aspect_ratio = thumbnails.create(result.mime_type, result.hash)
                if not maybe_aspect_ratio:
                    return '', 400

                result.aspect_ratio = maybe_aspect_ratio
                session.commit()

        return this_import_schema.dump(result_dict), 200
    else:
        return this_import_schema.dump(result_dict), 200
