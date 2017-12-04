from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest

# Create your views here.

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from creocheck.forms import UploadFileForm
from creocheck.models import CheckTemplate, Assignment, CheckTask, CheckUser, AssignmentCollection, UploadFile
from django.http import HttpResponseRedirect
import io
import json
import random
import json
from django.conf import settings

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
import io

from django.contrib.auth.decorators import login_required

import datetime


def get_user(request):
    return CheckUser.objects.get(pk=request.session.get('active_user_pk'))


def serialize_task(checktask):
    d = [
        checktask.pk, checktask.assignment.name, checktask.file.display_name,
        checktask.progress, checktask.get_status(), checktask.passed, None]
    return d
    return json.dumps(d)


@login_required
def checks_admin(request):

    print(request.session.get("active_assignment"))
    try:
        selected_assignment = Assignment.objects.get(
            pk=request.session.get("active_assignment"))
        tasks = CheckTask.objects.filter(
            assignment=selected_assignment).order_by("-passed", "-created")
    except:
        tasks = CheckTask.objects.all().order_by("-passed", "-created")
    context = {}
    context.update({"tasks": tasks})
    return render(request, "creocheck/admin-main.html", context)


@login_required
def admin_check_detail(request, pk):
    checktask = CheckTask.objects.get(pk=pk)
    context = {}
    context.update({"checktask": checktask})
    return render(request, "creocheck/admin-check.html", context)


@login_required
def checks_admin_filter(request, active_assignment):
    request.session['active_assignment'] = active_assignment
    return HttpResponseRedirect("/checks_admin/")


@login_required
@csrf_exempt
def admin_excel_export(request):

    try:
        selected_assignment = Assignment.objects.get(
            pk=request.session.get("active_assignment"))
        tasks = CheckTask.objects.filter(
            assignment=selected_assignment).order_by("-passed", "-created")
    except:
        tasks = CheckTask.objects.all().order_by("-passed", "-created")

    print("EXPORT to EXCEL")
    header = ["Check ID", "User ID", "Timestamp",
              "Assignment", "Collection", "Passed"]

    wb = Workbook()
    ws = wb.active
    ws.append(header)
    for t in tasks:
        ws.append(
            [t.pk, str(t.user), str(t.created), t.assignment.name, t.assignment.collection.name, str(t.passed)])
    out = io.BytesIO()
    wb.save(out)

    date_str = (datetime.datetime.now().strftime("CADVER_%y%m%d_%H%M%S"))
    response = HttpResponse(save_virtual_workbook(
        wb), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename={}.xlsx'.format(
        date_str)
    return response


@login_required
def admin_user_detail(request, pk):
    user = CheckUser.objects.get(pk=pk)
    context = {}
    context.update({"user": user})
    return render(request, "creocheck/admin-user.html", context)


def update_tasks(request):
    checktasks = CheckTask.objects.filter(
        user=get_user(request)).order_by("-pk")[:6]
    l = {"data": [serialize_task(i) for i in checktasks]}
    return HttpResponse(json.dumps(l), content_type="application/json")


def activate_user_collection(request):
    user_id = (request.GET.get("user_id"))
    assignment_collection_name = (request.GET.get("ac_name"))

    request.session['active_user_pk'] = CheckUser.objects.get_or_create(
        user_id=user_id)[0].pk
    try:
        request.session['active_collection_pk'] = AssignmentCollection.objects.get(
            name=assignment_collection_name).pk
    except AssignmentCollection.DoesNotExist:
        return HttpResponseBadRequest("Assignment collection does not exist")

    return HttpResponseRedirect("/")


from django.contrib.auth import logout as django_logout


def logout(request):
    request.session['active_user_pk'] = None
    django_logout(request)
    return HttpResponseRedirect("/")


def index(request):
    pk = request.session.get('active_user_pk')
    if not pk:
        return HttpResponse("USE LINK TO ACTIVATE SESSION.")
    if not CheckUser.objects.filter(pk=pk).exists():
        return HttpResponse("USE LINK TO ACTIVATE SESSION.")

    context = {}
    try:
        collection = AssignmentCollection.objects.get(
            pk=request.session.get('active_collection_pk'))
    except:
        return HttpResponse("USE LINK TO ACTIVATE SESSION.")

    context.update(
        {'assignments': Assignment.objects.filter(collection=collection)})
    context.update({'refresh_rate': settings.REFRESH_RATE})
    context.update({'admin_email': settings.ADMIN_EMAIL})
    return render(request, "creocheck/index.html", context)


def task_detail(request, pk):
    task = CheckTask.objects.get(pk=pk, user=get_user(request))
    context = {}
    context.update({"task": task})
    context.update({"checks": task.get_checks()})
    return render(request, "creocheck/task-detail.html", context)


import uuid


@csrf_exempt
def receive_file(request):

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            extension = f.name.split(".")[1].lower()
            display_name = f.name

            if not any(ext in extension for ext in settings.ALLOWED_EXTENSIONS):
                return HttpResponseBadRequest("INVALID FILE FORMAT")

            # generate the file a random name
            f.name = "{}.{}".format(str(uuid.uuid4()).split("-")[0], extension)
            # print(request.POST.get("assignment_name"))
            assignment = Assignment.objects.get(
                name=request.POST.get("assignment_name"))

            new_file = UploadFile(file=f, display_name=display_name)
            new_file.save()

            a = CheckTask.objects.create(
                assignment=assignment, file=new_file, user=get_user(request))
            print("Created checktask")
            print(CheckTask.objects.all().count())
            print("running checktask")
            a.run()
            return HttpResponse("OK")

    return HttpResponseBadRequest("Invalid request")
