from marshmallow import fields, Schema


class ThisImportSchema(Schema):
    status = fields.String()
    newIds = fields.List(fields.Int)


this_import_schema = ThisImportSchema()
