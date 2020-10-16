from marshmallow import EXCLUDE, fields, Schema

from ..schemas import requires_json_body


class LoginParamsSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.String(required=True)
    password = fields.String(required=True)


login_params_schema = requires_json_body(LoginParamsSchema())


class SfwModeSchema(Schema):
    sfwSession = fields.Boolean(required=True)


sfw_mode_schema = requires_json_body(SfwModeSchema())
