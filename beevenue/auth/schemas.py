
from marshmallow import fields, Schema, EXCLUDE


class LoginParamsSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.String(required=True)
    password = fields.String(required=True)


login_params_schema = LoginParamsSchema()


class SfwModeSchema(Schema):
    sfwSession = fields.Boolean(required=True)


sfw_mode_schema = SfwModeSchema()
