from typing import Counter
from config.settings import BASE_DIR
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib.auth.models import User
from account.models import File, Dictionary, Erepeat, Crepeat, E3sentences, C3sentences, Edeepen, Cdeepen, Efinish, Cfinish
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from .forms import Lan_appForm1, Excel_link, En_form1, En_form2, En_form3, En_form4, Ch_form1, Ch_form2, Ch_form3, Ch_form4, DeepenRadio, DeepenRadio2, FinishRadio, FinishRadio2
import openpyxl
import requests
from bs4 import BeautifulSoup
import sys
import wave
import numpy as np
import random
import datetime
from django.utils.datastructures import MultiValueDictKeyError
from django.core.paginator import Paginator
from django.db.models import Q


class Lan_appView2(TemplateView):
    def __init__(self):
        self.params = {
            'title':'一般公開コンテンツ',
            'message':'　',
            'form1':'',
            'item':'',
            'category':'',
            'english':'',
            'esound':'',
            'error':''
        }

    def get(self, request):
        global filename
        global sheet

        file = File.objects.filter(owner=request.user).first()
        filename = file.filename1
        sheet = 'sheet2'
        excel = Excel_link(filename, sheet)
        excel_list = excel.getlist()
        form1 = Lan_appForm1(filename, sheet)
        form1.fields['choice1'].choices = excel_list[2]
        self.params['form1'] = form1
        return render(request, 'sancom_free/publiccontents.html', self.params)

    def post(self, request):
        global item
        global category
        global english
        global esound
        global filename
        global filename

        if 'start' in request.POST:
            file = File.objects.filter(owner=request.user).first()
            filename = file.filename1
            sheet = 'sheet2'
            excel = Excel_link(filename, sheet)
            excel_list = excel.getlist()
            verb_dic = excel_list[0]
            try:
                ch1 = request.POST['choice1']
            except MultiValueDictKeyError:
                self.params['error'] = 'コンテンツを選択してください。'
                return render(request, 'sancom_free/publiccontents.html', self.params)
            item=ch1            
            category = verb_dic[item]["category"]
            english = verb_dic[item]["english"] 
            esound = "sancom_free/sound/" + verb_dic[item]["esound"]
            self.params['item'] = item             
            self.params['category'] = category
            self.params['english'] = english
            self.params['esound'] = esound
            self.params['form1'] = Lan_appForm1(filename, sheet, request.POST)
            return render(request, 'sancom_free/publiccontents.html', self.params)

        if 'scraping' in request.POST:
            file = File.objects.filter(owner=request.user).first()
            filename = file.filename1
            sheet = 'sheet2'
            word = request.POST['word']
            load_url1 = "https://ejje.weblio.jp/content/" + word
            html = requests.get(load_url1)
            try:
                soup1 = BeautifulSoup(html.content, "html.parser")
                pronouciation = soup1.find(class_="phoneticEjjeDesc").text
                meaning = soup1.find(class_="content-explanation ej").text
            except AttributeError:
                self.params['error'] = '辞書内に' + word + 'はありませんでした。'
                self.params['item'] = item
                self.params['category'] = category
                self.params['english'] = english
                self.params['esound'] = esound    
                self.params['form1'] = Lan_appForm1(filename, sheet, request.POST)                        
                return render(request, 'sancom_free/publiccontents.html', self.params)
            self.params['item'] = item
            self.params['category'] = category           
            self.params['english'] = english
            self.params['esound'] = esound
            self.params['word'] = word
            self.params['pronWeblio'] = pronouciation
            self.params['meaningWeblio'] = meaning
            self.params['form1'] = Lan_appForm1(filename, sheet, request.POST)   
            return render(request, 'sancom_free/publiccontents.html', self.params)

        if 'split' in request.POST:
            file = File.objects.filter(owner=request.user).first()
            filename = file.filename1
            sheet = 'sheet2'            
            start_position = request.POST['start_position']
            end_position = request.POST['end_position']
            duration = request.POST['duration']
            #sound = './static/' + esound
            sound = BASE_DIR + '/static/' + esound
            in_wav = wave.Wave_read(sound)
            nchannels, sampwidth, framerate, nframes, comptype, compname = in_wav.getparams()
            st = float(start_position)/float(duration)
            en = float(end_position)/float(duration)
            start = int(st*float(nframes))  #開始位置の処理
            end   = int(en*float(nframes))  #終了位置の処理
            data = in_wav.readframes(nframes)
            tmp_data = np.frombuffer(data, dtype='int16')
            x = tmp_data[start*nchannels:end*nchannels] #切り出し
            #出力ファイル書き込み
            id = str(self.request.user.id)
            #newsound = './static/sancom_free/sound/sound_' + id + '.wav'
            newsound = BASE_DIR + '/static/sancom_free/sound/sound_' + id + '.wav'
            out_wav = wave.Wave_write(newsound)
            nframes = x.size//nchannels
            out_wav.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
            out_wav.writeframes(x)
            in_wav.close()
            out_wav.close()
            self.params['item'] = item
            self.params['category'] = category
            self.params['english'] = english
            self.params['esound'] = esound
            self.params['sound_splited'] = 'sancom_free/sound/sound_' + id +'.wav'
            self.params['start'] = start_position
            self.params['length'] = duration
            self.params['end'] = end_position
            self.params['finish_comment'] = "以下に分割ファイルを作成しました。" 
            self.params['form1'] = Lan_appForm1(filename, sheet, request.POST)            
            return render(request, 'sancom_free/publiccontents.html', self.params) 

def business (request, num=1):
    dictionary = Dictionary.objects.all()
    page = Paginator(dictionary, 10)
    params = {
        'login_user': request.user,
        'data': page.get_page(num),
    }
    return render(request, 'sancom_free/business.html', params)

def econtents (request, id):
    contents = Dictionary.objects.get(id=id)
    params = {
        'contents': contents,
    }
    return render(request, 'sancom_free/econtents.html', params)

