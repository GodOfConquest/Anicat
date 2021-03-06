# -*- coding: utf-8 -*-
import datetime
from anime.models import ANIME_TYPES, USER_STATUS, LINKS_TYPES
from anime.api.base import ApiBase
from anime.api.types import (Comment, Noneable, NoneableDict,
                             Field, CatalogGetTypes )
from anime.api.forms import from_form

__all__ = ['Filter', 'Register', 'Login', 'Add', 'Get', 'Search',
           'List', 'Forms', 'Statistics', 'Set', 'out', 'to_file']


class Filter(ApiBase):
    """Apply filter to site output."""

    link = 'filter/'
    response = 'filter'

    params = from_form('anime.forms.Error.FilterForm')

    error = {
        'text': dict
    }


class List(ApiBase):
    """Get main list as JSON-object."""

    link = 'list/'
    response = 'list'
    view = 'anime.views.table.IndexListView'

    error = {
        'text': list
    }



class Statistics(ApiBase):
    """User statisics.
    Returns statistics for curren user if `user_id` is not set."""

    link = 'stat/'
    response = 'stat'

    params = {
        'user_id': Noneable(int)
    }

    returns = {
        'text': {
            'stat': [{
                'count': int,
                'anime__duration': Noneable(int),
                'full': Noneable(int),
                'name': unicode,
                'anime__episodesCount': Noneable(int),
                'custom': Noneable(int)
            }],
            'userid': int
        }
    }

    error = {
        'text': list
    }



class Register(ApiBase):
    """Register new account."""

    link = 'register/'

    params = {
        'register-email': unicode,
    }

    returns = {
        'status': True,
        'response': 'login',
        'text': {'name': unicode}
    }

    error = {
        'response': 'register',
        'status': False,
        'text': dict,
    }


class Login(ApiBase):
    """Login to site."""

    link = 'login/'
    response = 'login'
    params = from_form('anime.forms.User.NotActiveAuthenticationForm')

    returns = {
        'text': {'name': unicode}
    }

    error = {
        'text': dict,
    }


class Add(ApiBase):
    """Add new record.
    This is a `form` field. It returns form if requested without parameters."""

    link = 'add/'
    response = 'add'

    params = from_form('anime.forms.ModelError.AnimeForm')

    returns = {
        'id': int,
    }

    returns_noarg = {
        'title': Field('input', 'title'),
        'releaseType': Field('select', 'releaseType', choices=ANIME_TYPES),
        'duration': Field('input', 'duration', value=int),
        'episodesCount': Field('input', 'episodesCount', value=int),
        'releasedAt': Field('input', 'releasedAt', value=datetime.date),
        'endedAt': Field('input', 'endedAt', value=datetime.date),
        'genre': [Field('input', 'genre', value=int), Field('input', 'genre', value=int)],
        'air': Field('input', 'air', value=bool),
    }

    error = {
        'text': dict,
    }


class Get(ApiBase):
    """Get certain field for record."""

    link = 'get/'
    response = 'get'

    params = {
        'field': tuple,
        'id': int
    }

    returns = {
        'id': int,
        'text': CatalogGetTypes()
    }

    error = Comment(u"""        No global errors for the get rerquest.
        All fields errors in response `text` parameter.""")


class Search(ApiBase):
    """Search in database.
    Optional `fields` argument can be passed to retrive only certain fields in response."""

    link = 'search/'
    response = 'search'
    view = 'anime.views.table.SearchListView'
    error = {
        'text': list,
    }


class Forms(ApiBase):
    """This API call returns JSON-serialized form for field."""

    api_keys = ['state', 'anime', 'links', 'bundle', 'name']

    link = 'form/'
    response = 'form'

    params = {
        'id': int,
        'model': unicode,
        'field': Noneable(unicode)
    }

    returns = NoneableDict({
        'status': True,
        'id': int,
        'model': unicode,
        'field': Noneable(unicode),
        'form': list
    })

    forms = {
        'state': Field('select','state', choices=USER_STATUS),
        'anime': {
            'title': Field('input', 'title'),
            'releaseType': Field('select', 'releaseType', choices=ANIME_TYPES),
            'episodesCount': Field('input', 'episodesCount', value=int),
            'duration': Field('input', 'duration', value=int),
            'releasedAt': Field('input', 'releasedAt', 'Released', value=datetime.date),
            'endedAt': Field('input', 'endedAt', 'Ended', value=datetime.date),
            'air': Field('input', 'air'),
        },
        'links': [Field('input', 'Link 0', default_obj='http://example.com'), Field('select', 'Link type 0', choices=LINKS_TYPES, default_obj=0)],
        'animerequest': Field('textarea', 'text', 'Request anime'),
        'image': Field('input', 'text', 'File'),
        'request': Field('textarea', 'text'),
        'feedback': Field('textarea', 'text', 'Please tell about your suffering'),
        'bundle': [Field('input', 'Bundle 0', default_obj=1), Field('input', 'Bundle 1', default_obj=2)],
        'name': [Field('input', 'Name 0'), Field('input', 'Name 1')],
    }

    error = {
        'status': False,
        'model': unicode,
        'field': Noneable(unicode),
        'id': unicode,
        'text': unicode,
    }

    def get_fields(self, t, f=None):
        ret = []
        if not isinstance(self.forms[t], Field) and f is not None:
            form = self.forms[t][f]
        else:
            form = self.forms[t]
        if type(form) in (tuple, list):
            ret.extend(form)
        else:
            ret.append(form)
        return ret

    def get_returns(self, t, f=None):
        r = self.returns
        r['form'] = []
        for item in self.get_fields(t, f):
            if type(item) is dict:
                for key, value in item.items():
                    r['form'].append(value.field())
            else:
                r['form'].append(item.field())
        return r

    def string_returns(self):
        r = self.returns
        f = {}
        for i in self.api_keys:
            f[i] = self.forms[i]
        r['form'] = [Comment("This data is serialised form fields list. Field types:"), f]
        return r


class Set(Get):
    """Change field."""

    link = 'set/'

    params = {
        'id': int,
        'model': unicode,
        'field': Noneable(unicode),
    }

    returns = {
        'response': 'edit',
        'status': True,
        'id': int,
        'field': Noneable(unicode),
        'model': unicode,
        'text': dict,
    }

    error = {
        'response': 'form',
        'status': False,
        'model': unicode,
        'field': Noneable(unicode),
        'id': int,
        'text': dict,
    }

    types = CatalogGetTypes()
    forms = Forms()

    def get_returns(self, t):
        r = self.returns.copy()
        r['text'] = self.types[t]
        return r

    def string_returns(self):
        return self.returns.copy()

    def get_params(self, t, f=None):
        form = self.forms.get_fields(t, f)
        ret = self.params.copy()
        for item in form:
            attr = item.props(False)
            ret[attr['name']] = attr['value']
        return ret

    def string_params(self):
        return self.params.copy()


OUTPUT = [Search, List, Get, Statistics, Filter, Login, Forms, Add, Set]

def out():
    for item in OUTPUT:
        print item.__str__()


def to_file(filename):
    with open(filename, 'w') as fl:
        fl.write(u"""API reference.
Notes:
    Ajax requests must be POST, sent to /ajax/$target.
    Response is a json structure with 3 mandatory fields:
        response - string, type of response,
        status - bool, result of request process,
        text - different, body of response.

""")
        for item in OUTPUT:
            fl.write(item.__str__())
            fl.write('\n')
