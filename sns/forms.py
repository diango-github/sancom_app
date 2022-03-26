from cProfile import label
from django import forms
from matplotlib import widgets
from account.models import User, Message, Friend, Group, Good
#from django.contrib.auth.models import User

# Groupのチェックボックスフォーム
class GroupCheckForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(GroupCheckForm, self).__init__(*args, **kwargs)
        public = User.objects.filter(email='public').first()
        #self.fields['groups'] = forms.MultipleChoiceField(choices=[(item.title, item.title) for item in Group.objects.filter(owner__in=[user,public])], widget=forms.CheckboxSelectMultiple(),)
        self.fields['groups'] = forms.ChoiceField(choices=[(item.title, item.title) for item in Group.objects.filter(owner__in=[user,public])], widget=forms.CheckboxSelectMultiple(),)

# Groupの選択メニューフォーム
class GroupSelectForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(GroupSelectForm, self).__init__(*args, **kwargs)
        self.fields['groups'] = forms.ChoiceField(label='グループ', choices=[('-','-')] + [(item.title, item.title) for item in Group.objects.filter(owner=user)], widget=forms.Select(attrs={'class':'form-control'}),)

# Friendのチェックボックスフォーム
class FriendsForm(forms.Form):
    def __init__(self, user, friends=[], vals=[], *args, **kwargs):
        super(FriendsForm, self).__init__(*args, **kwargs)
        self.fields['friends'] = forms.MultipleChoiceField(choices=[(item.user, item.user) for item in friends], widget=forms.CheckboxSelectMultiple(), initial=vals)

# Group作成フォーム
class CreateGroupForm(forms.Form):
    group_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))

# 投稿フォーム(画像)
class ImageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['images']
        #widgets = {
            #'content': forms.TextInput(attrs={'class':'form-control'}),
            #'images': forms.ImageInput(attrs={'class':'form-control'})
        #}


# 投稿フォーム(テキスト)
class PostForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        public = User.objects.filter(email='public').first()        
        self.fields['groups'] = forms.ChoiceField(label='グループ', choices=[('-','-')] + [(item.title, item.title) for item in Group.objects.all()], widget=forms.Select(attrs={'class':'form-control'}),)
        #self.fields['groups'] = forms.ChoiceField(label='グループ', choices=[('-','-')] + [(item.title, item.title) for item in Group.objects.filter(owner__in=[user, public])], widget=forms.Select(attrs={'class':'form-control'}),)

    content = forms.CharField(label='メッセージ', max_length=500, widget=forms.Textarea(attrs={'class':'form-control', 'rows':2}),)

class LanguageForm(forms.Form):
    data = (
        (7, 'Russian'),
        (6, 'Spanish'),
        (5, 'French'),
        (4, 'English'),
        (3, 'Korean'),
        (2, 'Chinese'),
        (1, 'Japanese')
    )
    choice = forms.ChoiceField(label='翻訳言語', initial='4', choices=data, widget=forms.Select(attrs={'class':'form-control'}),)
 