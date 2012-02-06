import json
from django.contrib.auth.models import User
from django.db import models
from django.test import TestCase
from anime import api
from anime.forms.create import createFormFromModel
from anime.models import AnimeItem, AnimeName, AnimeRequest, AnimeImageRequest, DATE_FORMATS
from anime.tests.functions import create_user, login, check_response, fill_params


class ErrorsTest(TestCase):

    fixtures = ['2trash.json']

    def send_request(self, link, params, returns):
        response = self.client.post(link, params)
        ret = json.loads(response._container[0])
        try:
            check_response(ret, returns)
        except AssertionError, e:
            raise AssertionError('Error in response check. Data: %s, %s\nOriginal message: %s' % (
                    ret, returns, e.message))

    @create_user()
    def setUp(self):
        pass

    #def test_login(self):

    @login()
    def test_add(self):
        a = api.Add()
        link = a.get_link()
        self.send_request(link, {}, a.errors)

    def test_fields(self):
        pass
        #wait for assertFieldOutput
