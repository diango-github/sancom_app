from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.utils import timezone


#流用
class UserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

#流用
class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_('email address'), unique=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


#自作
class File(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_user')
    filename1 = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        return '<' + self.filename1 + '(' + str(self.owner) + ')>'

class Dictionary(models.Model):
    item = models.CharField(max_length=20, null=True, blank=True)
    category = models.CharField(max_length=40, null=True, blank=True)
    japanese = models.CharField(max_length=200, null=True, blank=True)
    english = models.CharField(max_length=200, null=True, blank=True)
    esound = models.CharField(max_length=40, null=True, blank=True)
    chinese = models.CharField(max_length=200, null=True, blank=True)
    csound = models.CharField(max_length=40, null=True, blank=True)
 
    def __str__(self):
        return '<' + self.item + '>'
        #return '<' + self.item + '(' + str(self.category) + ')>'

class Erepeat(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='e_memorytraining1')
    dictionary = models.ForeignKey(Dictionary, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return '<' + self.dictionary.item + '(' + str(self.owner) + ')>'

class Crepeat(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='c_memorytraining1')
    dictionary = models.ForeignKey(Dictionary, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return '<' + self.dictionary.item + '(' + str(self.owner) + ')>'

class E3sentences(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='e_memorytraining2')
    dictionary = models.ForeignKey(Dictionary, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return '<' + self.dictionary.item + '(' + str(self.owner) + ')>'

class C3sentences(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='c_memorytraining2')
    dictionary = models.ForeignKey(Dictionary, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return '<' + self.dictionary.item + '(' + str(self.owner) + ')>'

class Edeepen(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='e_memorytraining3')
    dictionary = models.ForeignKey(Dictionary, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return '<' + self.dictionary.item + '(' + str(self.owner) + ')>'

class Cdeepen(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='c_memorytraining3')
    dictionary = models.ForeignKey(Dictionary, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return '<' + self.dictionary.item + '(' + str(self.owner) + ')>'

class Efinish(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='e_memorytraining4')
    dictionary = models.ForeignKey(Dictionary, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return '<' + self.dictionary.item + '(' + str(self.owner) + ')>'

class Cfinish(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='c_memorytraining4')
    dictionary = models.ForeignKey(Dictionary, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return '<' + self.dictionary.item + '(' + str(self.owner) + ')>'

# Messageクラス
class Message(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_owner')
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    images = models.ImageField(upload_to='images/', default='ozawa.jpg')
    #videos = models.FileField(upload_to='videos/',null=True,validators=[FileExtensionValidator(allowed_extensions=['MOV','avi','mp4','webm','mkv'])])
    share_id = models.IntegerField(default=-1)
    good_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.content) + '(' + str(self.owner) + ')'
    
    def get_share(self):
        return Message.objects.get(id=self.share_id)
    
    class Meta:
        ordering = ('-pub_date', )

# Groupクラス
class Group(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_owner')
    title = models.CharField(max_length=100)

    def __str__(self):
        return '<' + self.title + '(' + str(self.owner) + ')>'

# Friendクラス
class Friend(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_owner')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey('Group', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user) + '(group:"' + str(self.group) + '")'

# Goodクラス
class Good(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='good_owner')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)

    def __str__(self):
        return 'good for "' + str(self.message) + '"(by ' + str(self.owner) + ')'
