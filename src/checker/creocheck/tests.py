#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test import Client
import json
import random
import io

from creocheck.models import AssignmentCollection, Assignment, CheckTask, CheckTemplate, CheckLogEvent

from django.conf import settings

from django.test.utils import override_settings


class CadverTestCase(TestCase):

    @classmethod
    def setUp(self):
        self.CREO_RUNNING = True


        massprop_params = """
            [
                {
                "paramset" : {},
                "volume" : 1,
                "surface_area" : 6
                },
                {
                "paramset" : {},
                "volume" : null,
                "surface_area" : null
                }
            ] """
        massprop_params = """
            [
                {
                "paramset" : {},
                "volume" : 10,
                "surface_area" : 6
                },
                {
                "paramset" : {},
                "volume" : null,
                "surface_area" : null
                }
            ] """


        regen_params = """
            [
                {
                "paramset" : {"X": 2, "Y": 5}
                },
                {
                "paramset" : {"X": 3, "Y": 4}
                }
            ]
            """

        modeltree_params = """
            [
                {
                "base_feature": "BASE",
                "paramset" : {"THICK": false, "PARAM2": 50},
                "modeltree": ["PROTRUSION", "PROTRUSION"]
                },
                {
                "base_feature": "BASE",
                "paramset" : {"THICK": false, "PARAM2": 40},
                "modeltree": null
                }
            ]
            """

        macro_params = """
                    [
                        {
                        "paramset" : {"THICK": false, "PARAM2": 50},
                        "custom_funcs": ["custom_func1"]
                        }
                    ]
                    """



        self.c = Client()
        collection  = AssignmentCollection.objects.create(name="123")
        correct_file = "test_files/cube.prt"

        b = Assignment.objects.create(collection=collection, name="TEST ASSIGNMENT 1", correct_file=correct_file)

        # these tests can be run if a creo session is active
        if self.CREO_RUNNING:
            CheckTemplate.objects.create(assignment=b, name="CHECK MASS PROPS", check_func="MassPropChecker", checkparams=massprop_params)
            #CheckTemplate.objects.create(assignment=b, name="CHECK REGEN", check_func="RegenChecker", checkparams=regen_params)
            #CheckTemplate.objects.create(assignment=b, name="CHECK MODELTREE", check_func="ModelTreeChecker", checkparams=modeltree_params)

        for i in CheckLogEvent.objects.all():
            print(i)

        #CheckTemplate.objects.create(assignment=b, name="CHECK MACRO", check_func="MacroRunner", checkparams=macro_params)
        #CheckTemplate.objects.create(assignment=b, name="UPDATE METADATA", check_func="SaveMetaData")

        #CheckTemplate.objects.create(assignment=b, name="SLEEP TEST", check_func="SleepOneSecond")


        super(CadverTestCase, self).setUp(self)



@override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, CELERY_ALWAYS_EAGER=True, BROKER_BACKEND='memory', TEST_RUNNER='djcelery.contrib.test_runner.CeleryTestSuiteRunner')
class test_cadver_views(CadverTestCase):


    def test_index_no_activation(self):
        r = self.c.get('/')
        self.assertTrue("LINK" in str(r.content))


    def test_activate_collection(self):
        r = self.c.get('/login/?user_id=123123&ac_name=123', follow=True)
        self.assertTrue("html" in str(r.content))


    def test_post_incorrect_filetype(self):
        with open("test_files/testfile.txt", 'rb') as f:
            c = Client()
            r = self.c.get('/login/?user_id=123123&ac_name=123', follow=True)
            params = {'assignment_name': Assignment.objects.first().name, 'file': f}
            r = self.c.post('/receive-file', params)

            self.assertTrue("INVALID FILE FORMAT" in str(r.content))

    def test_post_file(self):

        with open("test_files/cube.prt.1", 'rb') as f:
            c = Client()
            r = self.c.get('/login/?user_id=123123&ac_name=123', follow=True)
            params = {'assignment_name': Assignment.objects.first().name, 'file': f}
            r = self.c.post('/receive-file', params)
            self.assertTrue("OK" in str(r.content))
            #if self.CREO_RUNNING:
            #    self.assertEqual(CheckLogEvent.objects.all().count(), 12)
            #else:
            #    self.assertEqual(CheckLogEvent.objects.all().count(), 4)
