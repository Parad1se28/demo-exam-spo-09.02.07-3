import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.db import connection

@csrf_exempt
def register(request):
    # Разрешаем CORS (Preflight)
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

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
                    response = JsonResponse({'error': 'Пользователь уже существует'}, status=400)
                    response['Access-Control-Allow-Origin'] = '*'
                    return response
                
                # Записываем в базу данных
                cursor.execute("INSERT INTO Users (login, password, fio, phone, email) VALUES (%s, %s, %s, %s, %s)",
                            [login, hashed_pw, fio, phone, email]
                        )
            response = JsonResponse({'message': 'Успешная регистрация'}, status=201)
            response['Access-Control-Allow-Origin'] = '*'
            return response
        except Exception as e:
            response = JsonResponse({'error': str(e)}, status=500)
            response['Access-Control-Allow-Origin'] = '*'
            return response
    response = JsonResponse({'error': 'Метод не разрешен'}, status=405)
    response['Access-Control-Allow-Origin'] = '*'
    return response
        
@csrf_exempt
def login_user(request):
    # Разрешаем CORS (Preflight)
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response


    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            login = data.get('login')
            password = data.get('password')

            with connection.cursor() as cursor:
                cursor.execute("SELECT id, login, password, role FROM Users WHERE login = %s", [login])
                row = cursor.fetchone() # Возвращает кортеж (id, login, password, role)
            
            # Если пользователь найден и пароли совпадает
            if row and check_password(password, row[2]):
                response = JsonResponse({
                    'message': 'Авторизация успешна',
                    'user_id': row[0],
                    'login' : row[1],
                    'role': row[3]
                }, status=200)
                response['Access-Control-Allow-Origin'] = '*'
                return response
            else:
                response = JsonResponse({'error': 'Неверный логин или пароль'}, status=401)
                response['Access-Control-Allow-Origin'] = '*'
                return response
        except Exception as e:
            response = JsonResponse({'error': str(e)}, status=500)
            response['Access-Control-Allow-Origin'] = '*'
            return response
    response = JsonResponse({'error': 'Метод не разрешен'}, status=405)
    response['Access-Control-Allow-Origin'] = '*'
    return response

@csrf_exempt
def application(request):
    # Разрешаем CORS
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    # ПОЛУЧЕНИЕ ЗАЯВОК ПОЛЬЗОВАТЕЛЯ
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        if not user_id:
            res = JsonResponse({'error': 'Не указан user_id'}, status=400)
            res['Access-Control-Allow-Origin'] = '*'
            return res

        try:
            with connection.cursor() as cursor:
                # Джоиним таблицу Courses, чтобы получить название курса вместо ID
                cursor.execute("""
                    SELECT a.id, c.title, a.start_date, a.payment_method, a.status 
                    FROM Applications a
                    JOIN Courses c ON a.course_id = c.id
                    WHERE a.user_id = %s
                    ORDER BY a.id DESC
                """, [user_id])
                
                rows = cursor.fetchall()
                # Формируем список словарей для JSON
                apps = []
                for row in rows:
                    apps.append({
                        'id': row[0],
                        'course_title': row[1],
                        'start_date': row[2].strftime('%d.%m.%Y'), # Форматируем дату
                        'payment_method': row[3],
                        'status': row[4]
                    })
            
            res = JsonResponse({'applications': apps}, status=200)
            res['Access-Control-Allow-Origin'] = '*'
            return res
        except Exception as e:
            res = JsonResponse({'error': str(e)}, status=500)
            res['Access-Control-Allow-Origin'] = '*'
            return res

    # СОЗДАНИЕ НОВОЙ ЗАЯВКИ
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_id = data.get('user_id')
            course_id = data.get('course_id')
            start_date = data.get('start_date') # Ожидаем YYYY-MM-DD для базы
            payment_method = data.get('payment_method')

            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Applications (user_id, course_id, start_date, payment_method) VALUES (%s, %s, %s, %s)",
                    [user_id, course_id, start_date, payment_method]
                )
            
            res = JsonResponse({'message': 'Заявка успешно создана'}, status=201)
            res['Access-Control-Allow-Origin'] = '*'
            return res
        except Exception as e:
            res = JsonResponse({'error': str(e)}, status=500)
            res['Access-Control-Allow-Origin'] = '*'
            return res
            
    return JsonResponse({'error': 'Метод не разрешен'}, status=405)

@csrf_exempt
def admin_applications(request):
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # ПОЛУЧИТЬ ВСЕ ЗАЯВКИ (С данными пользователей)
    if request.method == 'GET':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT a.id, u.fio, u.phone, c.title, a.start_date, a.payment_method, a.status 
                    FROM Applications a
                    JOIN Users u ON a.user_id = u.id
                    JOIN Courses c ON a.course_id = c.id
                    ORDER BY a.id DESC
                """)
                rows = cursor.fetchall()
                apps = []
                for row in rows:
                    apps.append({
                        'id': row[0],
                        'fio': row[1],
                        'phone': row[2],
                        'course_title': row[3],
                        'start_date': row[4].strftime('%d.%m.%Y'),
                        'payment_method': row[5],
                        'status': row[6]
                    })
            res = JsonResponse({'applications': apps}, status=200)
            res['Access-Control-Allow-Origin'] = '*'
            return res
        except Exception as e:
            res = JsonResponse({'error': str(e)}, status=500)
            res['Access-Control-Allow-Origin'] = '*'
            return res

    # ИЗМЕНИТЬ СТАТУС ЗАЯВКИ
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            app_id = data.get('app_id')
            new_status = data.get('status')

            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE Applications SET status = %s WHERE id = %s",
                    [new_status, app_id]
                )
            res = JsonResponse({'message': 'Статус обновлен'}, status=200)
            res['Access-Control-Allow-Origin'] = '*'
            return res
        except Exception as e:
            res = JsonResponse({'error': str(e)}, status=500)
            res['Access-Control-Allow-Origin'] = '*'
            return res