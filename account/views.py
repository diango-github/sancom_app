from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import (
     get_user_model, logout as auth_logout,
)
from .forms import UserCreateForm
from .models import User, File, Dictionary
import openpyxl
import os
from config.settings import BASE_DIR
from sancom_free.forms import Excel_link

User = get_user_model()

class Top(generic.TemplateView):
    params = {
        'visiter':''
    }

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            id = str(self.request.user.id)
            user_name= self.request.user.get_username()

            #file = File()
            #file.owner = User.objects.filter(email=user_name).first()
            #file.filename1 = 'SancomContents_' + id + '.xlsx'
            #wb=openpyxl.load_workbook(BASE_DIR + '/static/SancomContents.xlsx')
            #wb.save(BASE_DIR + '/static/' + file.filename1)
            #file.save()

            if user_name == "oz5java@gyahoo.co.jp":
                filename = 'SancomContents.xlsx'
                sheet = 'sheet1'
                excel = Excel_link(filename, sheet)
                excel_list = excel.getlist()
                verb_dic = excel_list[0]
                verb_list = excel_list[1]
                
                #dictionary = Dictionary.objects.all()
                #dictionary.delete()
                for i in range(len(verb_list)):
                    dictionary = Dictionary.objects.get(id=541+i)
                    dictionary.item=verb_list[i]
                    dictionary.category=verb_dic[verb_list[i]]["category"]
                    dictionary.japanese=verb_dic[verb_list[i]]["japanese"]
                    dictionary.english= verb_dic[verb_list[i]]["english"]
                    dictionary.esound= "sancom_free/sound/" + verb_dic[verb_list[i]]["esound"]
                    dictionary.chinese= verb_dic[verb_list[i]]["chinese"]
                    dictionary.csound= "sancom_free/sound/" + verb_dic[verb_list[i]]["csound"]
                    dictionary.save()
                    #dictionary = Dictionary.objects.create(item=verb_list[i], category= verb_dic[verb_list[i]]["category"], japanese= verb_dic[verb_list[i]]["japanese"], english= verb_dic[verb_list[i]]["english"], esound= "sancom_free/sound/" + verb_dic[verb_list[i]]["esound"], chinese= verb_dic[verb_list[i]]["chinese"], csound= "sancom_free/sound/" + verb_dic[verb_list[i]]["csound"])
                    #dictionary = Dictionary(item=verb_list[i], category= verb_dic[verb_list[i]]["category"], japanese= verb_dic[verb_list[i]]["japanese"], english= verb_dic[verb_list[i]]["english"], esound= "sancom_free/sound/" + verb_dic[verb_list[i]]["esound"], chinese= verb_dic[verb_list[i]]["chinese"], csound= "sancom_free/sound/" + verb_dic[verb_list[i]]["csound"])
                    #dictionary.save()

            self.params['visiter'] = user_name
        return render(self.request,'index.html', self.params)

class SignUpView(generic.CreateView):
    form_class = UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class ProfileView(LoginRequiredMixin, generic.View):

    def get(self, *args, **kwargs):
        return render(self.request,'registration/profile.html')


class DeleteView(LoginRequiredMixin, generic.View):

    def get(self, *args, **kwargs):
        user = User.objects.get(email=self.request.user.email)
        user.is_active = False
        user.save()
        auth_logout(self.request)
        return render(self.request,'registration/delete_complete.html')