def erepeat (request, id):
        params = {
            'contents':'',
            'message':'',
        }
        #POST送信時の処理        
        if request.method == 'POST':
            contents = Dictionary.objects.get(id=id)
            cnt = Erepeat.objects.filter(owner=request.user).filter(dictionary=contents).count()
            if cnt == 0:
                e_repeat= Erepeat(owner=request.user, dictionary=contents)
                e_repeat.save()
                params['message'] = '暗唱訓練BOXに登録しました'
            else:
                params['message'] = '既に暗唱訓練BOXに登録されています'
            params['contents'] = contents
        #GETアクセス時の処理
        else:
            contents = Dictionary.objects.get(id=id)
            params['contents'] = contents               
        return render(request, 'sancom_free/erepeat.html', params)

def escraper (request, id):
        params = {
            'contents':'',
            'word':'',
            'pronWeblio':'',
            'meaningWeblio':'',
            'error':''
        }
        #POST送信時の処理        
        if request.method == 'POST':
            contents = Dictionary.objects.get(id=id)
            if 'scraping' in request.POST:
                word = request.POST['word']
                load_url1 = "https://ejje.weblio.jp/content/" + word
                html = requests.get(load_url1)
                try:
                    soup1 = BeautifulSoup(html.content, "html.parser")
                    pronouciation = soup1.find(class_="phoneticEjjeDesc").text
                    meaning = soup1.find(class_="content-explanation ej").text
                except AttributeError:
                    params['error'] = '辞書内に' + word + 'はありませんでした。'
                    params['contents'] = contents
                    return render(request, 'sancom_free/escraper.html', params)
                params['contents'] = contents
                params['word'] = word
                params['pronWeblio'] = pronouciation
                params['meaningWeblio'] = meaning
        #GETアクセス時の処理
        else:
            contents = Dictionary.objects.get(id=id)
            params['contents'] = contents              
        return render(request, 'sancom_free/escraper.html', params) 

def eseparate (request, id):
        params = {
            'contents':'',
            'start':'',
            'length':'',
            'end':'',
            'finish_comment':'(未作成)',
        }
        #POST送信時の処理        
        if request.method == 'POST':
            contents = Dictionary.objects.get(id=id)
            start_position = request.POST['start_position']
            end_position = request.POST['end_position']
            duration = request.POST['duration']
            sound = BASE_DIR + '/static/' + contents.esound
            in_wav = wave.Wave_read(sound)
            nchannels, sampwidth, framerate, nframes, comptype, compname = in_wav.getparams()
            st = float(start_position)/float(duration)
            en = float(end_position)/float(duration)
            start = int(st*float(nframes))  #開始位置の処理
            end   = int(en*float(nframes))  #終了位置の処理
            data = in_wav.readframes(nframes)
            tmp_data = np.frombuffer(data, dtype='int16')
            x = tmp_data[start*nchannels:end*nchannels] #切り出し
            #出力ファイル書き込み
            tag = str(request.user.id)
            newsound = BASE_DIR + '/static/sancom_free/sound/splite/sound_' + tag + '.wav'
            out_wav = wave.Wave_write(newsound)
            nframes = x.size//nchannels
            out_wav.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
            out_wav.writeframes(x)
            in_wav.close()
            out_wav.close()
            params['contents'] = contents
            params['sound_splited'] = 'sancom_free/sound/splite/sound_' + tag +'.wav'
            params['start'] = start_position
            params['length'] = duration
            params['end'] = end_position
            params['finish_comment'] = "(再生可能)"
        #GETアクセス時の処理
        else:
            contents = Dictionary.objects.get(id=id)
            params['contents'] = contents              
        return render(request, 'sancom_free/eseparate.html', params) 

def ccontents (request, id):
    contents = Dictionary.objects.get(id=id)
    params = {
        'contents': contents,
    }
    return render(request, 'sancom_free/ccontents.html', params)

def crepeat (request, id):
        params = {
            'contents':'',
            'message':'',
        }
        #POST送信時の処理        
        if request.method == 'POST':
            contents = Dictionary.objects.get(id=id)
            cnt = Crepeat.objects.filter(owner=request.user).filter(dictionary=contents).count()
            if cnt == 0:
                c_repeat= Crepeat(owner=request.user, dictionary=contents)
                c_repeat.save()
                params['message'] = '暗唱訓練BOXに登録しました'
            else:
                params['message'] = '既に暗唱訓練BOXに登録されています'
            params['contents'] = contents
        #GETアクセス時の処理
        else:
            contents = Dictionary.objects.get(id=id)
            params['contents'] = contents               
        return render(request, 'sancom_free/crepeat.html', params)

def cscraper (request, id):
        params = {
            'contents':'',
            'word':'',
            'pronWeblio':'',
            'meaningWeblio':'',
            'error':''
        }
        #POST送信時の処理        
        if request.method == 'POST':
            contents = Dictionary.objects.get(id=id)
            if 'scraping' in request.POST:
                word = request.POST['word']
                load_url1 = "https://zh.hatsuon.info/word/" + word
                html = requests.get(load_url1)
                try:
                    soup1 = BeautifulSoup(html.content, "html.parser")
                    pronouciation = soup1.find('div', class_="font4").text
                    meaning = soup1.find('div', class_="font1").text
                except AttributeError:
                    params['error'] = '辞書内に' + word + 'はありませんでした。'
                    params['contents'] = contents
                    return render(request, 'sancom_free/cscraper.html', params)
                params['contents'] = contents
                params['word'] = word
                params['pronWeblio'] = pronouciation
                params['meaningWeblio'] = meaning
        #GETアクセス時の処理
        else:
            contents = Dictionary.objects.get(id=id)
            params['contents'] = contents              
        return render(request, 'sancom_free/cscraper.html', params) 

