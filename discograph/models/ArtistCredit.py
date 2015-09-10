import mongoengine
from discograph import Bootstrapper
from discograph.models.ArtistRole import ArtistRole
from discograph.models.Model import Model


class ArtistCredit(Model, mongoengine.EmbeddedDocument):

    ### MONGOENGINE FIELDS ###

    anv = mongoengine.StringField()
    name = mongoengine.StringField()
    discogs_id = mongoengine.IntField()
    join = mongoengine.StringField()
    roles = mongoengine.EmbeddedDocumentListField('ArtistRole')
    tracks = mongoengine.StringField()

    ### PUBLIC METHODS ###

    @classmethod
    def from_element(cls, element):
        data = cls.tags_to_fields(element)
        document = cls(**data)
        return document

    ### PUBLIC PROPERTIES ###

    @property
    def artist(self):
        from discograph import models
        return models.Artist.objects.get(discogs_id=self.discogs_id)


ArtistCredit._tags_to_fields_mapping = {
    'anv': ('anv', Bootstrapper.element_to_string),
    'id': ('discogs_id', Bootstrapper.element_to_integer),
    'join': ('join', Bootstrapper.element_to_string),
    'name': ('name', Bootstrapper.element_to_string),
    'role': ('roles', ArtistRole.from_element),
    'tracks': ('tracks', Bootstrapper.element_to_string),
    }