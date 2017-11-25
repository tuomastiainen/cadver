from django import forms

from creocheck.models import UploadFile


class UploadFileForm(forms.ModelForm):

    class Meta:
        model = UploadFile
        fields = ('file',)