def cseparate (request, id):
        params = {
            'contents':'',
            'start':'',
            'length':'',
            'end':'',
            'finish_comment':'(未作成)',
        }
        #POST送信時の処理        
        if request.method == 'POST':
            contents = Dictionary.objects.get(id=id)
            start_position = request.POST['start_position']
            end_position = request.POST['end_position']
            duration = request.POST['duration']
            sound = BASE_DIR + '/static/' + contents.csound
            in_wav = wave.Wave_read(sound)
            nchannels, sampwidth, framerate, nframes, comptype, compname = in_wav.getparams()
            st = float(start_position)/float(duration)
            en = float(end_position)/float(duration)
            start = int(st*float(nframes))  #開始位置の処理
            end   = int(en*float(nframes))  #終了位置の処理
            data = in_wav.readframes(nframes)
            tmp_data = np.frombuffer(data, dtype='int16')
            x = tmp_data[start*nchannels:end*nchannels] #切り出し
            #出力ファイル書き込み
            tag = str(request.user.id)
            newsound = BASE_DIR + '/static/sancom_free/sound/splite/sound_' + tag + '.wav'
            out_wav = wave.Wave_write(newsound)
            nframes = x.size//nchannels
            out_wav.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
            out_wav.writeframes(x)
            in_wav.close()
            out_wav.close()
            params['contents'] = contents
            params['sound_splited'] = 'sancom_free/sound/splite/sound_' + tag +'.wav'
            params['start'] = start_position
            params['length'] = duration
            params['end'] = end_position
            params['finish_comment'] = "(再生可能)"
        #GETアクセス時の処理
        else:
            contents = Dictionary.objects.get(id=id)
            params['contents'] = contents              
        return render(request, 'sancom_free/cseparate.html', params) 

def trainingbox(request):
    params = {
        'en_form1':'',
        'ch_form1':'',
        'en_form2':'',
        'ch_form2':'',
        'en_form3':'',
        'ch_form3':'',
        'en_form4':'',
        'ch_form4':'',
        }
    e1list_all = []
    e1list_target1 = []
    e1list_finish = []
    e2list_all = []
    e2list_target2 = []
    e3list_all = []
    e3list_target3 = []
    e4list_all = []
    en_list1 = []
    en_list2 = []
    en_list3 = []
    en_list4 = []
    e1object = {}
    c1list_all = []
    c1list_target1 = []
    c1list_finish = []
    c2list_all = []
    c2list_target2 = []
    c3list_all = []
    c3list_target3 = []
    c4list_all = []
    ch_list1 = []
    ch_list2 = []
    ch_list3 = []
    ch_list4 = []
    c1object = {}
    erepeat = Erepeat.objects.filter(owner=request.user).order_by('dictionary')
    crepeat = Crepeat.objects.filter(owner=request.user).order_by('dictionary')
    e3sentences = E3sentences.objects.filter(owner=request.user).order_by('dictionary')
    c3sentences = C3sentences.objects.filter(owner=request.user).order_by('dictionary')
    edeepen = Edeepen.objects.filter(owner=request.user).order_by('dictionary')
    cdeepen = Cdeepen.objects.filter(owner=request.user).order_by('dictionary')
    efinish = Efinish.objects.filter(owner=request.user).order_by('dictionary')
    cfinish = Cfinish.objects.filter(owner=request.user).order_by('dictionary')
    for item in erepeat:
        key = item.dictionary.item
        day = item.date
        if key not in e1list_all:
            e1list_all.append(key)
            e1object.setdefault(key,[day])
        else:
            e1object[key].append(day)
    for key in e1list_all:
        if len(e1object[key]) <= 2:
            e1list_target1.append(key)
        if len(e1object[key]) == 3:
            e1list_finish.append(key)
    for item in e3sentences:
        key = item.dictionary.item
        e2list_all.append(key)
    for key in e1list_finish:
        if key not in e2list_all:
            e2list_target2.append(key)
    for item in edeepen:
        key = item.dictionary.item
        if key not in e3list_all:
            e3list_all.append(key)
    for item in efinish:
        key = item.dictionary.item
        if key not in e4list_all:
            e4list_all.append(key)
    for key in e3list_all:
        if key not in e4list_all:
            e3list_target3.append(key)
    for i in range(len(e1list_target1)):
        en_list1.append((e1list_target1[i], e1list_target1[i]))
    for i in range(len(e2list_target2)):
        en_list2.append((e2list_target2[i], e2list_target2[i]))
    for i in range(len(e3list_target3)):
        en_list3.append((e3list_target3[i], e3list_target3[i]))
    for i in range(len(e4list_all)):
        en_list4.append((e4list_all[i], e4list_all[i]))

    for item in crepeat:
        key = item.dictionary.item
        day = item.date
        if key not in c1list_all:
            c1list_all.append(key)
            c1object.setdefault(key,[day])
        else:
            c1object[key].append(day)
    for key in c1list_all:
        if len(c1object[key]) <= 2:
            c1list_target1.append(key)
        if len(c1object[key]) == 3:
            c1list_finish.append(key)
    for item in c3sentences:
        key = item.dictionary.item
        c2list_all.append(key)
    for key in c1list_finish:
        if key not in c2list_all:
            c2list_target2.append(key)
    for item in cdeepen:
        key = item.dictionary.item
        if key not in c3list_all:
            c3list_all.append(key)
    for item in cfinish:
        key = item.dictionary.item
        if key not in c4list_all:
            c4list_all.append(key)
    for key in c3list_all:
        if key not in c4list_all:
            c3list_target3.append(key)
    for i in range(len(c1list_target1)):
        ch_list1.append((c1list_target1[i], c1list_target1[i]))
    for i in range(len(c2list_target2)):
        ch_list2.append((c2list_target2[i], c2list_target2[i]))
    for i in range(len(c3list_target3)):
        ch_list3.append((c3list_target3[i], c3list_target3[i]))
    for i in range(len(c4list_all)):
        ch_list4.append((c4list_all[i], c4list_all[i]))
    en_form1 = En_form1(en_list1)
    en_form2 = En_form1(en_list2)
    en_form3 = En_form1(en_list3)
    en_form4 = En_form1(en_list4)
    ch_form1 = Ch_form1(ch_list1)
    ch_form2 = Ch_form1(ch_list2)
    ch_form3 = Ch_form1(ch_list3)
    ch_form4 = Ch_form1(ch_list4)
    params['en_form1'] = en_form1
    params['en_form2'] = en_form2
    params['en_form3'] = en_form3
    params['en_form4'] = en_form4
    params['ch_form1'] = ch_form1
    params['ch_form2'] = ch_form2
    params['ch_form3'] = ch_form3
    params['ch_form4'] = ch_form4
    return render(request, 'sancom_free/trainingbox.html', params)

