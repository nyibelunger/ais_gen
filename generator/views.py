from datetime import datetime
from django.http import HttpResponse
from .models import Document
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.cache import cache
import pandas as pd
from io import BytesIO
import xlsxwriter
import unicodedata
from .ais_file import Generate_for_all
from django.shortcuts import render
from .forms import UploadFileForm, UploadDateForm,FormDateAndUpload

import requests
from django.conf import settings


def home(request):

    def validate_input(date_input):
        valid = False
        try:
            date_input_year = int(date_input[:4])
            date_input_month = int(date_input[5:7])
            date_input_dict = {"month":date_input_month, "year":date_input_year}
            request.session["date_input_final"] = date_input_dict
            valid = True
        except ValueError:
            valid = False
        return valid, date_input_dict

    if request.method == 'POST':
        form = FormDateAndUpload(request.POST)
        print(request.POST.get('date', None))
        date_input = request.POST.get('date', None)

        #if form.is_valid():
        if validate_input(date_input):
            print("date input - %s" %date_input)
            print("validate")

            return render(request, 'ais_gen/input_excel.html')
    else:
        form = FormDateAndUpload()
        print("not valid")
    return render(request, 'ais_gen/home.html', {'form': form})

def upload_date(request):
    """view pro input data"""
    date_form = UploadDateForm(request.POST)
    return render(request, 'ais_gen/input_date.html', {'date_form': date_form})

def input_date(request):
    """
    grabne vložený datum a posuneho do input_excel()
    :param request:
    :return:
    """

    def validate_input(date_input):
        #global date_input_year, date_input_month
        valid = False
        try:
            date_input_year = int(date_input[:4])
            date_input_month = int(date_input[5:7])
            date_input_dict = {"month": date_input_month, "year": date_input_year}
            request.session["date_input_final"] = date_input_dict
            if 2000 <= date_input_year <= int(datetime.now().year) and date_input_month in range(1, 13):
                valid = True
        except ValueError:
            raise ValidationError("Špatný formát datumu")
        return valid, date_input_year, date_input_month


    if request.method == 'POST':
        form = UploadDateForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['file'], doc_date=request.POST['date'])
            validation = validate_input(newdoc.doc_date)
            if validation[0]:
                ''' Begin reCAPTCHA validation '''
                recaptcha_response = request.POST.get('g-recaptcha-response')
                data = {
                    'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                    'response': recaptcha_response
                }
                r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
                result = r.json()
                ''' End reCAPTCHA validation '''
                if result['success']:
                    try:
                        novy_objekt = Generate_for_all(newdoc.docfile, validation[1], validation[2])
                        user_select = novy_objekt.gen_ais_all()
                        cache.set("user_select", user_select, 60)

                        # Redirect to the document list after POST
                        return render(request, 'ais_gen/user_selection.html', {'user_select': user_select})
                    except:
                        messages.error(request, 'Chyba, špatné datum nebo soubor.')
                        return render(request, 'ais_gen/input_date.html')
                else:
                    messages.error(request, 'Invalid reCAPTCHA. Please try again.')
        else:
            messages.error(request, "Pravděpodobně špatně zadané datum")

def input_excel(request):
    #global user_select
    cele_datum = request.session["date_input_final"]
    if request.method == 'POST':
        #print("cele_datum: %s" % cele_datum)
        date_input_month = cele_datum["month"]
        date_input_year = cele_datum["year"]
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['file'])
            print("type: %s" %type(newdoc.docfile))
            try:
                novy_objekt = Generate_for_all(newdoc.docfile, date_input_year, date_input_month)
                user_select = novy_objekt.gen_ais_all()
                cache.set("user_select", user_select, 60)

                # Redirect to the document list after POST
                return render(request, 'ais_gen/user_selection.html', {'user_select':user_select})
            except:
                return render(request, 'ais_gen/input_excel.html')
        else:
            #form = DocumentForm()  # A empty, unbound form
            print("else:form - ok")
            return render(request, 'ais_gen/input_excel.html')

            # Load documents for the list page
        #documents = Document.objects.all()

        # Render list page with the documents and the form
        return render(request, 'ais_gen/input_excel.html')

def render_sel_us_ais(request):
    """
    view pro vygenerování xlsx souboru pro daného zaměstnance.
    :param request:
    :return:
    """
    uzivatel =  request.POST.get('zamestnanec', None)

    excel_file = BytesIO()
    uzivatel_pd = cache.get("user_select")[uzivatel]
    xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    uzivatel_pd.to_excel(xlwriter, sheet_name='Sheet1')

    xlwriter.save()
    xlwriter.close()

    excel_file.seek(0)
    #name = uzivatel

    filename = "ais" + "_" + uzivatel.split()[1] + "_" + str(request.session["date_input_final"]["year"]) + "_" + str(request.session["date_input_final"]["month"])
    normal_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode('UTF-8').lower()

    response = HttpResponse(excel_file.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # set the file name in the Content-Disposition header
    response['Content-Disposition'] = 'attachment; filename=%s.xlsx' %normal_filename

    return response


def upload(request):
    form = UploadFileForm(request.POST, request.FILES)
    return render(request, 'ais_gen/input_excel.html', {'form': form})


class IndexView(generic.ListView):
    template_name = 'ais_gen/index.html'
    context_object_name ='latest_question_list'

def index(request):
    return render(request, 'ais_gen/index.html')


def generator_ais(request):
    return HttpResponse("Vyberte požadovaný měsíc a vepište Vaše služby.")