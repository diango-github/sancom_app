from django.shortcuts import render
from django.shortcuts import redirect
#from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from account.models import User, Message, Friend, Group, Good
from .forms import GroupCheckForm, GroupSelectForm, FriendsForm, CreateGroupForm, PostForm, ImageForm, LanguageForm

import os
from google.cloud import translate_v3 as translate
from config.settings import BASE_DIR

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(BASE_DIR, 'token.json')
client = translate.TranslationServiceClient()
project_id = 'sancom-project-2022'
location = 'us-central1'
parent = f"projects/{project_id}/locations/{location}"

# indexのビュー関数
@login_required(login_url='/admin/login/')
def index(request, page=1):
    # publicのuserを取得
    (public_user, public_group) = get_public()

    transList = []

    # POST送信時の処理
    if request.method == 'POST':
        # Groupのチェックを更新したときの処理
        # フォームの用意
        checkform = GroupCheckForm(request.user, request.POST)
        #checkform = GroupSelectForm(request.user, request.POST)
        languageform = LanguageForm(request.POST)
        # チェックされたGroup名をリストにまとめる
        glist = []
        for item in request.POST.getlist('groups'):
            glist.append(item)
        # Messageの取得
        messages = get_your_group_message(request.user, glist, page)
        # Languageの取得
        ch = request.POST['choice']
        if (ch == "1"):
            target_language = 'ja'
        elif (ch == "2"):
            target_language = 'zh-CN'
        elif (ch == "3"):
            target_language = 'ko'
        elif (ch == "4"):
            target_language = 'en'
        elif (ch == "5"):
            target_language = 'fr'
        elif (ch == "6"):
            target_language = 'es'
        elif (ch == "7"):
            target_language = 'ru'

        # 多言語表示機能追加
        for message in messages:

            req = client.detect_language (
                parent = parent,
                content = message.content,
                mime_type = 'text/plain' )
            source_language = req.languages[0].language_code

            if (source_language != target_language):
                res = client.translate_text (
                    parent = parent,
                    contents = [message.content],
                    mime_type = 'text/plain',
                    source_language_code = source_language,
                    target_language_code = target_language )
                for translation in res.translations:
                    result = translation.translated_text
                    transList.append(result)
            else:
                transList.append(message.content)
        message1 = ""
        message2 = glist[0] + "グループの投稿"


    # GETアクセス時の処理
    else:
        # フォームの用意
        checkform = GroupCheckForm(request.user)
        #checkform = GroupSelectForm(request.user)
        languageform = LanguageForm()
        # Groupのリストを取得
        gps = Group.objects.filter(owner=request.user)
        glist = [public_group.title]
        for item in gps:
            glist.append(item.title)
        # メッセージの取得
        messages = get_your_group_message(request.user, glist, page)
        # message
        message1 = "※翻訳文はオレンジ色で表示されます"
        message2 = "一般投稿"

    # 共通処理
    params = {
        'login_user':request.user,
        'contents':messages,
        'check_form':checkform,
        'language_form':languageform,
        'trans_list':transList,
        'message1': message1,
        'message2': message2
    }
    return render(request, 'sns/index.html', params)

@login_required(login_url='/admin/login/')
def groups(request):
    # 自分が登録したFriendを取得
    friends = Friend.objects.filter(owner=request.user)

    # POST送信時の処理
    if request.method == 'POST':
        # Groupsメニュー選択時の処理
        if request.POST['mode'] == '__groups_form__':
            #選択したGroup名を取得
            sel_group = request.POST['groups']
            # Groupを取得
            gp = Group.objects.filter(owner=request.user).filter(title=sel_group).first()
            # Groupに含まれるFriendを取得
            fds = Friend.objects.filter(owner=request.user).filter(group=gp)
            # FriendのUserをリストにまとめる
            vlist = []
            for item in fds:
                vlist.append(item.user.email)
            # フォームの用意
            groupsform = GroupSelectForm(request.user, request.POST)
            friendsform = FriendsForm(request.user, friends=friends, vals=vlist)
        
        # Friendsのチェック更新時の処理
        if request.POST['mode'] == '__friends_form__':
            # 選択したGroup名を取得
            sel_group = request.POST['group']
            group_obj = Group.objects.filter(title=sel_group).first()
            # チェックしたFriendsを取得
            sel_fds = request.POST.getlist('friends')
            print(sel_fds)
            # FriendsのUserを取得
            sel_users = User.objects.filter(email__in=sel_fds)
            # Userのリストに含まれるユーザーが登録したFriendを取得
            fds = Friend.objects.filter(owner=request.user).filter(user__in=sel_users)
            # すべてのFriendにGroupを設定し保存する
            vlist = []
            for item in fds:
                item.group = group_obj
                item.save()
                vlist.append(item.user.email)
            # メッセージを設定
            messages.success(request, '　チェックされたFriendを' + sel_group + 'に登録しました。')
            # フォームの用意
            groupsform = GroupSelectForm(request.user, {'groups':sel_group})
            friendsform = FriendsForm(request.user, friends=friends, vals=vlist)            

    # GETアクセス時の処理
    else:
        # フォームの用意
        groupsform = GroupSelectForm(request.user)
        friendsform = FriendsForm(request.user, friends=friends, vals=[])
        sel_group = '-'                

    # 共通処理
    createform = CreateGroupForm()
    params = {
        'login_user':request.user,
        'groups_form':groupsform,
        'friends_form':friendsform,
        'create_form':createform,
        'group':sel_group,
    }
    return render(request, 'sns/groups.html', params)

