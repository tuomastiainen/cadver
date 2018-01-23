# -*- coding: utf-8 -*-


from io import StringIO
from time import sleep
import traceback
import os

from django.conf import settings
#from creocheck.models import CheckTemplate
import json
import random
import re


if os.name == 'nt':
    from win32com.client.dynamic import Dispatch
    from win32com.client.gencache import EnsureDispatch
    import win32com
    from win32com.client import makepy
    import pythoncom

class CreoWrapperError(Exception):
    def __init__(self, message):
        super(CreoWrapperError, self).__init__(message)

class PythonCreoConnection():

    def init_win32com(self):
        pythoncom.CoInitialize()

    def __enter__(self):
        self.init_win32com()
        print("Trying to form connection")
        self.models = []
        self.asyncconn = Dispatch('pfcls.pfcAsyncConnection')
        self.conn = self.asyncconn.Connect(None, None, None, None)
        self.session = self.conn.Session
        print("Connection formed")

        return self

    def open_file(self, path):
        options = Dispatch('pfcls.pfcRetrieveModelOptions')
        o = options.Create()
        file = Dispatch('pfcls.pfcModelDescriptor')

        # VBAPI fails if it is given a creo file with the version number appended
        path = re.sub(r"\.prt(\.[0-9]+)", ".prt", path)

        f = file.CreateFromFilename(path)
        self.models.append(self.session.RetrieveModelWithOpts(f, o))
        self.session.OpenFile(f)

    def activate_window(self, model_id):
        self.window = self.session.GetModelWindow(self.models[model_id])
        self.window.Activate()

    def close_window(self):
        self.window.Close()

    def set_parameter(self, mdl, param_name, value):
        param = mdl.GetParam(param_name)

        try:
            paramvalue = param.value
        except AttributeError:
            raise CreoWrapperError("Parameter {} not found".format(param_name))


        modelitem = Dispatch('pfcls.MpfcModelItem')
        #create boolean if param is not float
        if isinstance(value, bool):
            val = modelitem.CreateBoolParamValue(value)
        elif isinstance(value, (float, int)):
            val = modelitem.CreateDoubleParamValue(value)
        else:
            raise CreoWrapperError("Invalid value type")

        param.SetScaledValue(val, None)

        # this could be separated, is it really needed to regenerate after each param set?

    def assign_paramset(self, mdl, paramset):
        for key in paramset:
            self.set_parameter(mdl, key, paramset[key])

    def regenerate(self, mdl):
        try:
            mdl.Regenerate(None)
            self.window.Repaint()
            mdl.Regenerate(None)
            self.window.Repaint()
        except:
            raise CreoWrapperError("Model failed to regenerate with {} = {}".format(param_name, value))

    def __exit__(self, exc_type, exc_value, traceback):

        for i in range(len(self.models)):
            try:
                window = self.session.GetModelWindow(self.models[i])
                window.Activate()
                window.Close()
            except:
                pass

        self.conn.Disconnect(2)
        print("Connection closed")



class CheckBase(object):

    def __init__(self, *args, **kwargs):
        self.check_object = kwargs.get("check_object")
        self.checktemplate = kwargs.get("checktemplate")

        self.result = False
        if self.checktemplate.assignment.correct_file:
            self.correct_file_path = "{}\{}".format(
                settings.ROOT, self.checktemplate.assignment.correct_file).replace("/", "\\")
        else:
            self.correct_file_path = None

        self.check_file_path = "{}\{}".format(
            settings.ROOT, self.check_object.task.file.file).replace("/", "\\")

        print(self.correct_file_path)
        print(self.check_file_path)

        try:
            self.data = json.loads(self.checktemplate.checkparams)
        except (TypeError, ValueError):
            self.data = None

    def log(self, text):
        # circular import from models if this is on top
        from creocheck.models import CheckLogEvent
        log = CheckLogEvent.objects.create(
            check_object=self.check_object, text=text)
        print(log)

    def isclose(self, a, b, rel_tol=0.01, abs_tol=0.0):
        return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class RegenChecker(CheckBase):

    def __init__(self, *args, **kwargs):
        super(RegenChecker, self).__init__(*args, **kwargs)
        self.passed = True
        self.check_regen()

    def check_regen(self):


        with PythonCreoConnection() as conn:
            for i in self.data:

                conn.open_file(self.check_file_path)
                conn.activate_window(0)
                model = conn.models[0]
                conn.set_parameter(model, "MP_DENSITY", 1)
                paramset = i.get("paramset")

                try:
                    conn.assign_paramset(model, paramset)
                    conn.regenerate(model)
                    self.log("passed regeneration with paramset {}".format(paramset))
                except:
                    self.passed = False
                    self.log("failed to regenerate with paramset {}".format(paramset))
                conn.close_window()
    def check_result(self):
        return self.passed


