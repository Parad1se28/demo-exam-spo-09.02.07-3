import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.db import connection

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            # Получаем данные от JS (Фронтенда)
            data = json.loads(request.body)
            login = data.get('login')
            password = data.get('password')
            fio = data.get('fio')
            phone = data.get('phone')
            email = data.get('email')

            # Хешируем пароль встроенными средствами Djanog
            hashed_pw = make_password(password)

            with connection.cursor() as cursor:

                # Проверяем уникальность 
                cursor.execute("SELECT id FROM Users WHERE login = %s", [login])
                if cursor.fetchone():
                    return JsonResponse({'error': 'Пользователь уже существует'}, status=400)
                
                # Записываем в базу данных
                cursor.execute("INSERT INTO Users (login, password, fio, phone, email) VALUES (%s, %s, %s, %s, %s)"
                            [login, hashed_pw, fio, phone, email]
                        )
            return JsonResponse({'message': 'Успешная регистрация'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=505)
    return JsonResponse({'error': 'Метод не разрешен'}, status=405)
        
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            login = data.get('login')
            password = data.get('password')

            with connection.cursor() as cursor:
                cursor.execute("SELECT id, login, password, role FROM Users WHERE login = %s" [login])
                row = cursor.fetchone() # Возвращает кортеж (id, login, password, role)
            
            # Если пользователь найден и пароли совпадает
            if row and check_password(password, row[2]):
                return JsonResponse({
                    'message': 'Авторизация успешна',
                    'user_id': row[0],
                    'login' : row[1],
                    'role': row[3]
                }, status=200)
            else:
                return JsonResponse({'error': 'Неверный логин или пароль'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Метод не разрешен'}, status=405)