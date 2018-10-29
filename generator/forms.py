from django import forms
from django.utils import timezone
from datetime import datetime
from django.core.exceptions import ValidationError


class UploadFileForm(forms.Form):
    #title = forms.CharField(max_length=50)
    file = forms.FileField(label='Select a file', help_text='max. 42 megabytes')


class UploadDateForm(forms.Form):
    class Meta:
        pass

class UploadDateForm(forms.Form):
    # to be deleted
    #date = forms.DateField(widget=forms.TextInput(attrs={'type':'month', 'name':'date'}))
    date = forms.CharField(widget=forms.TextInput(attrs={'type':'month', 'name':'date'}))

    # TEST-upload
    file = forms.FileField(label='Import rozpisu služeb', help_text='max. 42 megabytes')

    # def clean_date(self):
    #     print("validating_date")
    #     date = self.cleaned_data["date"]
    #
    #     if 2000 >= date[:4] >= int(datetime.now().year) and date[5:7] not in range(1, 13):
    #         print("validation_date FALSE")
    #         raise ValidationError("chyba")
    #
    #     print("validation_date TRUE")
    #     return date
    #
    # def clean_file(self):
    #     print("validate file")
    #     file = self.cleaned_data["file"]
    #
    #     return file

    def clean(self):
        print("function clean()")
        x = super()
        print(x)
        cleaned_data = super().clean()
        print("cleaned data %s" %cleaned_data)
        date = cleaned_data.get("date")
        print("date %s" %date)
        file = cleaned_data.get("file")
        print("file %s" %file)

        #if 2000 >= date[:4] >= int(datetime.now().year) and date[5:7] not in range(1, 13):
        #    print("validation_date FALSE")
        #    raise ValidationError("chyba")

        print("return cleaned data")
        return cleaned_data



class FormDateAndUpload(forms.Form):
    #date = forms.DateField(widget=forms.TextInput(attrs={'type': 'month'}), help_text="vyberte měsíc a rok")
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'month'}), help_text="vyberte měsíc a rok")
    date1 = forms.CharField(max_length=50)
    start_date = forms.DateField(label="Start date",
                                 initial=timezone.now().date(),
                                 input_formats=['%Y/%m/%d'],
                                 widget=forms.DateInput(format='%Y/%m/%d'))

    #file = forms.FileField(label='Select a file', help_text='max. 42 megabytes')


    def clean(self):
        cleaned_data = super().clean()
        print("cleaned_data-%s" %cleaned_data)
        #date = cleaned_data.get('date')
        date1 = cleaned_data.get('date1')
        start_date = cleaned_data.get('start_date')
        print( date1, start_date)
        #file = cleaned_data.get('file')
        if not date1:
            raise forms.ValidationError('You have to write something!')
        return cleaned_data


    def clean_date(self):
        data = self.cleaned_data['date']
        #print("printing-%s" %data)

        return data

