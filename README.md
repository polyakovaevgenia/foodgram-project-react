### Описание проекта 

Проект Foodgram - сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Автор 

Студентка 57 когорты Яндекс Практикума по направлению "Python-разработчик" Евгения Полякова.

### Стек технологий: 

Python, Django, Django Rest Framework, API, nginx, gunicorn, Docker, PostgreSQL, Яндекс Облако.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
cd  foodgram-project-react 
```

Перейти в папку backend:

```
cd backend
```
Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver 
``` 
### Как создать администратора: 

```
python manage.py createsuperuser
```  

Далее придумайте логин и пароль, если пароль будет очень лёгким, Django предложит усложнить его. 

### Примеры запросов к API:  

1.Post. Получение токена.  
``` 
 api/auth//token/login/
```

```
{
    "password": "123567",
    "email": "user@mail.ru"
}
```
Пример успешного ответа:
```
{
    "auth_token": "34hjh23ghg2h3g5h5gh2ghg5"
}
```
2. Get. Получение списка всех пользователей. 
```
`api/users/`
``` 

Пример успешного ответа:
```

{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
        "id": 1,
        "username": "user",
        "email": "user@mail.ru",
        "first_name": "Kate",
        "last_name": "Popova"б
        "is_subscribed": false
        }
    ]
}

```

3. Get. Получение списка ингредиентов.
```  
api/ingredients/ 
```
Пример успешного ответа:
```
{
    "name": "абрикосовое варенье",
    "measurement_unit": "г",
    "recipes": [],
    "id": 1
}
```
### Команда для запуска скрипта по загрузке данных из csv файлов: 
``` 
python manage.py import_ingredients 
``` 

### Докуметация для API YaMDb:

Запустите проект и перейдите по адресу: 

```
http://127.0.0.1:8000/redoc/
```
### Проект доступен по ссылке:
```
http://foodgramforyou.hopto.org
```