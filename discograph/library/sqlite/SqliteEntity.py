# -*- encoding: utf-8 -*-
import peewee
import random
from discograph.library.sqlite.SqliteModel import SqliteModel


class SqliteEntity(SqliteModel):

    ### PEEWEE FIELDS ###

    name = peewee.TextField()
    entity_id = peewee.IntegerField()
    entity_type = peewee.IntegerField()

    ### PEEWEE META ###

    class Meta:
        db_table = 'entity'

    ### PRIVATE METHODS ###

    @classmethod
    def _load_from_mongo_class(cls, mongo_class):
        import discograph
        entity_type = 1
        if mongo_class == discograph.Label:
            entity_type = 2
        query = mongo_class.objects().no_cache().timeout(False)
        query = query.only('discogs_id', 'name')
        count = query.count()
        rows = []
        for i, mongo_document in enumerate(query, 1):
            if mongo_document.discogs_id and mongo_document.name:
                rows.append(dict(
                    entity_id=mongo_document.discogs_id,
                    entity_type=entity_type,
                    name=mongo_document.name,
                    random=random.random(),
                    ))
            if len(rows) == 100:
                cls.insert_many(rows).execute()
                rows = []
                print('[{}] Processing {}... {} of {} [{:.3f}%]'.format(
                    cls.__name__,
                    mongo_class.__name__,
                    i,
                    count,
                    (float(i) / count) * 100),
                    )
        if rows:
            cls.insert_many(rows).execute()
            print('[{}] Processing {}... {} of {} [{:.3f}%]'.format(
                cls.__name__,
                mongo_class.__name__,
                i,
                count,
                (float(i) / count) * 100),
                )

    ### PUBLIC METHODS ###

    @classmethod
    def bootstrap(cls):
        import discograph
        cls.drop_table(True)
        discograph.SqliteFTSEntity.drop_table(True)
        cls.create_table()
        discograph.SqliteFTSEntity.create_table(
            content=discograph.SqliteEntity,
            tokenize='unicode61',
            )
        cls._load_from_mongo_class(discograph.Artist)
        cls._load_from_mongo_class(discograph.Label)
        discograph.SqliteFTSEntity.rebuild()
        discograph.SqliteFTSEntity.optimize()

    @classmethod
    def from_artist_id(cls, artist_id):
        where_clause = cls.entity_id == id
        where_clause &= cls.entity_type == 1
        return cls.select().where(where_clause).get()

    @classmethod
    def from_label_id(cls, label_id):
        where_clause = cls.entity_id == id
        where_clause &= cls.entity_type == 2
        return cls.select().where(where_clause).get()

    ### PUBLIC PROPERTIES ###

    @property
    def discogs_id(self):
        return self.id