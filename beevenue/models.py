from .beevenue import db


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(length=256), unique=True, nullable=False)

    def __init__(self, tag):
        self.tag = tag
        self.rating = 'u'


MediaTags = db.Table('medium_tag', db.metadata,
    db.Column('medium_id', db.Integer, db.ForeignKey('medium.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)


class Medium(db.Model):
    __tablename__ = 'medium'
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(length=32), unique=True, nullable=False)
    mime_type = db.Column(db.String(length=256), nullable=False)
    aspect_ratio = db.Column(db.Numeric(precision=4, scale=2), nullable=True)
    rating = db.Column(db.Enum('e', 's', 'q', 'u', name="Rating"), nullable=False)

    tags = db.relationship(
        'Tag',
        secondary=MediaTags,
        lazy='joined',
        backref=db.backref('media', lazy="joined"))

    def __init__(self, hash, mime_type, rating='u', tags=[], aspect_ratio=None):
        self.rating = rating
        self.mime_type = mime_type
        self.hash = hash
        self.tags = tags
        self.aspect_ratio = aspect_ratio