def en_repeat_list(request):
    elist = []
    dlist = []
    object = {}
    erepeat = Erepeat.objects.filter(owner=request.user).order_by('dictionary')
    for item in erepeat:
        key = item.dictionary.id
        day =item.date
        if key not in elist:
            elist.append(key)
            object.setdefault(key,[day])
        else:
            object[key].append(day)
    for key in elist:
        if len(object[key]) == 3:
            object.pop(key)
    dlist = list(object.keys())
    for key in dlist:
        if len(object[key]) == 1:
            object[key].append("NEXT")
            object[key].append("")
        if len(object[key]) == 2:
            object[key].append("NEXT")
    params = {
        'object':object,
    }
    return render(request, 'sancom_free/en_repeat_list.html', params)

def en_repeat (request, id):
        params = {
            'contents':'',
            'message':'',
        }
        #POST送信時の処理        
        if request.method == 'POST':
            contents = Dictionary.objects.get(id=id)
            e_repeat= Erepeat(owner=request.user, dictionary=contents)
            e_repeat.save()
            cnt = Erepeat.objects.filter(owner=request.user).filter(dictionary=contents).count()
            if cnt == 3:
                params['message'] = '３回目が終了して、３文訓練に登録されました)'
            else:
                params['message'] = '２回目が終了しました'
            params['contents'] = contents
        #GETアクセス時の処理
        else:
            contents = Dictionary.objects.get(id=id)
            params['contents'] = contents               
        return render(request, 'sancom_free/en_repeat.html', params)

def ch_repeat_list(request):
    elist = []
    dlist = []
    object = {}
    crepeat = Crepeat.objects.filter(owner=request.user).order_by('dictionary')
    for item in crepeat:
        key = item.dictionary.id
        day =item.date
        if key not in elist:
            elist.append(key)
            object.setdefault(key,[day])
        else:
            object[key].append(day)
    for key in elist:
        if len(object[key]) == 3:
            object.pop(key)
    dlist = list(object.keys())
    for key in dlist:
        if len(object[key]) == 1:
            object[key].append("NEXT")
            object[key].append("")
        if len(object[key]) == 2:
            object[key].append("NEXT")
    params = {
        'object':object,
    }
    return render(request, 'sancom_free/ch_repeat_list.html', params)

def ch_repeat (request, id):
        params = {
            'contents':'',
            'message':'',
        }
        #POST送信時の処理        
        if request.method == 'POST':
            contents = Dictionary.objects.get(id=id)
            c_repeat= Crepeat(owner=request.user, dictionary=contents)
            c_repeat.save()
            cnt = Crepeat.objects.filter(owner=request.user).filter(dictionary=contents).count()
            if cnt == 3:
                params['message'] = '３回目が終了して、３文訓練に登録されました)'
            else:
                params['message'] = '２回目が終了しました'
            params['contents'] = contents
        #GETアクセス時の処理
        else:
            contents = Dictionary.objects.get(id=id)
            params['contents'] = contents               
        return render(request, 'sancom_free/ch_repeat.html', params)

class en_3sentences(TemplateView):
    def __init__(self):
        self.params = {
            'sentences':'',
            'message':'',
            'message1':'',
            'dictionary_choiced':'',
            'message2':'',
            'message3':'',
            'message4':'',
            'message5':'',
        }
        
    def get(self, request):
        language = "english"
        en_list2 = get_sentences_list(request.user, language)
        if len(en_list2) == 3:  
            self.params['sentences'] = en_list2
            self.params['message'] = "この３文例で訓練を開始します。計３０回行います。"
            self.params['message1'] = "message1"
        else:
            self.params['sentences'] = ""
            self.params['message'] = "訓練に必要な３文例以上を確保してください"
            self.params['message1'] = ""              
        return render(request, 'sancom_free/en_3sentences.html', self.params)

    def post(self, request):
        global dictionary_choiced
        global count
        list = []
        language = "english"
        en_list2 = get_sentences_list(request.user, language)
        if 'start' in request.POST:
            count=1
            dictionary_choiced = random.choice(en_list2)
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['message'] = ""
            self.params['message1'] = ""
            self.params['message2'] = "message2"
        if 'verify' in request.POST:
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['message'] = ""
            self.params['message1'] = ""
            self.params['message2'] = "message2"
            self.params['message3'] = "message3"
        elif 'next' in request.POST:
            count = count + 1
            list = en_list2
            list.remove(dictionary_choiced)
            dictionary_choiced = random.choice(list)
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['message'] = ""
            self.params['message1'] = ""
            self.params['message2'] = "message2"
            self.params['message3'] = ""
            if count >29:
                self.params['message4'] = "規定回数に到達しました"
            else:
                self.params['message4'] = ""                 
        if 'register' in request.POST:
            for item in en_list2:
                e_3sentences= E3sentences(owner=request.user, dictionary=item)
                e_3sentences.save()
                e_deepen = Edeepen(owner=request.user, dictionary=item, status=0)
                e_deepen.save()
            self.params['message'] = ""                 
            self.params['message1'] = ""
            self.params['message2'] = ""
            self.params['message3'] = ""                 
            self.params['message4'] = ""
            self.params['message5'] = "３文例 を「記憶深化」へ登録しました"
        return render(request, 'sancom_free/en_3sentences.html', self.params)    

