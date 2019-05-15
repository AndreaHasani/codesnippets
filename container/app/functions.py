import json
from sqlalchemy.ext.declarative import DeclarativeMeta
from datetime import date


from sqlalchemy import or_ as _or
from sqlalchemy import and_ as _and

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                if isinstance(data, date):
                    data = data.strftime("%Y-%m-%d")
                try:
                    # this will fail on non-encodable values, like other classes
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    pass
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)

def init_celery(app, celery):
    """Add flask app context to celery.Task"""
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask


class Search(object):
    def __init__(self, app=None, db=None):
        """
        You can custom analyzer by::

            from jieba.analyse import ChineseAnalyzer
            search = Search(analyzer = ChineseAnalyzer)
        """
        self.db = db
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not self.db:
            self.db = self.app.extensions['sqlalchemy'].db
        self.db.Model.query_class = self._query_class(
            self.db.Model.query_class)


    def _query_class(self, q):
        _self = self

        class Query(q):
            def search(self, query, tags_query=None, fields=None, limit=None, or_=False):
                model = self._mapper_zero().class_
                return _self.search(model, query, tags_query, fields, limit, or_)

        return Query

    def search(self, module, title_query, tags_query=None, fields=None, limit=None, or_=True):
        if fields is None:
            fields = module.__searchable__
        filter_title = []
        filter_tags = []
        keywords = title_query.split(' ')
        for field in fields:
            if field == "title":
                query = [getattr(module, field).contains(keyword)
                         for keyword in keywords if keyword]

                if not or_:
                    filter_title.append(_and(*query))
                else:
                    filter_title.append(_or(*query))

            if field == "tags":
                query = [getattr(module, field).contains(tag)
                         for tag in tags_query if tag]

                filter_tags.append(_and(*query))
        results = module.query.filter(_or(*filter_title))
        results = results.filter(_and(*filter_tags))
        if limit is not None:
            results = results.limit(limit)
        return results
