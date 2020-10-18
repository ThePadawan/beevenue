from marshmallow import EXCLUDE, fields, Schema

from ..schemas import requires_json_body


class _LoginParamsSchema(Schema):
    class Meta:
        """Exclude all other fields not listed here."""

        unknown = EXCLUDE

    username = fields.String(required=True)
    password = fields.String(required=True)


login_params_schema = requires_json_body(_LoginParamsSchema())


class _SfwModeSchema(Schema):
    sfwSession = fields.Boolean(required=True)


sfw_mode_schema = requires_json_body(_SfwModeSchema())
