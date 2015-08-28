import math
from abjad import documentationtools
from discograph import models


# TODO: add all aliases within same degree (they should have relative degree 0)
# TODO: match discogs id against name and degree (use dict, not set).


class ArtistMembershipGrapher(object):

    ### INITIALIZER ###

    def __init__(self, artists, degree=3):
        assert len(artists)
        assert all(isinstance(_, models.Artist) for _ in artists)
        assert 0 < int(degree)
        self.artists = tuple(artists)
        self.degree = int(degree)

    ### SPECIAL METHODS ###

    def __graph__(self):
        nodes, edges = self.analyze()
        artist_id_to_node_mapping = {}
        cluster_id_to_cluster_mapping = {}
        graphviz_graph = documentationtools.GraphvizGraph(
            attributes=dict(
                bgcolor='transparent',
                fontname='Arial',
                output_order='edgesfirst',
                overlap='prism',
                penwidth=2,
                sep='+10',
                esep='+10',
                splines='spline',
                style=('bold', 'filled', 'rounded'),
                truecolor=True,
                ),
            edge_attributes=dict(
                penwidth=2,
                ),
            node_attributes=dict(
                colorscheme='rdylbu9',
                penwidth=2,
                ),
            )
        for node in nodes:
            (
                artist_id,
                artist_name,
                cluster_id,
                distance,
                member_count,
                ) = node

            if not member_count:
                fontname = 'Arial'
                shape = 'box'
                style = ('bold', 'filled', 'rounded')
            else:
                fontname = 'Arial Bold'
                shape = 'circle'
                style = ('bold', 'filled')
            node = documentationtools.GraphvizNode(
                name='node{}'.format(artist_id),
                attributes=dict(
                    fillcolor=distance + 1,
                    fontname=fontname,
                    label=r'\n'.join(artist_name.split()),
                    shape=shape,
                    style=style,
                    ),
                )
            artist_id_to_node_mapping[artist_id] = node
            if cluster_id is not None:
                if cluster_id not in cluster_id_to_cluster_mapping:
                    cluster = documentationtools.GraphvizSubgraph(
                        is_cluster=False,
                        name='alias{}'.format(cluster_id)
                        )
                    cluster_id_to_cluster_mapping[cluster_id] = cluster
                    graphviz_graph.append(cluster)
                cluster = cluster_id_to_cluster_mapping[cluster_id]
                cluster.append(node)
            else:
                graphviz_graph.append(node)
        for head_id, tail_id, role in edges:
            head_node = artist_id_to_node_mapping[head_id]
            tail_node = artist_id_to_node_mapping[tail_id]
            if role == 'Alias':
                attributes = {
                    'dir': 'none',
                    'style': 'dotted',
                    }
            else:
                attributes = {}
            edge = documentationtools.GraphvizEdge(attributes=attributes)
            edge.attach(head_node, tail_node)
        root_node_names = ['node{}'.format(_.discogs_id) for _ in self.artists]
        for node in graphviz_graph:
            edge_count_weighting = len(node.edges)
            edge_count_weighting = math.sqrt(edge_count_weighting)
            node.attributes['fontsize'] = 12 + edge_count_weighting
            if node.name in root_node_names:
                node.attributes['fillcolor'] = 'black'
                node.attributes['fontcolor'] = 'white'
                node.attributes['fontsize'] = 20
        return graphviz_graph

    ### PUBLIC METHODS ###

    def analyze(self, max_nodes=None):
        template = (
            'DEGREE {}: {} artists, '
            '{} edges, '
            '{} clusters'
            )
        cluster_count = 0
        clusters = {}
        edges = set()
        artist_aliases = dict()
        artist_ids_visited = dict()
        artist_ids_to_visit = set(_.discogs_id for _ in self.artists)
        for distance in range(self.degree + 1):
            if max_nodes and max_nodes <= len(artist_ids_visited):
                break
            current_artist_ids_to_visit = list(artist_ids_to_visit)
            artist_ids_to_visit.clear()
            while current_artist_ids_to_visit:
                if max_nodes and max_nodes <= len(artist_ids_visited):
                    break
                artist_id = current_artist_ids_to_visit.pop()
                if artist_id in artist_ids_visited:
                    continue
                artist = models.Artist.objects.get(discogs_id=artist_id)
                aliases = []
                for alias in artist.aliases:
                    alias_query = models.Artist.objects(name=alias)
                    if not alias_query.count():
                        continue
                    aliases.append(alias_query.first())
                artist_aliases[artist.discogs_id] = aliases
                if len(aliases) and artist_id not in clusters:
                    cluster_count += 1
                    clusters[artist_id] = cluster_count
                for alias in aliases:
                    if alias.discogs_id not in artist_ids_visited:
                        current_artist_ids_to_visit.append(alias.discogs_id)
                        edge = sorted([artist.discogs_id, alias.discogs_id])
                        edge.append('Alias')
                        edge = tuple(edge)
                        edges.add(edge)
                    clusters[alias.discogs_id] = cluster_count
                for group in artist.groups:
                    if distance < self.degree:
                        artist_ids_to_visit.add(group.discogs_id)
                        edge = (
                            artist.discogs_id,
                            group.discogs_id,
                            'Member Of',
                            )
                        edges.add(edge)
                for member in artist.members:
                    if distance < self.degree:
                        artist_ids_to_visit.add(member.discogs_id)
                        edge = (
                            member.discogs_id,
                            artist.discogs_id,
                            'Member Of',
                            )
                        edges.add(edge)
                value = (distance, artist)
                artist_ids_visited[artist_id] = value
            message = template.format(
                distance,
                len(artist_ids_visited),
                len(edges),
                cluster_count,
                )
            print(message)
        edges = [_ for _ in edges
            if _[0] in artist_ids_visited and
            _[1] in artist_ids_visited
            ]
        nodes = []
        for artist_id, (distance, artist) in artist_ids_visited.items():
            is_missing_edges = False
            for group in artist.groups:
                if group.discogs_id not in artist_ids_visited:
                    is_missing_edges = True
            for member in artist.members:
                if member.discogs_id not in artist_ids_visited:
                    is_missing_edges = True
            for alias in artist_aliases[artist.discogs_id]:
                if alias.discogs_id not in artist_ids_visited:
                    is_missing_edges = True
            node = [
                artist.discogs_id,
                artist.name,
                clusters.get(artist_id, None),
                distance,
                len(artist.members),
                is_missing_edges,
                ]
            nodes.append(node)
        return nodes, sorted(edges)

    def to_json(self, max_nodes=None):
        nodes, edges = self.analyze(max_nodes=max_nodes)
        data = {
            'center': [_.discogs_id for _ in self.artists],
            'nodes': [],
            'links': [],
            }
        for node in nodes:
            (
                artist_id,
                artist_name,
                cluster_id,
                distance,
                size,
                is_missing_edges,
                ) = node
            node = {
                'id': artist_id,
                'name': artist_name,
                'group': cluster_id,
                'distance': distance,
                'size': size,
                'incomplete': is_missing_edges,
                }
            data['nodes'].append(node)
        for edge in edges:
            (
                head_id,
                tail_id,
                role,
                ) = edge
            if role == 'Alias':
                dotted = True
            else:
                dotted = False
            link = {
                'dotted': dotted,
                'source': tail_id,
                'target': head_id,
                }
            data['links'].append(link)
        return data