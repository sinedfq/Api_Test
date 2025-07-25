<h1>Реферальная система</h1>

<h3>Задание: </h3>

```bash

Реализовать простую реферальную систему. Минимальный интерфейс для
тестирования

Реализовать логику и API для следующего
функционала :

● Авторизация по номеру телефона. Первый запрос на ввод номера
телефона. Имитировать отправку 4хзначного кода авторизации(задержку
на сервере 1-2 сек). Второй запрос на ввод кода
● Если пользователь ранее не авторизовывался, то записать его в бд
● Запрос на профиль пользователя
● Пользователю нужно при первой авторизации нужно присвоить
рандомно сгенерированный 6-значный инвайт-код(цифры и символы)
● В профиле у пользователя должна быть возможность ввести чужой
инвайт-код(при вводе проверять на существование). В своем профиле
можно активировать только 1 инвайт код, если пользователь уже когда-
то активировал инвайт код, то нужно выводить его в соответсвующем
поле в запросе на профиль пользователя
● В API профиля должен выводиться список пользователей(номеров
телефона), которые ввели инвайт код текущего пользователя.
● Реализовать и описать в readme Api для всего функционала
● Создать и прислать Postman коллекцию со всеми запросами

```

-----

<h3>Техническое описание</h3>

views.py 

```python

def phone_auth(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        if phone and phone.startswith('+') and phone[1:].isdigit():
            request.session['auth_phone'] = phone
            return redirect('code_auth')
        else:
            messages.error(request, 'Неверный формат номера телефона')
    return render(request, 'ref/phone_auth.html')

def code_auth(request):
    phone = request.session.get('auth_phone')
    if not phone:
        return redirect('phone_auth')
    
    if request.method == 'POST':
        code = request.POST.get('code')
        if code and len(code) == 4 and code.isdigit():
            time.sleep(1)  # Имитация задержки
            
            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={'username': phone}
            )
            
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Неверный код подтверждения')
    
    return render(request, 'ref/code_auth.html', {'phone': phone})

@login_required
def profile(request):
    referred_users = User.objects.filter(
        activated_invite_code=request.user.invite_code
    ).values_list('phone', flat=True)
    
    return render(request, 'ref/profile.html', {
        'user': request.user,
        'referred_users': referred_users
    })

@login_required
def activate_invite(request):
    if request.user.activated_invite_code:
        messages.warning(request, 'Вы уже активировали инвайт-код')
        return redirect('profile')
    
    if request.method == 'POST':
        invite_code = request.POST.get('invite_code')
        
        try:
            referrer = User.objects.get(invite_code=invite_code)
            if referrer == request.user:
                messages.error(request, 'Нельзя активировать свой собственный инвайт-код')
            else:
                request.user.activated_invite_code = invite_code
                request.user.save()
                messages.success(request, 'Инвайт-код успешно активирован')
                return redirect('profile')
        except User.DoesNotExist:
            messages.error(request, 'Инвайт-код не найден')
    
    return render(request, 'ref/activate_invite.html')

```

```python 
phone_auth(request)
Назначение: Обработка ввода номера телефона

Логика:

    Валидация формата номера (+79123456789)
    Сохранение номера в сессии
    Перенаправление на страницу ввода кода

Шаблон: ref/phone_auth.html

 ```

```python
code_auth(request)
Назначение: Подтверждение авторизации по коду

Логика:

    Проверка 4-значного цифрового кода
    Создание/получение пользователя
    Авторизация пользователя

Шаблон: ref/code_auth.html
```

```python
profile(request)
Назначение: Просмотр профиля пользователя

Логика:

    Отображение информации о пользователе
    Показ списка приглашенных пользователей

Требования: Требуется авторизация (@login_required)
Шаблон: ref/profile.html

```

```python
activate_invite(request)
Назначение: Активация реферального кода

Логика:

    Проверка существования кода
    Запрет активации собственного кода
    Сохранение активированного кода

Требования: Требуется авторизация (@login_required)
Шаблон: ref/activate_invite.html

```

------

serializers.py

```python

class PhoneAuthSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    
    def validate_phone(self, value):
        # Простая валидация номера телефона
        if not value.startswith('+') or not value[1:].isdigit():
            raise serializers.ValidationError("Номер телефона должен быть в формате +79123456789")
        return value

class CodeAuthSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=4)

class UserProfileSerializer(serializers.ModelSerializer):
    referred_users = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['phone', 'invite_code', 'activated_invite_code', 'referred_users']
    
    def get_referred_users(self, obj):
        return list(User.objects.filter(activated_invite_code=obj.invite_code).values_list('phone', flat=True))

class InviteCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6)

```

```python

PhoneAuthSerializer
Назначение: Валидация номера телефона при авторизации
Поля:
    phone (CharField):
    Максимальная длина: 15 символов
Формат: должен начинаться с "+" и содержать только цифры после него
Методы:
  validate_phone(value) - проверяет корректность формата номера телефона
  
  Вызывает ValidationError при неверном формате

Пример корректного номера: +79123456789

```

```python

CodeAuthSerializer
Назначение: Валидация кода подтверждения
Поля:
    phone (CharField): номер телефона (макс. 15 символов)  
    code (CharField):
4-значный код подтверждения
Должен содержать только цифры

```

```python

UserProfileSerializer (ModelSerializer)
Назначение: Сериализация данных профиля пользователя
Поля модели User:
    phone - номер телефона пользователя
    invite_code - 6-символьный инвайт-код пользователя
    activated_invite_code - активированный реферальный код

Дополнительные поля:
    referred_users (SerializerMethodField):
        Список телефонов пользователей, которые активировали код текущего пользователя
        Формируется методом get_referred_users()

Методы:
    get_referred_users(obj) - возвращает список телефонов рефералов

```

```python
InviteCodeSerializer
Назначение: Валидация инвайт-кода при активации
Поля:
    invite_code (CharField):
    6-символьный код

Должен существовать в системе (проверяется в view)
```

----

models.py

```python

class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    invite_code = models.CharField(max_length=6, unique=True, blank=True)
    activated_invite_code = models.CharField(max_length=6, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self.generate_invite_code()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_invite_code():
        return get_random_string(6, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

    def __str__(self):
        return self.phone
```

```python

phone	 - CharField   Уникальный номер телефона (15 символов)
invite_code	- CharField	  Уникальный 6-символьный реферальный код
activated_invite_code	- CharField	  Активированный чужой код (6 символов)

Особенности:

    Автогенерация invite_code при создании (буквы+цифры)
    Наследует все стандартные поля пользователя Django
    __str__ возвращает номер телефона

```

------

<h3>Демонстрация работы приложения:</h3>

Главная страница со вводом номера телефона
<img width="1918" height="1028" alt="image" src="https://github.com/user-attachments/assets/56a90604-17bb-4d6c-98d4-cf921d1f94f1" />

Страница с вводом кода
<img width="1913" height="1025" alt="image" src="https://github.com/user-attachments/assets/cfbadad3-4b44-4a49-aa90-c5901e14de9e" />

Страница профиля пользователя
<img width="1919" height="1030" alt="image" src="https://github.com/user-attachments/assets/bf383397-d826-4314-893f-ec68c3465d80" />

*код генерируется автоматически если номер не был зарегистрирован ранее <br>
*код можно активировать только 1 раз <br>
*пользователи, которые ввели код, отображаются в профиле



