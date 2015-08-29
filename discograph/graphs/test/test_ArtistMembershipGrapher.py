import discograph

import unittest


class Test(unittest.TestCase):

    def setUp(self):
        self.client = discograph.connect()

    def tearDown(self):
        self.client.close()

    def test_1(self):
        artist = discograph.models.Artist.objects.get(name='Morris Day')
        grapher = discograph.graphs.ArtistMembershipGrapher
        neighborhood = grapher.get_neighborhood(artist)
        assert neighborhood == {
            'aliases': (),
            'edges': (
                (152882, 32550, 'Member Of'),
                (152882, 2561672, 'Member Of'),
                ),
            'id': 152882,
            'name': 'Morris Day',
            'nodes': (
                {'id': 32550, 'name': 'Time, The'},
                {'id': 2561672, 'name': 'Original 7ven, The'},
                ),
            'size': 0,
            }

    def test_2(self):
        artist = discograph.models.Artist.objects.get(name='Time, The')
        grapher = discograph.graphs.ArtistMembershipGrapher
        neighborhood = grapher.get_neighborhood(artist)
        assert neighborhood == {
            'aliases': (2561672,),
            'edges': (
                (23446, 32550, 'Member Of'),
                (32550, 2561672, 'Alias'),
                (37806, 32550, 'Member Of'),
                (53261, 32550, 'Member Of'),
                (55449, 32550, 'Member Of'),
                (100600, 32550, 'Member Of'),
                (113965, 32550, 'Member Of'),
                (152882, 32550, 'Member Of'),
                (241356, 32550, 'Member Of'),
                (354129, 32550, 'Member Of'),
                (409502, 32550, 'Member Of'),
                (453969, 32550, 'Member Of')
                ),
            'id': 32550,
            'name': 'Time, The',
            'nodes': (
                {'id': 23446, 'name': "Alexander O'Neal"},
                {'id': 37806, 'name': 'Jesse Johnson'},
                {'id': 53261, 'name': 'St. Paul'},
                {'id': 55449, 'name': 'Terry Lewis'},
                {'id': 100600, 'name': 'Monte Moir'},
                {'id': 113965, 'name': 'Jellybean Johnson'},
                {'id': 152882, 'name': 'Morris Day'},
                {'id': 241356, 'name': 'James Harris III'},
                {'id': 354129, 'name': 'Jerome Benton'},
                {'id': 409502, 'name': 'Mark Cardenas'},
                {'id': 453969, 'name': 'Jerry Hubbard'},
                {'id': 2561672, 'name': 'Original 7ven, The'},
                ),
            'size': 11,
            }

    def test_3(self):
        artist = discograph.models.Artist.objects.get(name='Morris Day')
        grapher = discograph.graphs.ArtistMembershipGrapher([artist], 1)
        network = grapher.get_network()
        assert network == {
            'center': [152882],
            'links': (
                {'role': 'Alias', 'source': 32550, 'target': 2561672},
                {'role': 'Member Of', 'source': 152882, 'target': 32550},
                {'role': 'Member Of', 'source': 152882, 'target': 2561672},
                ),
            'nodes': (
                {'distance': 1, 'group': 1, 'id': 32550, 'incomplete': True, 'name': 'Time, The', 'size': 11},
                {'distance': 0, 'group': None, 'id': 152882, 'incomplete': False, 'name': 'Morris Day', 'size': 0},
                {'distance': 1, 'group': 1, 'id': 2561672, 'incomplete': True, 'name': 'Original 7ven, The', 'size': 7},
                ),
            }

    def test_4(self):
        artist = discograph.models.Artist.objects.get(name='Morris Day')
        grapher = discograph.graphs.ArtistMembershipGrapher([artist], 2)
        network = grapher.get_network()
        assert network == {
            'center': [152882],
            'links': (
                {'role': 'Member Of', 'source': 23446, 'target': 32550},
                {'role': 'Alias', 'source': 32550, 'target': 2561672},
                {'role': 'Member Of', 'source': 37806, 'target': 32550},
                {'role': 'Member Of', 'source': 37806, 'target': 2561672},
                {'role': 'Member Of', 'source': 53261, 'target': 32550},
                {'role': 'Member Of', 'source': 55449, 'target': 32550},
                {'role': 'Member Of', 'source': 55449, 'target': 2561672},
                {'role': 'Member Of', 'source': 100600, 'target': 32550},
                {'role': 'Member Of', 'source': 100600, 'target': 2561672},
                {'role': 'Member Of', 'source': 113965, 'target': 32550},
                {'role': 'Member Of', 'source': 113965, 'target': 2561672},
                {'role': 'Member Of', 'source': 152882, 'target': 32550},
                {'role': 'Member Of', 'source': 152882, 'target': 2561672},
                {'role': 'Member Of', 'source': 241356, 'target': 32550},
                {'role': 'Member Of', 'source': 241356, 'target': 2561672},
                {'role': 'Member Of', 'source': 354129, 'target': 32550},
                {'role': 'Member Of', 'source': 354129, 'target': 2561672},
                {'role': 'Member Of', 'source': 409502, 'target': 32550},
                {'role': 'Member Of', 'source': 453969, 'target': 32550},
                ),
            'nodes': (
                {'distance': 2, 'group': None, 'id': 23446, 'incomplete': True, 'name': "Alexander O'Neal", 'size': 0},
                {'distance': 1, 'group': 1, 'id': 32550, 'incomplete': False, 'name': 'Time, The', 'size': 11},
                {'distance': 2, 'group': None, 'id': 37806, 'incomplete': True, 'name': 'Jesse Johnson', 'size': 0},
                {'distance': 2, 'group': 2, 'id': 53261, 'incomplete': True, 'name': 'St. Paul', 'size': 0},
                {'distance': 2, 'group': None, 'id': 55449, 'incomplete': True, 'name': 'Terry Lewis', 'size': 0},
                {'distance': 2, 'group': None, 'id': 100600, 'incomplete': True, 'name': 'Monte Moir', 'size': 0},
                {'distance': 2, 'group': None, 'id': 113965, 'incomplete': True, 'name': 'Jellybean Johnson', 'size': 0},
                {'distance': 0, 'group': None, 'id': 152882, 'incomplete': False, 'name': 'Morris Day', 'size': 0},
                {'distance': 2, 'group': 3, 'id': 241356, 'incomplete': True, 'name': 'James Harris III', 'size': 0},
                {'distance': 2, 'group': None, 'id': 354129, 'incomplete': True, 'name': 'Jerome Benton', 'size': 0},
                {'distance': 2, 'group': None, 'id': 409502, 'incomplete': True, 'name': 'Mark Cardenas', 'size': 0},
                {'distance': 2, 'group': None, 'id': 453969, 'incomplete': True, 'name': 'Jerry Hubbard', 'size': 0},
                {'distance': 1, 'group': 1, 'id': 2561672, 'incomplete': False, 'name': 'Original 7ven, The', 'size': 7},
                ),
            }

    def test_5(self):
        artist = discograph.models.Artist.objects.get(name='Morris Day')
        grapher = discograph.graphs.ArtistMembershipGrapher(
            [artist], degree=3, max_nodes=5)
        network = grapher.get_network()
        assert network == {
            'center': [152882],
            'links': (
                {'role': 'Alias', 'source': 32550, 'target': 2561672},
                {'role': 'Member Of', 'source': 55449, 'target': 32550},
                {'role': 'Member Of', 'source': 55449, 'target': 2561672},
                {'role': 'Member Of', 'source': 152882, 'target': 32550},
                {'role': 'Member Of', 'source': 152882, 'target': 2561672},
                {'role': 'Member Of', 'source': 409502, 'target': 32550},
                ),
            'nodes': (
                {'distance': 1, 'group': 1, 'id': 32550, 'incomplete': True, 'name': 'Time, The', 'size': 11},
                {'distance': 2, 'group': None, 'id': 55449, 'incomplete': True, 'name': 'Terry Lewis', 'size': 0},
                {'distance': 0, 'group': None, 'id': 152882, 'incomplete': False, 'name': 'Morris Day', 'size': 0},
                {'distance': 2, 'group': None, 'id': 409502, 'incomplete': True, 'name': 'Mark Cardenas', 'size': 0},
                {'distance': 1, 'group': 1, 'id': 2561672, 'incomplete': True, 'name': 'Original 7ven, The', 'size': 7},
                ),
            }