class ch_3sentences(TemplateView):
    def __init__(self):
        self.params = {
            'sentences':'',
            'message':'',
            'message1':'',
            'dictionary_choiced':'',
            'message2':'',
            'message3':'',
            'message4':'',
            'message5':'',
        }
        
    def get(self, request):
        language = "chinese"
        en_list2 = get_sentences_list(request.user, language)
        if len(en_list2) == 3:  
            self.params['sentences'] = en_list2
            self.params['message'] = "この３文例で訓練を開始します。計３０回行います。"
            self.params['message1'] = "message1"
        else:
            self.params['sentences'] = ""
            self.params['message'] = "訓練に必要な３文例以上を確保してください"
            self.params['message1'] = ""              
        return render(request, 'sancom_free/ch_3sentences.html', self.params)

    def post(self, request):
        global dictionary_choiced
        global count
        list = []
        language = "chinese"
        en_list2 = get_sentences_list(request.user, language)
        if 'start' in request.POST:
            count=1
            dictionary_choiced = random.choice(en_list2)
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['message'] = ""
            self.params['message1'] = ""
            self.params['message2'] = "message2"
        elif 'verify' in request.POST:
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['message'] = ""
            self.params['message1'] = ""
            self.params['message2'] = "message2"
            self.params['message3'] = "message3"
        elif 'next' in request.POST:
            count = count + 1
            list = en_list2
            list.remove(dictionary_choiced)
            dictionary_choiced = random.choice(list)
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['message'] = ""
            self.params['message1'] = ""
            self.params['message2'] = "message2"
            self.params['message3'] = ""
            if count >29:
                self.params['message4'] = "規定回数に到達しました"
            else:
                self.params['message4'] = ""                 
        if 'register' in request.POST:
            for item in en_list2:
                c_3sentences= C3sentences(owner=request.user, dictionary=item)
                c_3sentences.save()
                c_deepen = Cdeepen(owner=request.user, dictionary=item, status=0)
                c_deepen.save()
            self.params['message'] = ""                 
            self.params['message1'] = ""
            self.params['message2'] = ""
            self.params['message3'] = ""                 
            self.params['message4'] = ""
            self.params['message5'] = "３つの文例を「記憶深化」へ登録しました"
        return render(request, 'sancom_free/ch_3sentences.html', self.params) 

class en_deepen_list(TemplateView):
    def __init__(self):
        self.params = {
            'object':'',
            'form':'',
            'message1':'',
            'message2':'',
            'message3':'',
            'message4':'',
            'message5':'',
        }
        
    def get(self, request):
        date_nest1 = {}
        date_nest2 = {}
        language = "english"
        dictionary_list = get_deepen_list(request.user, language)
        for item in dictionary_list:
            target_objects = Edeepen.objects.filter(owner=request.user).filter(dictionary=item).order_by('date').reverse()
            cnt = target_objects.count()-1
            date_list1 = []
            date_list2 = []
            date_list1.append([cnt, 0])
            date_list2.append([cnt, 0])
            for object in target_objects:
                date_list1.append([object.date, object.status])
                status = object.status
                if status >0:
                    date_list2.append([str(object.date.month)+"月"+str(object.date.day)+"日", "レベル"+str(status)])
                else:
                    date_list2.append([str(object.date.month)+"月"+str(object.date.day)+"日", "登録"])
            date_nest1.setdefault(item, date_list1)
            date_nest2.setdefault(item, date_list2)
            date_nest1[item][0][1] = (datetime.date.today() - date_nest1[item][1][0]).days
            date_nest2[item][0][1] = (datetime.date.today() - date_nest1[item][1][0]).days
        self.params['form'] = DeepenRadio() 
        self.params['object'] = date_nest2
        return render(request, 'sancom_free/en_deepen_list.html', self.params)

    def post(self, request):
        date_nest1 = {}
        date_nest2 = {}
        language = "english"
        dictionary_list = get_deepen_list(request.user, language)
        for item in dictionary_list:
            target_objects = Edeepen.objects.filter(owner=request.user).filter(dictionary=item).order_by('date').reverse()
            cnt = target_objects.count()-1
            date_list1 = []
            date_list2 = []
            date_list1.append([cnt, 0])
            date_list2.append([cnt, 0])
            for object in target_objects:
                date_list1.append([object.date, object.status])
                status = object.status
                if status >0:
                    date_list2.append([str(object.date.month)+"月"+str(object.date.day)+"日", "レベル"+str(status)])
                else:
                    date_list2.append([str(object.date.month)+"月"+str(object.date.day)+"日", "登録"])
            date_nest1.setdefault(item, date_list1)
            date_nest2.setdefault(item, date_list2)
            date_nest1[item][0][1] = (datetime.date.today() - date_nest1[item][1][0]).days
            date_nest2[item][0][1] = (datetime.date.today() - date_nest1[item][1][0]).days

        sort_list1 = []
        sort_dic1 = {}
        dictionary_list1 = []
        date_nest_choice = {}
        ch = request.POST['choice']
        for item in dictionary_list:
            if(ch == '1'): 
                sort_dic1.setdefault(item, date_nest1[item][1][1])
                sort_list1 = sorted(sort_dic1.items(), key = lambda x : x[1])                
            elif(ch == '2'): 
                sort_dic1.setdefault(item, date_nest1[item][0][0])
                sort_list1 = sorted(sort_dic1.items(), key = lambda x : x[1])
            elif(ch == '3'):
                sort_dic1.setdefault(item, date_nest1[item][0][1])
                sort_list1 = sorted(sort_dic1.items(), reverse=True, key = lambda x : x[1])
        for i in range(len(sort_list1)):
            dictionary_list1.append(sort_list1[i][0])
        for item in dictionary_list1:
            date_nest_choice.setdefault(item, date_nest2[item])            
        self.params['object'] = date_nest_choice
        self.params['form'] = DeepenRadio(request.POST) 
        return render(request, 'sancom_free/en_deepen_list.html', self.params)       

