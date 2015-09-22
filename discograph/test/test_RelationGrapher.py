# -*- coding: utf-8 -*-
import discograph
import unittest


class Test(unittest.TestCase):

    def setUp(self):
        self.client = discograph.connect()

    def tearDown(self):
        self.client.close()

    def test_1(self):
        artist = discograph.models.Artist.objects.get(name='Morris Day')
        grapher = discograph.RelationGrapher
        role_names = ['Alias', 'Member Of']
        neighborhood = grapher.get_neighborhood(artist, role_names=role_names)
        assert neighborhood == {
            'aliases': (),
            'id': 152882,
            'links': (
                {'role': 'Member Of', 'source': ('artist', 152882), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 152882), 'target': ('artist', 2561672)},
                ),
            'name': 'Morris Day',
            'nodes': (
                ('artist', 32550),
                ('artist', 152882),
                ('artist', 2561672),
                ),
            'size': 0,
            'type': 'artist',
            }

    def test_2(self):
        artist = discograph.models.Artist.objects.get(name='Time, The')
        grapher = discograph.RelationGrapher
        role_names = ['Alias', 'Member Of']
        neighborhood = grapher.get_neighborhood(artist, role_names=role_names)
        assert neighborhood == {
            'aliases': (2561672,),
            'id': 32550,
            'links': (
                {'role': 'Alias', 'source': ('artist', 32550), 'target': ('artist', 2561672)},
                {'role': 'Member Of', 'source': ('artist', 23446), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 37806), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 53261), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 55449), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 100600), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 113965), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 152882), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 241356), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 354129), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 409502), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 453969), 'target': ('artist', 32550)},
                ),
            'name': 'Time, The',
            'nodes': (
                ('artist', 23446),
                ('artist', 32550),
                ('artist', 37806),
                ('artist', 53261),
                ('artist', 55449),
                ('artist', 100600),
                ('artist', 113965),
                ('artist', 152882),
                ('artist', 241356),
                ('artist', 354129),
                ('artist', 409502),
                ('artist', 453969),
                ('artist', 2561672),
                ),
            'size': 11,
            'type': 'artist',
            }

    def test_3(self):
        artist = discograph.models.Artist.objects.get(name='Time, The')
        grapher = discograph.RelationGrapher
        role_names = ['Member Of', 'Alias']
        neighborhood = grapher.get_neighborhood(artist, role_names=role_names)
        assert neighborhood == {
            'aliases': (2561672,),
            'id': 32550,
            'links': (
                {'role': 'Alias', 'source': ('artist', 32550), 'target': ('artist', 2561672)},
                {'role': 'Member Of', 'source': ('artist', 23446), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 37806), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 53261), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 55449), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 100600), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 113965), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 152882), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 241356), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 354129), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 409502), 'target': ('artist', 32550)},
                {'role': 'Member Of', 'source': ('artist', 453969), 'target': ('artist', 32550)},
                ),
            'name': 'Time, The',
            'nodes': (
                ('artist', 23446),
                ('artist', 32550),
                ('artist', 37806),
                ('artist', 53261),
                ('artist', 55449),
                ('artist', 100600),
                ('artist', 113965),
                ('artist', 152882),
                ('artist', 241356),
                ('artist', 354129),
                ('artist', 409502),
                ('artist', 453969),
                ('artist', 2561672),
                ),
            'size': 11,
            'type': 'artist',
            }

    def test_4(self):
        artist = discograph.models.Artist.objects.get(name='Morris Day')
        role_names = ['Alias', 'Member Of']
        grapher = discograph.RelationGrapher(
            [artist],
            degree=2,
            role_names=role_names,
            )
        network = grapher.get_network()
        assert network == {
            'center': ('artist-152882',),
            'links': (
                {'key': 'artist-23446-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-23446', 'target': 'artist-32550'},
                {'key': 'artist-32550-alias-artist-2561672', 'role': 'Alias', 'source': 'artist-32550', 'target': 'artist-2561672'},
                {'key': 'artist-37806-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-37806', 'target': 'artist-32550'},
                {'key': 'artist-37806-member-of-artist-2561672', 'role': 'Member Of', 'source': 'artist-37806', 'target': 'artist-2561672'},
                {'key': 'artist-53261-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-53261', 'target': 'artist-32550'},
                {'key': 'artist-55449-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-55449', 'target': 'artist-32550'},
                {'key': 'artist-55449-member-of-artist-2561672', 'role': 'Member Of', 'source': 'artist-55449', 'target': 'artist-2561672'},
                {'key': 'artist-100600-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-100600', 'target': 'artist-32550'},
                {'key': 'artist-100600-member-of-artist-2561672', 'role': 'Member Of', 'source': 'artist-100600', 'target': 'artist-2561672'},
                {'key': 'artist-113965-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-113965', 'target': 'artist-32550'},
                {'key': 'artist-113965-member-of-artist-2561672', 'role': 'Member Of', 'source': 'artist-113965', 'target': 'artist-2561672'},
                {'key': 'artist-152882-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-152882', 'target': 'artist-32550'},
                {'key': 'artist-152882-member-of-artist-2561672', 'role': 'Member Of', 'source': 'artist-152882', 'target': 'artist-2561672'},
                {'key': 'artist-241356-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-241356', 'target': 'artist-32550'},
                {'key': 'artist-241356-member-of-artist-2561672', 'role': 'Member Of', 'source': 'artist-241356', 'target': 'artist-2561672'},
                {'key': 'artist-354129-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-354129', 'target': 'artist-32550'},
                {'key': 'artist-354129-member-of-artist-2561672', 'role': 'Member Of', 'source': 'artist-354129', 'target': 'artist-2561672'},
                {'key': 'artist-409502-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-409502', 'target': 'artist-32550'},
                {'key': 'artist-453969-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-453969', 'target': 'artist-32550'},
                ),
            'nodes': (
                {'distance': 2, 'group': None, 'id': 23446, 'key': 'artist-23446', 'missing': 1, 'name': "Alexander O'Neal", 'size': 0, 'type': 'artist'},
                {'distance': 1, 'group': 1, 'id': 32550, 'key': 'artist-32550', 'missing': 0, 'name': 'Time, The', 'size': 11, 'type': 'artist'},
                {'distance': 2, 'group': None, 'id': 37806, 'key': 'artist-37806', 'missing': 2, 'name': 'Jesse Johnson', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': 2, 'id': 53261, 'key': 'artist-53261', 'missing': 5, 'name': 'St. Paul', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': None, 'id': 55449, 'key': 'artist-55449', 'missing': 3, 'name': 'Terry Lewis', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': None, 'id': 100600, 'key': 'artist-100600', 'missing': 1, 'name': 'Monte Moir', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': None, 'id': 113965, 'key': 'artist-113965', 'missing': 4, 'name': 'Jellybean Johnson', 'size': 0, 'type': 'artist'},
                {'distance': 0, 'group': None, 'id': 152882, 'key': 'artist-152882', 'missing': 0, 'name': 'Morris Day', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': 3, 'id': 241356, 'key': 'artist-241356', 'missing': 4, 'name': 'James Harris III', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': None, 'id': 354129, 'key': 'artist-354129', 'missing': 1, 'name': 'Jerome Benton', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': None, 'id': 409502, 'key': 'artist-409502', 'missing': 1, 'name': 'Mark Cardenas', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': None, 'id': 453969, 'key': 'artist-453969', 'missing': 2, 'name': 'Jerry Hubbard', 'size': 0, 'type': 'artist'},
                {'distance': 1, 'group': 1, 'id': 2561672, 'key': 'artist-2561672', 'missing': 0, 'name': 'Original 7ven, The', 'size': 7, 'type': 'artist'},
                ),
            }

    def test_5(self):
        artist = discograph.models.Artist.objects.get(name='Morris Day')
        role_names = ['Alias', 'Member Of']
        grapher = discograph.RelationGrapher(
            [artist],
            degree=2,
            role_names=role_names,
            )
        network = grapher.get_network()
        assert network == {
            'center': ('artist-152882',),
            'links': (
                {'key': 'artist-23446-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-23446', 'target': 'artist-32550'},
                {'key': 'artist-32550-alias-artist-2561672', 'role': 'Alias', 'source': 'artist-32550', 'target': 'artist-2561672'},
                {'key': 'artist-37806-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-37806', 'target': 'artist-32550'},
                {'key': 'artist-37806-member-of-artist-2561672', 'role': 'Member Of', 'source': 'artist-37806', 'target': 'artist-2561672'},
                {'key': 'artist-53261-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-53261', 'target': 'artist-32550'},
                {'key': 'artist-55449-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-55449', 'target': 'artist-32550'},
                {'key': 'artist-55449-member-of-artist-2561672', 'role': 'Member Of', 'source': 'artist-55449', 'target': 'artist-2561672'},
                {'key': 'artist-100600-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-100600', 'target': 'artist-32550'},
                {'key': 'artist-100600-member-of-artist-2561672', 'role': 'Member Of', 'source': 'artist-100600', 'target': 'artist-2561672'},
                {'key': 'artist-113965-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-113965', 'target': 'artist-32550'},
                {'key': 'artist-113965-member-of-artist-2561672', 'role': 'Member Of', 'source': 'artist-113965', 'target': 'artist-2561672'},
                {'key': 'artist-152882-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-152882', 'target': 'artist-32550'},
                {'key': 'artist-152882-member-of-artist-2561672', 'role': 'Member Of', 'source': 'artist-152882', 'target': 'artist-2561672'},
                {'key': 'artist-241356-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-241356', 'target': 'artist-32550'},
                {'key': 'artist-241356-member-of-artist-2561672', 'role': 'Member Of', 'source': 'artist-241356', 'target': 'artist-2561672'},
                {'key': 'artist-354129-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-354129', 'target': 'artist-32550'},
                {'key': 'artist-354129-member-of-artist-2561672', 'role': 'Member Of', 'source': 'artist-354129', 'target': 'artist-2561672'},
                {'key': 'artist-409502-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-409502', 'target': 'artist-32550'},
                {'key': 'artist-453969-member-of-artist-32550', 'role': 'Member Of', 'source': 'artist-453969', 'target': 'artist-32550'},
                ),
            'nodes': (
                {'distance': 2, 'group': None, 'id': 23446, 'key': 'artist-23446', 'missing': 1, 'name': "Alexander O'Neal", 'size': 0, 'type': 'artist'},
                {'distance': 1, 'group': 1, 'id': 32550, 'key': 'artist-32550', 'missing': 0, 'name': 'Time, The', 'size': 11, 'type': 'artist'},
                {'distance': 2, 'group': None, 'id': 37806, 'key': 'artist-37806', 'missing': 2, 'name': 'Jesse Johnson', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': 2, 'id': 53261, 'key': 'artist-53261', 'missing': 5, 'name': 'St. Paul', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': None, 'id': 55449, 'key': 'artist-55449', 'missing': 3, 'name': 'Terry Lewis', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': None, 'id': 100600, 'key': 'artist-100600', 'missing': 1, 'name': 'Monte Moir', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': None, 'id': 113965, 'key': 'artist-113965', 'missing': 4, 'name': 'Jellybean Johnson', 'size': 0, 'type': 'artist'},
                {'distance': 0, 'group': None, 'id': 152882, 'key': 'artist-152882', 'missing': 0, 'name': 'Morris Day', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': 3, 'id': 241356, 'key': 'artist-241356', 'missing': 4, 'name': 'James Harris III', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': None, 'id': 354129, 'key': 'artist-354129', 'missing': 1, 'name': 'Jerome Benton', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': None, 'id': 409502, 'key': 'artist-409502', 'missing': 1, 'name': 'Mark Cardenas', 'size': 0, 'type': 'artist'},
                {'distance': 2, 'group': None, 'id': 453969, 'key': 'artist-453969', 'missing': 2, 'name': 'Jerry Hubbard', 'size': 0, 'type': 'artist'},
                {'distance': 1, 'group': 1, 'id': 2561672, 'key': 'artist-2561672', 'missing': 0, 'name': 'Original 7ven, The', 'size': 7, 'type': 'artist'},
                ),
            }