class MassPropChecker(CheckBase):
    # volume, surface area, mass, and center of gravity

    def __init__(self, *args, **kwargs):
        super(MassPropChecker, self).__init__(*args, **kwargs)
        self.get_info()
        self.form_check_result()

    def get_info(self):
        """
        Populate self.data with:
            * read_X <- values from the file to be checked
            * Replace null (becomes None in json.loads) values by actual values from the correct file
        """

        with PythonCreoConnection() as conn:
            for i in self.data:

                conn.open_file(self.check_file_path)
                conn.activate_window(0)
                model = conn.models[0]
                conn.set_parameter(model, "MP_DENSITY", 1)
                paramset = i.get("paramset")

                self.log(
                    "Regenerating returned model with paramset: {}".format(paramset))

                conn.assign_paramset(model, paramset)
                conn.regenerate(model)

                massprop = model.GetMassProperty(None)
                i.update({"read_surface_area": massprop.SurfaceArea})
                i.update({"read_volume": massprop.Volume})
            conn.close_window()

            # save time by not opening the correct file if values are already
            # present in the dict

            for i in self.data:
                if None in i.values():
                    open_correct_file = True

            # replace none values with correct

            if open_correct_file:
                conn.open_file(self.correct_file_path)
                #conn.activate_window(1)
                #print(conn.models)
                model = conn.models[2]

                for i in self.data:
                    conn.set_parameter(model, "MP_DENSITY", 1)
                    paramset = i.get("paramset")

                    #self.log(
                    #    "Regenerating correct model with paramset: {}".format(paramset))

                    conn.assign_paramset(model, paramset)
                    conn.regenerate(model)

                    # if needed (None is present), regenerate correct model
                    # with paramset
                    massprop = model.GetMassProperty(None)
                    for key in i:
                        value = i[key]
                        if value is None:
                            if key == "volume":
                                i[key] = massprop.Volume

                            if key == "surface_area":
                                i[key] = massprop.SurfaceArea
                    print(i)
                conn.close_window()

    def form_check_result(self):
        self.passed = True
        for i in self.data:
            if "volume" in i.keys():
                if not self.isclose(i.get("volume"), i.get("read_volume")):
                    self.log("failed volume check, correct {} != {} - {}".format(
                        i.get("volume"), i.get("read_volume"), i.get("paramset")))
                    self.passed = False
                else:
                    self.log(
                        "passed volume check {}".format(i.get("paramset")))

            if "surface_area" in i.keys():
                if not self.isclose(i.get("surface_area"), i.get("read_surface_area")):
                    self.log("failed surface_area check, correct {} != {} - {}".format(
                        i.get("surface_area"), i.get("read_surface_area"), i.get("paramset")))
                    self.passed = False
                else:
                    self.log(
                        "passed surface_area check {}".format(i.get("paramset")))

    def check_result(self):
        return self.passed