class en_deepen(TemplateView):
    def __init__(self):
        self.params = {
            'record':'',
            'dictionary_choiced':'',
            'form':'',
            'message1':'',
            'message2':'',
            'message3':'',
            'message4':'',
            'message5':'',
        }
        
    def get(self, request):
        global id
        id = request.GET['id']
        dictionary_choiced = Dictionary.objects.get(id=id)
        records = Edeepen.objects.filter(owner=request.user).filter(dictionary=dictionary_choiced)

        self.params['dictionary_choiced'] = dictionary_choiced
        self.params['records'] = records
        self.params['form'] = DeepenRadio2()
        self.params['message1'] = "message1"              
        return render(request, 'sancom_free/en_deepen.html', self.params)

    def post(self, request):
        global dictionary_choiced
        dictionary_choiced = Dictionary.objects.get(id=id)
        if 'start' in request.POST:
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['form'] = DeepenRadio2()
            self.params['message1'] = ""
            self.params['message2'] = "message2"
            self.params['message3'] = ""
        elif 'verify' in request.POST:
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['form'] = DeepenRadio2()
            self.params['message1'] = ""
            self.params['message2'] = "message2"
            self.params['message3'] = "message3"
            self.params['message4'] = ""
        elif 'register' in request.POST:
            st = request.POST['choice']
            e_deepen = Edeepen(owner=request.user, dictionary=dictionary_choiced, status=st)
            e_deepen.save()
            records = Edeepen.objects.filter(owner=request.user).filter(dictionary=dictionary_choiced)
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['records'] = records
            self.params['message1'] = ""
            self.params['message2'] = ""
            self.params['message3'] = ""
            self.params['message4'] = "訓練履歴を追加しました"
        elif 'to_finish' in request.POST:
            e_finish = Efinish(owner=request.user, dictionary=dictionary_choiced, status=0)
            e_finish.save()
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['message1'] = ""
            self.params['message2'] = ""
            self.params['message3'] = ""
            self.params['message4'] = ""
            self.params['message5'] = "message5"           
        return render(request, 'sancom_free/en_deepen.html', self.params)

class en_finish(TemplateView):
    def __init__(self):
        self.params = {
            'dictionary_choiced':'',
            'form':'',
            'message1':'',
            'message2':'',
            'message3':'',
            'message4':'',
            'message5':'',
        }
        
    def get(self, request):
        self.params['form'] = FinishRadio()
        self.params['message1'] = "message1"              
        return render(request, 'sancom_free/en_finish.html', self.params)

    def post(self, request):
        global dictionary_choiced
        global list_choiced
        date_nest1 = {}
        language = "english"
        dictionary_list = get_finish_list(request.user, language)
        for item in dictionary_list:
            target_objects = Efinish.objects.filter(owner=request.user).filter(dictionary=item).order_by('date').reverse()
            date_list1 = []
            for object in target_objects:
                date_list1.append((datetime.date.today() - object.date).days)
            date_nest1.setdefault(item, date_list1[0])
        if 'extract' in request.POST:
            list1a = []
            list2a = []
            list1 = []
            list2 = []            
            list3 = []
            ch = request.POST['choice']
            for item in dictionary_list:
                if date_nest1[item] > 6:
                    list1a.append(item)
                elif date_nest1[item] > 30:
                    list2a.append(item)
                elif date_nest1[item] > 90:
                    list3.append(item)
            for item in list1a:
                if item not in list2a:
                    list1.append(item)
            for item in list2a:
                if item not in list3:
                    list2.append(item)
            if (ch == "1"):
                list_choiced = list1a
            if (ch == "2"):
                list_choiced = list2
            if (ch == "3"):
                list_choiced = list3
            if len(list_choiced) == 0:
                message2 = "該当する文例はありません"
            else:
                message2 = "全部で"+str(len(list_choiced))+"文例あります"                  
            self.params['message1'] = ""
            self.params['message2'] = message2
            self.params['message3'] = ""
        if 'start' in request.POST:
            dictionary_choiced = random.choice(list_choiced)
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['message1'] = ""
            self.params['message2'] = ""
            self.params['message3'] = "message3"
            self.params['message4'] = ""
        elif 'verify' in request.POST:
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['form'] = FinishRadio2()
            self.params['message1'] = ""
            self.params['message2'] = ""
            self.params['message3'] = "message3"
            self.params['message4'] = "message4"
        elif 'register' in request.POST:
            st = request.POST['choice']
            e_finish= Efinish(owner=request.user, dictionary=dictionary_choiced, status=st)
            e_finish.save()
            records = Efinish.objects.filter(owner=request.user).filter(dictionary=dictionary_choiced)
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['records'] = records
            self.params['message1'] = ""
            self.params['message2'] = ""
            self.params['message3'] = ""
            self.params['message4'] = ""
            self.params['message5'] = "確認履歴を追加しました"
        elif 'next' in request.POST:
            list_choiced.remove(dictionary_choiced)
            if len(list_choiced) == 0:
                self.params['message1'] = ""
                self.params['message2'] = ""
                self.params['message3'] = ""
                self.params['message4'] = ""
                self.params['message5'] = ""
                self.params['message6'] = "全ての文例の確認が終わりました"                
            else:
                dictionary_choiced = random.choice(list_choiced)
                self.params['dictionary_choiced'] = dictionary_choiced
                self.params['message1'] = ""
                self.params['message2'] = ""
                self.params['message3'] = "message3"
                self.params['message4'] = ""
                self.params['message5'] = "" 
        return render(request, 'sancom_free/en_finish.html', self.params)

