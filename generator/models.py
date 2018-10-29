import datetime
import os

from django.db import models
from django.utils import timezone


# class Question(models.Model):
#     # to be deleted
#     question_text = models.CharField(max_length=200)
#     pub_date = models.DateTimeField('date published')
#
#     def __str__(self):
#         return self.question_text
#
#     def was_published_recently(self):
#         now = timezone.now()
#         return  now - datetime.timedelta(days=1) <= self.pub_date <= now
#
# class Choice(models.Model):
#     # to be deleted
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
#
#     def __str__(self):
#         return self.choice_text
#
#
# class User_input(models.Model):
#     # to be deleted
#     usr_input = models.CharField(max_length=200)
#     usr_input_datum = models.DateField(auto_now_add=True, null=True)
#     #text_to_show = "Generátor AIS."
#     #list_test = uzivatele
#     #dict_test = dict(list(enumerate(list_test)))
#
#
#     def __str__(self):
#         return self.usr_input
#
#     def change_date(self):
#         self.usr_input_datum = models.DateField("2018-09-07")

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/')
    #doc_date = models.DateField(null=True)
    doc_date = models.CharField(max_length=60)

    def filename(self):
        return os.path.basename(self.docfile.name)