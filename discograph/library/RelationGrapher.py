# -*- encoding: utf-8 -*-
import collections
import re
import six
from discograph.library.Artist import Artist
from discograph.library.ArtistRole import ArtistRole
from discograph.library.Label import Label
from discograph.library.SQLArtist import SQLArtist
from discograph.library.SQLLabel import SQLLabel
from discograph.library.SQLRelation import SQLRelation


class RelationGrapher(object):

    ### CLASS VARIABLES ###

    word_pattern = re.compile('\s+')

    ### INITIALIZER ###

    def __init__(
        self,
        center_entity,
        cache=None,
        degree=3,
        max_nodes=None,
        role_names=None,
        ):
        prototype = (Artist, Label, SQLArtist, SQLLabel)
        assert isinstance(center_entity, prototype)
        self.center_entity = center_entity
        degree = int(degree)
        assert 0 < degree
        self.degree = degree
        self.cache = cache
        if max_nodes is not None:
            max_nodes = int(max_nodes)
            assert 0 < max_nodes
        self.max_nodes = max_nodes
        role_names = role_names or None
        if role_names:
            if isinstance(role_names, six.string_types):
                role_names = (role_names,)
            elif not isinstance(role_names, collections.Iterable):
                role_names = (role_names,)
            role_names = tuple(role_names)
            assert all(_ in ArtistRole._available_credit_roles
                for _ in role_names)
        self.role_names = role_names

    @classmethod
    def get_link_key(cls, link):
        source_type, source_id = link['source']
        if source_type == 1:
            source_type = 'artist'
        else:
            source_type = 'label'
        target_type, target_id = link['target']
        if target_type == 1:
            target_type = 'artist'
        else:
            target_type = 'label'
        return '{}-{}-{}-{}-{}'.format(
            source_type,
            source_id,
            cls.word_pattern.sub('-', link['role']).lower(),
            target_type,
            target_id,
            )

    def relation_to_link(self, relation):
        link = relation.copy()
        entity_one_id = link['entity_one_id']
        entity_one_type = link['entity_one_type']
        #entity_one_type = Relation.EntityType(entity_one_type)
        #entity_one_type = entity_one_type.name.lower()
        source_key = (entity_one_type, entity_one_id)
        link['source'] = source_key
        entity_two_id = link['entity_two_id']
        entity_two_type = link['entity_two_type']
        #entity_two_type = Relation.EntityType(entity_two_type)
        #entity_two_type = entity_two_type.name.lower()
        target_key = (entity_two_type, entity_two_id)
        link['target'] = target_key
        link['role'] = link['role_name']
        link['key'] = self.get_link_key(link)
        if '_id' in link: del(link['_id'])
        if 'country' in link: del(link['country'])
        if 'entity_one_id' in link: del(link['entity_one_id'])
        if 'entity_one_type' in link: del(link['entity_one_type'])
        if 'entity_two_id' in link: del(link['entity_two_id'])
        if 'entity_two_type' in link: del(link['entity_two_type'])
        if 'id' in link: del(link['id'])
        if 'role_name' in link: del(link['role_name'])
        if 'category' in link and not link.get('category'):
            del(link['category'])
        if 'subcategory' in link and not link.get('subcategory'):
            del(link['subcategory'])
        if 'genres' in link and not link.get('genres'):
            del(link['genres'])
        if 'random' in link:
            del(link['random'])
        if 'release_id' in link and not link.get('release_id'):
            del(link['release_id'])
        if 'styles' in link and not link.get('styles'):
            del(link['styles'])
        if 'year' in link and not link.get('year'):
            del(link['year'])
        return link

    def entity_key_to_node(self, entity_key, distance):
        node = dict(distance=distance, missing=0, members=set(), aliases=set())
        node['id'] = entity_key[1]
        if entity_key[0] == 1:
            node['type'] = 'artist'
        else:
            node['type'] = 'label'
        node['key'] = '{}-{}'.format(node['type'], node['id'])
        node['links'] = set()
        return node

    def collect_entities_2(self):
        original_role_names = self.role_names or ()
        provisional_role_names = set(original_role_names)
        provisional_role_names.update(['Alias', 'Member Of'])
        provisional_role_names = sorted(provisional_role_names)

        if type(self.center_entity).__name__.endswith('Artist'):
            initial_key = (1, self.center_entity.discogs_id)
        else:
            initial_key = (2, self.center_entity.discogs_id)
        entity_keys_to_visit = set([initial_key])

        links = dict()
        nodes = dict()

        entity_query_cap = 999
        entity_query_cap -= (1 + len(provisional_role_names)) * 2
        entity_query_cap //= 2

        for distance in range(self.degree + 1):
            current_entity_keys_to_visit = list(entity_keys_to_visit)
            for key in current_entity_keys_to_visit:
                nodes.setdefault(key, self.entity_key_to_node(key, distance))
            entity_keys_to_visit.clear()
            relations = []
            for i in range(0, len(current_entity_keys_to_visit), entity_query_cap):
                # Split into multiple queries to avoid variable maximum.
                entity_key_slice = current_entity_keys_to_visit[i:i + entity_query_cap]
                relations.extend(SQLRelation.search_multi(
                    entity_key_slice,
                    role_names=provisional_role_names,
                    ))
            for relation in relations:
                e1k = (relation['entity_one_type'], relation['entity_one_id'])
                e2k = (relation['entity_two_type'], relation['entity_two_id'])
                if e1k not in nodes:
                    entity_keys_to_visit.add(e1k)
                    nodes[e1k] = self.entity_key_to_node(e1k, distance + 1)
                if e2k not in nodes:
                    entity_keys_to_visit.add(e2k)
                    nodes[e2k] = self.entity_key_to_node(e2k, distance + 1)
                if relation['role_name'] == 'Alias':
                    nodes[e1k]['aliases'].add(e2k[1])
                    nodes[e2k]['aliases'].add(e1k[1])
                elif relation['role_name'] in ('Member Of', 'Sublabel Of'):
                    nodes[e2k]['members'].add(e1k[1])
                if relation['role_name'] not in original_role_names:
                    continue
                link = self.relation_to_link(relation)
                link['distance'] = min(
                    nodes[e1k]['distance'],
                    nodes[e2k]['distance'],
                    )
                links[link['key']] = link
                nodes[e1k]['links'].add(link['key'])
                nodes[e2k]['links'].add(link['key'])

        # Query node names.
        artist_ids = []
        label_ids = []
        for entity_type, entity_id in nodes.keys():
            if entity_type == 1:
                artist_ids.append(entity_id)
            else:
                label_ids.append(entity_id)
        artists = []
        for i in range(0, len(artist_ids), 999):
            query = (SQLArtist
                .select()
                .where(SQLArtist.id.in_(artist_ids[i:i + 999]))
                )
            artists.extend(query)
        labels = []
        for i in range(0, len(artist_ids), 999):
            query = (SQLLabel
                .select()
                .where(SQLLabel.id.in_(label_ids[i:i + 999]))
                )
            labels.extend(query)
        for artist in artists:
            nodes[(1, artist.id)]['name'] = artist.name
        for label in labels:
            nodes[(2, label.id)]['name'] = label.name

        # Prune unvisited nodes and links.
        for key in entity_keys_to_visit:
            node = nodes.pop(key)
            for link_key in node['links']:
                link = links[link_key]
                source_key = link['source']
                if source_key in nodes:
                    source_node = nodes[link['source']]
                    source_node['missing'] += 1
                    source_node['links'].remove(link_key)
                target_key = link['target']
                if target_key in nodes:
                    target_node = nodes[link['target']]
                    target_node['missing'] += 1
                    target_node['links'].remove(link_key)
                del(links[link_key])

        return nodes, links

    def get_network_2(self):
        nodes, links = self.collect_entities_2()
        cluster_count = 0
        cluster_map = {}
        for node in nodes.values():
            cluster = None
            if node['aliases']:
                if node['id'] not in cluster_map:
                    cluster_count += 1
                    cluster_map[node['id']] = cluster_count
                    for alias_id in node['aliases']:
                        cluster_map[alias_id] = cluster_count
                cluster = cluster_map[node['id']]
            if not node['aliases']:
                del(node['aliases'])
            else:
                node['aliases'] = tuple(sorted(node['aliases']))
            if cluster is not None:
                node['cluster'] = cluster
            node['size'] = len(node.pop('members'))
            node['links'] = tuple(sorted(node['links']))
        links = tuple(sorted(links.values(),
            key=lambda x: (x['source'], x['role'], x['target'])))
        for link in links:
            if link['source'][0] == 1:
                link['source'] = 'artist-{}'.format(link['source'][1])
            else:
                link['source'] = 'label-{}'.format(link['source'][1])
            if link['target'][0] == 1:
                link['target'] = 'artist-{}'.format(link['target'][1])
            else:
                link['target'] = 'label-{}'.format(link['target'][1])
        nodes = tuple(sorted(nodes.values(), key=lambda x: (x['type'], x['id'])))
        if type(self.center_entity) in (Artist, SQLArtist):
            center = 'artist-{}'.format(self.center_entity.discogs_id)
        else:
            center = 'label-{}'.format(self.center_entity.discogs_id)
        network = {
            'center': center,
            'nodes': nodes,
            'links': links,
            }
        return network