class ch_deepen_list(TemplateView):
    def __init__(self):
        self.params = {
            'object':'',
            'form':'',
            'message1':'',
            'message2':'',
            'message3':'',
            'message4':'',
            'message5':'',
        }
        
    def get(self, request):
        date_nest1 = {}
        date_nest2 = {}
        language = "chinese"
        dictionary_list = get_deepen_list(request.user, language)
        for item in dictionary_list:
            target_objects = Cdeepen.objects.filter(owner=request.user).filter(dictionary=item).order_by('date').reverse()
            cnt = target_objects.count()-1
            date_list1 = []
            date_list2 = []
            date_list1.append([cnt, 0])
            date_list2.append([cnt, 0])
            for object in target_objects:
                date_list1.append([object.date, object.status])
                status = object.status
                if status >0:
                    date_list2.append([str(object.date.month)+"月"+str(object.date.day)+"日", "レベル"+str(status)])
                else:
                    date_list2.append([str(object.date.month)+"月"+str(object.date.day)+"日", "登録"])
            date_nest1.setdefault(item, date_list1)
            date_nest2.setdefault(item, date_list2)
            date_nest1[item][0][1] = (datetime.date.today() - date_nest1[item][1][0]).days
            date_nest2[item][0][1] = (datetime.date.today() - date_nest1[item][1][0]).days
        self.params['form'] = DeepenRadio() 
        self.params['object'] = date_nest2
        return render(request, 'sancom_free/ch_deepen_list.html', self.params)

    def post(self, request):
        date_nest1 = {}
        date_nest2 = {}
        language = "chinese"
        dictionary_list = get_deepen_list(request.user, language)
        for item in dictionary_list:
            target_objects = Cdeepen.objects.filter(owner=request.user).filter(dictionary=item).order_by('date').reverse()
            cnt = target_objects.count()-1
            date_list1 = []
            date_list2 = []
            date_list1.append([cnt, 0])
            date_list2.append([cnt, 0])
            for object in target_objects:
                date_list1.append([object.date, object.status])
                status = object.status
                if status >0:
                    date_list2.append([str(object.date.month)+"月"+str(object.date.day)+"日", "レベル"+str(status)])
                else:
                    date_list2.append([str(object.date.month)+"月"+str(object.date.day)+"日", "登録"])
            date_nest1.setdefault(item, date_list1)
            date_nest2.setdefault(item, date_list2)
            date_nest1[item][0][1] = (datetime.date.today() - date_nest1[item][1][0]).days
            date_nest2[item][0][1] = (datetime.date.today() - date_nest1[item][1][0]).days

        sort_list1 = []
        sort_dic1 = {}
        dictionary_list1 = []
        date_nest_choice = {}
        ch = request.POST['choice']
        for item in dictionary_list:
            if(ch == '1'): 
                sort_dic1.setdefault(item, date_nest1[item][1][1])
                sort_list1 = sorted(sort_dic1.items(), key = lambda x : x[1])                
            elif(ch == '2'): 
                sort_dic1.setdefault(item, date_nest1[item][0][0])
                sort_list1 = sorted(sort_dic1.items(), key = lambda x : x[1])
            elif(ch == '3'):
                sort_dic1.setdefault(item, date_nest1[item][0][1])
                sort_list1 = sorted(sort_dic1.items(), reverse=True, key = lambda x : x[1])
        for i in range(len(sort_list1)):
            dictionary_list1.append(sort_list1[i][0])
        for item in dictionary_list1:
            date_nest_choice.setdefault(item, date_nest2[item])            
        self.params['object'] = date_nest_choice
        self.params['form'] = DeepenRadio(request.POST) 
        return render(request, 'sancom_free/ch_deepen_list.html', self.params)       

class ch_deepen(TemplateView):
    def __init__(self):
        self.params = {
            'record':'',
            'dictionary_choiced':'',
            'form':'',
            'message1':'',
            'message2':'',
            'message3':'',
            'message4':'',
            'message5':'',
        }
        
    def get(self, request):
        global id
        id = request.GET['id']
        dictionary_choiced = Dictionary.objects.get(id=id)
        records = Cdeepen.objects.filter(owner=request.user).filter(dictionary=dictionary_choiced)

        self.params['dictionary_choiced'] = dictionary_choiced
        self.params['records'] = records
        self.params['form'] = DeepenRadio2()
        self.params['message1'] = "message1"              
        return render(request, 'sancom_free/ch_deepen.html', self.params)

    def post(self, request):
        global dictionary_choiced
        dictionary_choiced = Dictionary.objects.get(id=id)
        if 'start' in request.POST:
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['form'] = DeepenRadio2()
            self.params['message1'] = ""
            self.params['message2'] = "message2"
            self.params['message3'] = ""
        elif 'verify' in request.POST:
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['form'] = DeepenRadio2()
            self.params['message1'] = ""
            self.params['message2'] = "message2"
            self.params['message3'] = "message3"
            self.params['message4'] = ""
        elif 'register' in request.POST:
            st = request.POST['choice']
            c_deepen = Cdeepen(owner=request.user, dictionary=dictionary_choiced, status=st)
            c_deepen.save()
            records = Cdeepen.objects.filter(owner=request.user).filter(dictionary=dictionary_choiced)
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['records'] = records
            self.params['message1'] = ""
            self.params['message2'] = ""
            self.params['message3'] = ""
            self.params['message4'] = "訓練履歴を追加しました"
        elif 'to_finish' in request.POST:
            c_finish = Cfinish(owner=request.user, dictionary=dictionary_choiced, status=0)
            c_finish.save()
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['message1'] = ""
            self.params['message2'] = ""
            self.params['message3'] = ""
            self.params['message4'] = ""
            self.params['message5'] = "message5"           
        return render(request, 'sancom_free/ch_deepen.html', self.params)

