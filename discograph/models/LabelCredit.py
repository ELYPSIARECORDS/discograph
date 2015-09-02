import mongoengine
from discograph.models.Model import Model


class LabelCredit(Model, mongoengine.EmbeddedDocument):

    ### MONGOENGINE FIELDS ###

    catalog_number = mongoengine.StringField()
    discogs_id = mongoengine.IntField()
    name = mongoengine.StringField()

    ### PUBLIC METHODS ###

    @classmethod
    def from_element(cls, element):
        catalog_number = element.attrib.get('catno', None) or None
        name = element.attrib.get('name')
        document = cls(catalog_number=catalog_number, name=name)
        return document