# Friendの追加処理
@login_required(login_url='/admin/login/')
def add(request):
    # 追加するUserを取得
    add_name = request.GET['name']
    add_user = User.objects.filter(email=add_name).first()
    # Userが本人だった場合の処理
    if add_user == request.user:
        messages.info(request, "自分自身をriendに追加することはできません。")
        return redirect(to='/sns')
    # publicの取得
    (public_user, public_group) = get_public()
    # add_userのFriendの数を調べる
    frd_num = Friend.objects.filter(owner=request.user).filter(user=add_user).count()
    # ゼロより大きければ既に登録済み
    if frd_num > 0:
        messages.info(request, add_user.email + 'は既に追加されています。')
        return redirect(to='/sns')
    # ここからFriendの登録処理
    frd = Friend()
    frd.owner = request.user
    frd.user = add_user
    frd.group = public_group
    frd.save()
    # メッセージを設定
    messages.success(request, add_user.email + 'を追加しました。groupページに移動して、追加したFriendをメンバーに設定してください。')
    return redirect(to='/sns')

# グループの作成処理
@login_required(login_url='/admin/login/')
def creategroup(request):
    # Groupを作り、Userとtitleを設定して保存する
    gp = Group()
    gp.owner = request.user
    gp.title = request.POST['group_name']
    gp.save()
    messages.info(request, '新しいグループを作成しました。')
    return redirect(to='/sns/groups')

# メッセージのポスト処理
@login_required(login_url='/admin/login/')
def post(request):
    if request.method == 'POST':
        #送信内容の取得
        content = request.POST['content']
        gr_name = request.POST['groups']
        # Groupの取得
        #group = Group.objects.filter(owner=request.user).filter(title=gr_name).first()
        group = Group.objects.filter(title=gr_name).first()
        if group == None:
            (pub_use, group) = get_public()
        # Messageを作成し設定して保存
        msg = Message()
        msg.owner = request.user
        msg.group = group
        msg.content = content
        msg.save()
        # ModelFormのインスタンス作成
        form = ImageForm(request.POST, request.FILES, instance=msg) 
        if form.is_valid():
            form.save() # formを保存
        else:  # validationでエラーがあれば、formに戻る（エラーメッセージを返す）
            return render(request, 'sns/post.html', {'form': form}, )
        # メッセージを設定
        messages.success(request, '新しいメッセージを投稿しました！')
        return redirect(to='/sns')
    
    # GETアクセス時の処理
    else:
        form = ImageForm()
        form2 = PostForm(request.user)

    # 共通処理
    params = {
        'login_user':request.user,
        'form':form,
        'form2':form2
    }
    return render(request, 'sns/post.html', params)

# 投稿をシェアする
@login_required(login_url='/admin/login/')
def share(request, share_id):
    # シェアするMessageの取得
    share = Message.objects.get(id=share_id)
    # POST送信の処理
    if request.method == 'POST':
        # 送信内容の取得
        gr_name = request.POST['groups']
        content = request.POST['content']
        # Groupの取得
        group = Group.objects.filter(owner=request.user).filter(title=gr_name).first()
        if group == None:
            (pub_use, group) = get_public()
        # Messageを作成し設定して保存
        msg = Message()
        msg.owner = request.user
        msg.group = group
        msg.content = content
        msg.share_id = share_id
        msg.save()
        share_msg = msg.get_share() #シェアー元Messageの呼び出し
        share_msg.share_count += 1
        share_msg.save()
        # メッセージを設定
        messages.success(request, 'メッセージをシェアしました！')
        return redirect(to='/sns')
    # 共通処理
    form = PostForm(request.user)
    params = {
        'login_user':request.user,
        'form':form,
        'share':share,
    }
    return render(request, 'sns/share.html', params)


# goodボタンの作成処理
@login_required(login_url='/admin/login/')
def good(request, good_id):
    # goodするMessageを取得
    good_msg = Message.objects.get(id=good_id)
    # 自分がメッセージにGoodした数を調べる
    is_good = Good.objects.filter(owner=request.user).filter(message=good_msg).count()
    # ゼロより大きければ既にgood済
    if is_good > 0:
        messages.success(request, '既にメッセージにはGoodしています。')
        return redirect(to='/sns')
    # Messageのgood_countを１増やす
    good_msg.good_count += 1
    good_msg.save()
    # Goodを作成し、設定して保存
    good = Good()
    good.owner = request.user
    good.message = good_msg
    good.save()
    # メッセージを設定
    messages.success(request, 'メッセージにGoodしました！')
    return redirect(to='/sns')

# これ以降は普通の関数=========================

# 指定されたGroupおよび検索文字によるMessageの取得
def get_your_group_message(owner, glist, page):
    page_num = 10 #ページあたりの表示数
    # publicの取得
    (public_user, public_group) = get_public()
    # チェックされたGroupの取得
    groups = Group.objects.filter(Q(owner=owner)|Q(owner=public_user)).filter(title__in=glist)
    # Groupに含まれるriendの取得
    me_friends = Friend.objects.filter(group__in=groups)
    # FriendのUserをリストにまとめる
    me_users = []
    for f in me_friends:
        me_users.append(f.user)
    # UserリストのUserが作ったGroupの取得
    his_groups = Group.objects.filter(owner__in=me_users)
    his_friends = Friend.objects.filter(user=owner).filter(group__in=his_groups)
    me_groups = []
    for hf in his_friends:
        me_groups.append(hf.group)
    # groupがgroupsに含まれるか、me_groupsに含まれるMessageの取得
    messages = Message.objects.filter(Q(group__in=groups)|Q(group__in=me_groups))
    # ページネーションで指定ページを取得
    page_item = Paginator(messages, page_num)
    return page_item.get_page(page)

# publicなUserとGroupを取得する
def get_public():
    public_user = User.objects.filter(email='public@public.public').first()
    public_group = Group.objects.filter(owner=public_user).first()
    return (public_user, public_group)