class ModelTreeChecker(CheckBase):

    def __init__(self, *args, **kwargs):
        super(ModelTreeChecker, self).__init__(*args, **kwargs)
        self.get_trees()
        self.compare_trees()

    def get_trees(self):

        with PythonCreoConnection() as conn:

            for i in self.data:
                conn.open_file(self.check_file_path)
                conn.activate_window(0)
                model = conn.models[0]
                paramset = i.get("paramset")

                self.log("Regenerating model with paramset: {}".format(paramset))
                paramset = i.get("paramset")
                conn.assign_paramset(model, paramset)
                conn.regenerate(model)

                checked_tree = []
                base = model.GetFeatureByName(i.get("base_feature"))
                children = base.ListChildren()
                for n in range(0, children.Count):
                    checked_tree.append(children.Item(n).FeatTypeName)
                i.update({"read_modeltree": checked_tree})
                conn.close_window()

            for i in self.data:
                if i.get("modeltree") is None:
                    conn.open_file(self.correct_file_path)
                    conn.activate_window(1)
                    model = conn.models[1]

                    paramset = i.get("paramset")
                    conn.assign_paramset(model, paramset)
                    conn.regenerate(model)

                    correct_tree = []
                    base = (model.GetFeatureByName(i.get("base_feature")))
                    children = base.ListChildren()

                    for n in range(0, children.Count):
                        correct_tree.append(children.Item(n).FeatTypeName)
                    i.update({"correct_modeltree": correct_tree})
                    conn.close_window()
                else:
                    i.update({"preset_modeltree": i.get("modeltree")})


    def is_sublist(self, sublst, lst):
        for element in sublst:
            try:
                ind = lst.index(element)
            except ValueError:
                return False
            lst = lst[ind + 1:]
        return True

    def compare_trees(self):
        self.passed = True
        for i in self.data:
            read = i.get("read_modeltree")
            if i.get("correct_modeltree"):
                correct = i.get("correct_modeltree")
                if not (correct == read):
                    self.log("failed with paramset {}".format(i.get("paramset")))
                    self.passed = False
                self.log("Comparing {} to {} (exact match)".format(correct, read))
            elif i.get("preset_modeltree"):
                correct = i.get("preset_modeltree")
                self.log("Comparing {} to {} (features exist in correct order)".format(correct, read))
                if not self.is_sublist(correct, read):
                    self.log("failed with paramset {}".format(i.get("paramset")))
                    self.passed = False


    def check_result(self):
        self.log("Passed: {}".format(self.passed))
        return self.passed


class MacroRunner(CheckBase):

    # implement any macros and custom functions here
    # custom function could open a file and execute a mapkey macro
    def __init__(self, *args, **kwargs):
        super(MacroRunner, self).__init__(*args, **kwargs)
        self.custom_funcs = {"custom_func1": self.custom_func1}
        for i in self.data:
            for func in i.get("custom_funcs"):
                self.custom_funcs.get(func)()


    def custom_func1(self):
        self.log("Running custom macro function")


    def check_result(self):
        self.log("Ran custom macro")
        return True


class SaveMetaData(CheckBase):

    def __init__(self, *args, **kwargs):
        super(SaveMetaData, self).__init__(*args, **kwargs)

    def update_metadata():
        # dump any potentially useful metadata here
        # unfortunately Creo does not save a lot of info
        # also a possibility would be to use hash of file or some filesystem info
        self.checktask.file.metadata = "Not yet implemented"
        self.checktask.file.save()


    def check_result(self):
        self.log("Updated metadata")
        return True


class SleepOneSecond(CheckBase):

    def __init__(self, *args, **kwargs):
        super(SleepOneSecond, self).__init__(*args, **kwargs)
        self.log("Sleeping one second")
        sleep(1)
        self.log("Sleeping done")

    def check_result(self):
        self.log("Return random")
        passed = bool(random.getrandbits(1))
        self.log("Passed: {}".format(passed))
        return passed



import sys
if __name__ == "__main__":
    if False:
        import sys
        from win32com.client import makepy

        sys.argv = ["makepy", r"C:\Program Files\PTC\Creo 3.0\M050\Common Files\x86e_win64\obj\pfclscom.exe"]
        makepy.main ()

    from pprint import pprint

    with PythonCreoConnection() as conn:

        f2 = u"C:\\lego_correct_20171003.prt"

        conn.open_file(f2)
        conn.activate_window(0)
        model = conn.models[0]
        conn.set_parameter(model, "SIZE_V", 2)
        conn.set_parameter(model, "SIZE_H", 2)
        conn.set_parameter(model, "THIN", True)
        instrs = Dispatch('pfcls.pfcRegenInstructions')
        regen_instructions = instrs.Create(False, True, None)
        model.Regenerate(regen_instructions)
        checked_tree = []
        base = (model.GetFeatureByName("BASE"))
        children = base.ListChildren()
        for i in range(0, children.Count):
            checked_tree.append(children.Item(i).FeatTypeName)
        conn.close_window()

        print(checked_tree)
