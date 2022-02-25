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

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Поле email не должно быть пустым')
        if password is None:
            raise ValueError('Поле password не должно быть пустым')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    objects = UserManager()

    email = models.EmailField(verbose_name='Почта', max_length=254, unique=True)
    first_name = models.CharField(verbose_name='Имя', max_length=50)
    last_name = models.CharField(verbose_name='Фамилия', max_length=50)
    gender = models.CharField(verbose_name='Пол', choices=GENDER_CHOICES, max_length=7)
    avatar = models.ImageField(verbose_name='Аватарка', upload_to='media', blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользоваьель'
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
