from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django_rest_passwordreset.tokens import get_token_generator


GENDER_CHOICES = (
	('M', 'Male'),
	('F', 'Female'),
)


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

    email = models.EmailField(verbose_name='Почта', max_length=254, unique=True)
    first_name = models.CharField(verbose_name='Имя', max_length=50)
    last_name = models.CharField(verbose_name='Фамилия', max_length=50)
    gender = models.CharField(verbose_name='Пол', choices=GENDER_CHOICES, max_length=7)
    avatar = models.ImageField(verbose_name='Аватарка', upload_to='media', blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

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
