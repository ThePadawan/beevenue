from .db import db


TagImplication = db.Table('tagImplication', db.metadata,
    db.Column('implying_tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('implied_tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(length=256), unique=True, nullable=False)

    aliases = db.relationship(
        'TagAlias',
        lazy='joined')

    implying_this = db.relationship(
        'Tag',
        secondary=TagImplication,
        primaryjoin=id==TagImplication.c.implied_tag_id,
        secondaryjoin=id==TagImplication.c.implying_tag_id,
        lazy='joined')

    implied_by_this = db.relationship(
        'Tag',
        secondary=TagImplication,
        primaryjoin=id==TagImplication.c.implying_tag_id,
        secondaryjoin=id==TagImplication.c.implied_tag_id,
        lazy='joined')

    def __init__(self, tag):
        self.tag = tag
        self.rating = 'u'

    @staticmethod
    def create(tag):
        clean_tag = tag.strip()
        if clean_tag:
            return Tag(clean_tag)
        else:
            return None


class TagAlias(db.Model):
    __tablename__ = 'tagAlias'
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)
    alias = db.Column(db.String(length=256), unique=True, nullable=False)

    tag = db.relationship(Tag, lazy='joined')

    def __init__(self, tag_id, alias):
        self.tag_id = tag_id
        self.alias = alias


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
