import itertools
import mongoengine
from abjad.tools import datastructuretools
from abjad.tools import systemtools
from discograph.models.Model import Model


class Relation(Model, mongoengine.Document):

    ### CLASS VARIABLES ###

    class EntityType(datastructuretools.Enumeration):
        ARTIST = 1
        LABEL = 2

    ### MONGOENGINE FIELDS ###

    entity_one_id = mongoengine.IntField()
    entity_one_name = mongoengine.StringField()
    entity_one_type = mongoengine.IntField()
    entity_two_id = mongoengine.IntField()
    entity_two_name = mongoengine.StringField()
    entity_two_type = mongoengine.IntField()
    role_name = mongoengine.StringField()
    category = mongoengine.IntField()
    subcategory = mongoengine.IntField(null=True)
    is_trivial = mongoengine.BooleanField()
    release_id = mongoengine.IntField(null=True)
    year = mongoengine.IntField(null=True)

    ### MONOGENGINE META ###

    meta = {
        'indexes': [
            '#entity_one_name',
            '#entity_two_name',
            '#role_name',
            'category',
            'entity_one_id',
            'entity_one_type',
            'entity_two_id',
            'entity_two_type',
            'release_id',
            'subcategory',
            'year',
            ]
        }

    ### PRIVATE METHODS ###

    @classmethod
    def _get_categories(cls, role_name):
        from discograph import models
        categories = models.ArtistRole._available_credit_roles.get(
            role_name, None)
        if not categories:
            return None, None
        if len(categories) == 1:
            return categories[0], None
        return categories

    @classmethod
    def _partition_artists(cls, artists):
        pass

    ### PRIVATE PROPERTIES ###

    @property
    def _storage_format_specification(self):
        from discograph import models
        keyword_argument_names = sorted(self._fields)
        if 'id' in keyword_argument_names:
            keyword_argument_names.remove('id')
        keyword_argument_callables = dict(
            category=models.ArtistRole.Category,
            entity_one_type=self.EntityType,
            entity_two_type=self.EntityType,
            subcategory=models.ArtistRole.Subcategory,
            )
        for keyword_argument_name in keyword_argument_names[:]:
            value = getattr(self, keyword_argument_name)
            if isinstance(value, list) and not value:
                keyword_argument_names.remove(keyword_argument_name)
        return systemtools.StorageFormatSpecification(
            self,
            keyword_argument_names=keyword_argument_names,
            keyword_argument_callables=keyword_argument_callables,
            )

    ### PUBLIC METHODS ###

    def save_if_unique(self):
        query = type(self).objects(
            entity_one_id=self.entity_one_id,
            entity_one_type=self.entity_one_type,
            entity_two_id=self.entity_two_id,
            entity_two_type=self.entity_two_type,
            role_name=self.role_name,
            category=self.category,
            subcategory=self.subcategory,
            release_id=self.release_id,
            year=self.year,
            )
        if not query.count():
            print('    {!r} : {} : {!r}'.format(
                self.entity_one_name, self.role_name, self.entity_two_name)
                )
            self.save()

    @classmethod
    def bootstrap(cls):
        from discograph import models
        #cls.drop_collection()
        #for artist in models.Artist.objects:
        #    print(artist.discogs_id, artist.name)
        #    for relation in cls.from_artist(artist):
        #        relation.save_if_unique()
        #for label in models.Label.objects:
        #    print(label.discogs_id, label.name)
        #    for relation in cls.from_label(label):
        #        relation.save_if_unique()
        for release in models.Release.objects:
            print(release.discogs_id, release.title)
            for relation in cls.from_release(release):
                relation.save_if_unique()

    @classmethod
    def from_artist(cls, artist):
        from discograph import models
        relations = []
        role_name = 'Alias'
        assert role_name in models.ArtistRole._available_credit_roles
        category, subcategory = cls._get_categories(role_name)
        for alias in artist.aliases:
            query = models.Artist.objects(name=alias)
            query = query.hint([('name', 'hashed')])
            if not query.count():
                continue
            alias = query.first()
            artist_one, artist_two = sorted(
                [artist, alias],
                key=lambda x: x.discogs_id,
                )
            relation = dict(
                entity_one_id=artist_one.discogs_id,
                entity_one_name=artist_one.name,
                entity_one_type=cls.EntityType.ARTIST,
                entity_two_id=artist_two.discogs_id,
                entity_two_name=artist_two.name,
                entity_two_type=cls.EntityType.ARTIST,
                role_name=role_name,
                category=category,
                subcategory=subcategory,
                )
            relations.append(relation)
        role_name = 'Member Of'
        assert role_name in models.ArtistRole._available_credit_roles
        category, subcategory = cls._get_categories(role_name)
        for member in artist.members:
            relation = dict(
                entity_one_id=member.discogs_id,
                entity_one_name=member.name,
                entity_one_type=cls.EntityType.ARTIST,
                entity_two_id=artist.discogs_id,
                entity_two_name=artist.name,
                entity_two_type=cls.EntityType.ARTIST,
                role_name=role_name,
                category=category,
                subcategory=subcategory,
                )
            relations.append(relation)
        relations = set(tuple(_.items()) for _ in relations)
        relations = [cls(**dict(_)) for _ in relations]
        relations.sort(
            key=lambda x: (x.role_name, x.entity_one_id, x.entity_two_id),
            )
        return relations

    @classmethod
    def from_label(cls, label):
        if not label.discogs_id:
            return []
        triples = set()
        for sublabel in label.sublabels:
            if not sublabel.discogs_id:
                continue
            triples.add((sublabel, label, 'Sublabel Of'))
        key_function = lambda x: (x[0].discogs_id, x[1].discogs_id, x[2])
        triples = sorted(triples, key=key_function)
        relations = cls.from_triples(triples)
        return relations

    @classmethod
    def from_triples(cls, triples, release=None):
        from discograph import models
        relations = []
        release_id, year = None, None
        if release is not None:
            release_id = release.discogs_id
            if release.release_date is not None:
                year = release.release_date.year
        for entity_one, entity_two, role_name in triples:
            entity_one_type = cls.EntityType.ARTIST
            if isinstance(entity_one, models.Label):
                entity_one_type = cls.EntityType.LABEL
            entity_two_type = cls.EntityType.ARTIST
            if isinstance(entity_two, models.Label):
                entity_two_type = cls.EntityType.LABEL
            category, subcategory = cls._get_categories(role_name)
            is_trivial = None
            if entity_one_type == entity_two_type == cls.EntityType.ARTIST:
                if entity_one.discogs_id == entity_two.discogs_id:
                    is_trivial = True
                elif entity_one in entity_two.members:
                    is_trivial = True
                elif entity_one.name in entity_two.aliases:
                    is_trivial = True
                elif entity_two.name in entity_one.aliases:
                    is_trivial = True
            relation = cls(
                category=category,
                entity_one_id=entity_one.discogs_id,
                entity_one_name=entity_one.name,
                entity_one_type=entity_one_type,
                entity_two_id=entity_two.discogs_id,
                entity_two_name=entity_two.name,
                entity_two_type=entity_two_type,
                release_id=release_id,
                role_name=role_name,
                subcategory=subcategory,
                year=year,
                is_trivial=is_trivial,
                )
            relations.append(relation)
        return relations

    @classmethod
    def from_release(cls, release):
        artists = set(credit.artist for credit in release.artists)
        if len(artists) == 1 and list(artists)[0].name == 'Various':
            artists.clear()
            for track in release.tracklist:
                artists.update(credit.artist for credit in track.artists)
        labels = set(_.label for _ in release.labels)
        triples = set()
        for artist, label in itertools.product(artists, labels):
            triples.add((artist, label, 'Released On'))
        key_function = lambda x: (x[0].discogs_id, x[1].discogs_id, x[2])
        triples = sorted(triples, key=key_function)
        relations = cls.from_triples(triples, release=release)
        return relations