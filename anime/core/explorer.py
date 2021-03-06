# -*- coding: utf-8 -*-
from django.db.models.fields import FieldDoesNotExist
from django.utils.translation import ugettext_lazy as _
from anime.models import LINKS_TYPES, EDIT_MODELS, USER_STATUS


class GetError(Exception):
    pass


class FieldExplorer(object):
    CALLABLE_FIELDS = ['anime', 'state', 'name', 'genre', 'genre_list', 'links',
                       'release', 'type', 'releaseType', 'bundle']
    error_messages = {
        'bad_field': _('Bad field'),
        'error': _('Error: {0}'),
        'bad_user': _('Anonymous users have no statistics.'),
    }

    def __init__(self, field):
        self.set_field(field)

    def set_field(self, field):
        if field == 'releasedAt,endedAt':
            field = 'release'
        self.field = field

    def get_field(self):
        field = getattr(self, self.field, None)
        return field

    def get_value(self, anime, request):
        if not anime:
            return
        field = self.get_field()
        try:
            if callable(field):
                if field.__name__ in self.CALLABLE_FIELDS:
                    return field(anime, request)
                raise ValueError(self.error_messages['bad_field'])
            else:
                try:
                    anime._meta.get_field(self.field)
                    return getattr(anime, self.field)
                except (FieldDoesNotExist, AttributeError):
                    raise ValueError(self.error_messages['bad_field'])
        except Exception, e:
            raise GetError(self.error_messages['error'].format(e))

    def get_model(self):
        try:
            model = EDIT_MODELS[self.field]
        except KeyError:
            model = None
        return model

    def anime(self, anime, request):
        return None

    def state(self, anime, request):
        if not request.user.is_authenticated():
            return self.error_messages['bad_user']
        try:
            bundle = self.get_model().objects.get(anime=anime, user=request.user)
            status = int(bundle.state)
        except Exception:
            status = 0
        response = {'state': status, 'select': dict(USER_STATUS)}
        # Магические числа, охуенно
        if status == 3:
            response.update({'rating': bundle.rating})
        elif status in (2, 4):
            response.update({'completed': bundle.count,
                                        'all': anime.episodesCount})
        return response

    def name(self, anime, request):
        return list(self.get_model().objects.filter(anime=anime).values_list('title', flat=True))

    def genre(self, anime, request):
        return u', '.join(anime.genre.values_list('name', flat=True))

    def genre_list(self, anime, request):
        return anime.genre.values_list('name', flat=True)

    def links(self, anime, request):
        model = self.get_model()
        if model:
            d = {}
            for x in model.objects.filter(anime=anime).values_list('linkType', 'link'):
                for t in LINKS_TYPES:
                    if t[0] == x[0]:
                        name = t[-1]
                if name not in d:
                    d[name] = []
                d[name].append(x[1])
            return d

    def release(self, anime, request):
        return anime.release

    def type(self, anime, request):
        return anime.type

    def releaseType(self, anime, request):
        return anime.type

    def bundle(self, anime, request):
        if anime.bundle:
            items = anime.bundle.animeitems.all().order_by('releasedAt')
            bundles = [{'title': x.title, 'id': x.id} for x in items]
            return {'id': anime.bundle.id, 'bundles': bundles}
        return None
