from PIL import Image
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django_rest_passwordreset.tokens import get_token_generator

GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        if email is None:
            raise TypeError('Поле email не должно быть пустым.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        if email is None:
            raise TypeError('Поле email не должно быть пустым.')
        if password is None:
            raise TypeError('Поле password не должно быть пустым')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        return user


class User(AbstractUser):
    objects = UserManager()
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    email = models.EmailField(verbose_name='Почта', max_length=254, unique=True)
    first_name = models.CharField(verbose_name='Имя', max_length=50)
    last_name = models.CharField(verbose_name='Фамилия', max_length=50)
    gender = models.CharField(verbose_name='Пол', choices=GENDER_CHOICES, max_length=7)
    avatar = models.ImageField(verbose_name='Аватарка', upload_to='media', blank=True, null=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        max_length=150,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save()
        if not self.avatar:
            return
        img = Image.open(self.avatar.path)
        width, height = img.size
        watermark = Image.open('watermark.png')
        watermark.thumbnail((200, 200))
        mark_width, mark_height = watermark.size
        paste_mask = watermark.split()[3]
        x = width - mark_width - 5
        y = height - mark_height - 5
        img.paste(watermark, (x, y), paste_mask)
        img.save(self.avatar.path)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class ConfirmEmailToken(models.Model):
    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name="The User which is associated to this password reset token"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="When was this token generated"
    )

    key = models.CharField(
        max_length=64,
        db_index=True,
        unique=True
    )

    class Meta:
        verbose_name = 'Confirmation Token Email'
        verbose_name_plural = 'Confirmation Tokens Email'

    @staticmethod
    def generate_key():
        return get_token_generator().generate_token()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)


class Loves(models.Model):
    id_from = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name='id_from')
    id_to = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='id_to')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['id_from', 'id_to'],
                name='unique matches')
        ]
        verbose_name = 'Взаимность'
        verbose_name_plural = 'Взаимности'

    def __str__(self):
        return f"{self.id_from} + {self.id_to}"
