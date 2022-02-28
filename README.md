# "Find a soul mate" API приложения для знакомств
## Описание

Приложение предназначено для поиска второй половинки


**Базовая часть:**
* Возможноть регистрации, авторизации по токену;
* Возможность ставить лайки друг другу;
* Если симпатия взаимна на почту приходят уведомления;
* Возможность фильтровать людей по расстоянию и узнать кто к вам ближе

### Для запуска проекта необходимо:

Установить зависимости:

```bash
pip install -r requirements.txt
```

Вам необходимо будет создать базу и прогнать миграции:

```bash
manage.py makemigrations
manage.py migrate
manage.py createsuperuser
```

Выполнить команду:

```bash
python manage.py runserver
```
