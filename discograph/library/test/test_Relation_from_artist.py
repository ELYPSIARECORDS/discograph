# -*- encoding: utf-8 -*-
import mongoengine
import unittest
from abjad.tools import stringtools
from discograph.library.Bootstrapper import Bootstrapper
from discograph import library


class Test(unittest.TestCase):

    database_name = 'discograph:test'

    def setUp(self):
        self.database = mongoengine.connect(self.database_name)

    def tearDown(self):
        self.database.drop_database(self.database_name)
        self.database.close()

    def test_01(self):
        iterator = Bootstrapper.get_iterator('artist')
        artist_element = next(iterator)
        artist_element = next(iterator)
        artist_document = library.Artist.from_element(artist_element)
        for discogs_id, member in enumerate(artist_document.members, 200000000):
            name = member.name
            library.Artist(discogs_id=discogs_id, name=name).save()
        for discogs_id, alias in enumerate(artist_document.aliases, 100000000):
            name = alias.name
            library.Artist(discogs_id=discogs_id, name=name).save()
        artist_document.resolve_references()
        artist_document.save()
        artist_document.reload()
        relations = library.Relation.from_artist(artist_document)
        actual = '\n'.join(format(_) for _ in relations)
        expected = stringtools.normalize(r'''
            discograph.library.Relation(
                category=discograph.library.ArtistRole.Category.RELATION,
                entity_one_id=2,
                entity_one_name='Mr. James Barth & A.D.',
                entity_one_type=discograph.library.Relation.EntityType.ARTIST,
                entity_two_id=100000000,
                entity_two_name='ADCL',
                entity_two_type=discograph.library.Relation.EntityType.ARTIST,
                role_name='Alias',
                )
            discograph.library.Relation(
                category=discograph.library.ArtistRole.Category.RELATION,
                entity_one_id=2,
                entity_one_name='Mr. James Barth & A.D.',
                entity_one_type=discograph.library.Relation.EntityType.ARTIST,
                entity_two_id=100000001,
                entity_two_name='Alexi Delano & Cari Lekebusch',
                entity_two_type=discograph.library.Relation.EntityType.ARTIST,
                role_name='Alias',
                )
            discograph.library.Relation(
                category=discograph.library.ArtistRole.Category.RELATION,
                entity_one_id=2,
                entity_one_name='Mr. James Barth & A.D.',
                entity_one_type=discograph.library.Relation.EntityType.ARTIST,
                entity_two_id=100000002,
                entity_two_name='Crushed Insect & The Sick Puppy',
                entity_two_type=discograph.library.Relation.EntityType.ARTIST,
                role_name='Alias',
                )
            discograph.library.Relation(
                category=discograph.library.ArtistRole.Category.RELATION,
                entity_one_id=2,
                entity_one_name='Mr. James Barth & A.D.',
                entity_one_type=discograph.library.Relation.EntityType.ARTIST,
                entity_two_id=100000003,
                entity_two_name='Puente Latino',
                entity_two_type=discograph.library.Relation.EntityType.ARTIST,
                role_name='Alias',
                )
            discograph.library.Relation(
                category=discograph.library.ArtistRole.Category.RELATION,
                entity_one_id=2,
                entity_one_name='Mr. James Barth & A.D.',
                entity_one_type=discograph.library.Relation.EntityType.ARTIST,
                entity_two_id=100000004,
                entity_two_name='Yakari & Delano',
                entity_two_type=discograph.library.Relation.EntityType.ARTIST,
                role_name='Alias',
                )
            discograph.library.Relation(
                category=discograph.library.ArtistRole.Category.RELATION,
                entity_one_id=200000000,
                entity_one_name='Alexi Delano',
                entity_one_type=discograph.library.Relation.EntityType.ARTIST,
                entity_two_id=2,
                entity_two_name='Mr. James Barth & A.D.',
                entity_two_type=discograph.library.Relation.EntityType.ARTIST,
                role_name='Member Of',
                )
            discograph.library.Relation(
                category=discograph.library.ArtistRole.Category.RELATION,
                entity_one_id=200000001,
                entity_one_name='Cari Lekebusch',
                entity_one_type=discograph.library.Relation.EntityType.ARTIST,
                entity_two_id=2,
                entity_two_name='Mr. James Barth & A.D.',
                entity_two_type=discograph.library.Relation.EntityType.ARTIST,
                role_name='Member Of',
                )
            ''')
        assert actual == expected