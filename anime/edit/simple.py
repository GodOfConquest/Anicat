
from anime.utils import cache
from django.utils.translation import ugettext_lazy as _

from anime.edit.default import EditableDefault, EditError
from anime.models import AnimeItem, USER_STATUS



class Anime(EditableDefault):
    extra_error_messages = {
        'all_required': _('Cannot save new instance without all required fields.'),
    }

    def save(self, form, obj):
        if not self.item_id:
            if not self.fields:
                obj.save()
            else:
                raise ValueError(self.error_messages['all_required'])
        super(Anime, self).save(form, obj)

    def last(self):
        super(Anime, self).last()
        if 'title' in self.fields and self.obj.bundle:
            for item in self.obj.bundle.animeitems.values_list('id').all():
                cache.delete('card:%s' % item[0])


class State(EditableDefault):
    extra_error_messages = {
        'invalid': _('Status value not valid.'),
    }

    def setObject(self):
        try:
            anime = AnimeItem.objects.get(id=self.item_id)
        except AnimeItem.DoesNotExist:
            raise EditError(self.error_messages['bad_id'])
        try:
            obj = self.model.objects.get(user=self.request.user, anime=anime)
        except self.model.DoesNotExist:
            obj = self.model(user=self.request.user, anime=anime, state=0)
        self.oldstatus = obj.state
        self.obj = obj
        try:
            self.status = int(self.request.POST.get('state'))
            if not -1 < self.status < len(USER_STATUS):
                raise EditError(self.error_messages['invalid'])
        except:
            self.status = 0
        self.retid = self.item_id

    def last(self):
        user = self.request.user
        # We can setup it here instead of deleting, but expirience says:
        # NEVER TRUST THE CACHE
        cache.delete('lastuserbundle:{0}'.format(user.id))
        cache.delete('userCss:{0}'.format(user.id))
        cache.delete('Stat:{0}'.format(user.id))


class Bundle(EditableDefault):

    def get(self, formobject, data=None):
        if 'currentid' in self.request.POST:
            data = {'currentid': self.request.POST['currentid']}
        return super(Bundle, self).get(formobject, data)

    def explore_result(self):
        ret = {}
        retid = self.request.POST.get('currentid')
        try:
            anime = AnimeItem.objects.get(id = retid)
            ret['currentid'] = retid
        except (AnimeItem.DoesNotExist, ValueError):
            retid = self.retid or getattr(self.obj, 'id', 0) or 0
            try:
                anime = AnimeItem.objects.filter(bundle = retid)[0]
                ret['currentid'] = anime.id
            except IndexError:
                anime = None
        ret.update(self.explore_result_item(anime))
        if not ret['text']:
            ret['text'] = []
        return ret

    def last(self):
        for item in self.obj.animeitems.values_list('id').all():
            cache.delete('card:%s' % item[0])
