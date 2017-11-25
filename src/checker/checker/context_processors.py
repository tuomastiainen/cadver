#!/usr/bin/env python
# -*- coding: utf-8 -*-

from creocheck.models import CheckUser, AssignmentCollection

def active_user(request):
    try:
        return {'active_user': CheckUser.objects.get(pk=request.session.get('active_user_pk')).user_id}
    except:
        return {}


def ac(request):
    try:
        return {'assignment_collections': AssignmentCollection.objects.all()}
    except:
        return {}