class ch_finish(TemplateView):
    def __init__(self):
        self.params = {
            'dictionary_choiced':'',
            'form':'',
            'message1':'',
            'message2':'',
            'message3':'',
            'message4':'',
            'message5':'',
        }
        
    def get(self, request):
        self.params['form'] = FinishRadio()
        self.params['message1'] = "message1"              
        return render(request, 'sancom_free/ch_finish.html', self.params)

    def post(self, request):
        global dictionary_choiced
        global list_choiced
        date_nest1 = {}
        language = "chinese"
        dictionary_list = get_finish_list(request.user, language)
        for item in dictionary_list:
            target_objects = Cfinish.objects.filter(owner=request.user).filter(dictionary=item).order_by('date').reverse()
            date_list1 = []
            for object in target_objects:
                date_list1.append((datetime.date.today() - object.date).days)
            date_nest1.setdefault(item, date_list1[0])
        if 'extract' in request.POST:
            list1a = []
            list2a = []
            list1 = []
            list2 = []            
            list3 = []
            ch = request.POST['choice']
            for item in dictionary_list:
                if date_nest1[item] > 6:
                    list1a.append(item)
                elif date_nest1[item] > 30:
                    list2a.append(item)
                elif date_nest1[item] > 90:
                    list3.append(item)
            for item in list1a:
                if item not in list2a:
                    list1.append(item)
            for item in list2a:
                if item not in list3:
                    list2.append(item)
            if (ch == "1"):
                list_choiced = list1a
            if (ch == "2"):
                list_choiced = list2
            if (ch == "3"):
                list_choiced = list3
            if len(list_choiced) == 0:
                message2 = "該当する文例はありません"
            else:
                message2 = "全部で"+str(len(list_choiced))+"文例あります"                  
            self.params['message1'] = ""
            self.params['message2'] = message2
            self.params['message3'] = ""
        if 'start' in request.POST:
            dictionary_choiced = random.choice(list_choiced)
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['message1'] = ""
            self.params['message2'] = ""
            self.params['message3'] = "message3"
            self.params['message4'] = ""
        elif 'verify' in request.POST:
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['form'] = FinishRadio2()
            self.params['message1'] = ""
            self.params['message2'] = ""
            self.params['message3'] = "message3"
            self.params['message4'] = "message4"
        elif 'register' in request.POST:
            st = request.POST['choice']
            c_finish= Cfinish(owner=request.user, dictionary=dictionary_choiced, status=st)
            c_finish.save()
            records = Cfinish.objects.filter(owner=request.user).filter(dictionary=dictionary_choiced)
            self.params['dictionary_choiced'] = dictionary_choiced
            self.params['records'] = records
            self.params['message1'] = ""
            self.params['message2'] = ""
            self.params['message3'] = ""
            self.params['message4'] = ""
            self.params['message5'] = "確認履歴を追加しました"
        elif 'next' in request.POST:
            list_choiced.remove(dictionary_choiced)
            if len(list_choiced) == 0:
                self.params['message1'] = ""
                self.params['message2'] = ""
                self.params['message3'] = ""
                self.params['message4'] = ""
                self.params['message5'] = ""
                self.params['message6'] = "全ての文例の確認が終わりました"                
            else:
                dictionary_choiced = random.choice(list_choiced)
                self.params['dictionary_choiced'] = dictionary_choiced
                self.params['message1'] = ""
                self.params['message2'] = ""
                self.params['message3'] = "message3"
                self.params['message4'] = ""
                self.params['message5'] = "" 
        return render(request, 'sancom_free/ch_finish.html', self.params)

















def get_sentences_list(owner, language):
    e1list_all = []
    e1list_target1 = []
    e1list_finish = []
    e2list_all = []
    e2list_target2 = []
    e1object = {}
    dictionary_list = []
    if language == "english":
        repeat = Erepeat.objects.filter(owner=owner).order_by('dictionary')
        sentences = E3sentences.objects.filter(owner=owner).order_by('dictionary')
    if language == "chinese":
        repeat = Crepeat.objects.filter(owner=owner).order_by('dictionary')
        sentences = C3sentences.objects.filter(owner=owner).order_by('dictionary')
    for item in repeat:
        key = item.dictionary.id
        day = item.date
        if key not in e1list_all:
            e1list_all.append(key)
            e1object.setdefault(key,[day])
        else:
            e1object[key].append(day)
    for key in e1list_all:
        if len(e1object[key]) <= 2:
            e1list_target1.append(key)
        if len(e1object[key]) == 3:
            e1list_finish.append(key)
    for item in sentences:
        key = item.dictionary.id
        e2list_all.append(key)
    for key in e1list_finish:
        if key not in e2list_all:
            e2list_target2.append(key)
    if len(e2list_target2) >= 3:  
        dictionary1 = Dictionary.objects.get(id=e2list_target2[0])
        dictionary2 = Dictionary.objects.get(id=e2list_target2[1])
        dictionary3 = Dictionary.objects.get(id=e2list_target2[2])
        dictionary_list = [dictionary1, dictionary2, dictionary3]
    if len(e2list_target2) < 3:  
        dictionary_list = []    
    return dictionary_list

def get_deepen_list(owner, language):
    e3list_all = []
    e3list_target3 = []
    e4list_all = []
    dictionary_list = []
    if language == "english":
        deepen = Edeepen.objects.filter(owner=owner).order_by('dictionary')
        finish = Efinish.objects.filter(owner=owner).order_by('dictionary')
    if language == "chinese":
        deepen = Cdeepen.objects.filter(owner=owner).order_by('dictionary')
        finish = Cfinish.objects.filter(owner=owner).order_by('dictionary')
    for item in deepen:
        key = item.dictionary.id
        if key not in e3list_all:
            e3list_all.append(key)
    for item in finish:
        key = item.dictionary.id
        if key not in e4list_all:
            e4list_all.append(key)
    for key in e3list_all:
        if key not in e4list_all:
            e3list_target3.append(key)
    for key in e3list_target3:
        dictionary_list.append(Dictionary.objects.get(id=key))
    return dictionary_list

def get_finish_list(owner, language):
    e4list_all = []
    dictionary_list = []
    if language == "english":
        finish = Efinish.objects.filter(owner=owner).order_by('dictionary')
    if language == "chinese":
        finish = Cfinish.objects.filter(owner=owner).order_by('dictionary')
    for item in finish:
        key = item.dictionary.id
        if key not in e4list_all:
            e4list_all.append(key)
    for key in e4list_all:
        dictionary_list.append(Dictionary.objects.get(id=key))
    return dictionary_list
