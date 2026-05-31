# Заметки по проекту

## Исправление ошибки CORS (Access-Control-Allow-Origin)

**Причина ошибки:**
Браузер требует наличие заголовка `Access-Control-Allow-Origin` не только во время предварительного `OPTIONS` (Preflight) запроса, но и в ответе на сам `POST` запрос. Без него браузер блокирует ответ, даже если сервер успешно его обработал.

**Текущее решение (ручное):**
Проблема решена путем добавления `response['Access-Control-Allow-Origin'] = '*'` к абсолютно каждому объекту `JsonResponse` перед его возвратом в `views.py`.

**Правильное решение (Best Practice) на будущее:**
Чтобы не дублировать код в каждом view, стандартным решением в Django является использование библиотеки `django-cors-headers`.

1. Установить библиотеку: 
   `pip install django-cors-headers`
2. В `backend/settings.py`:
   - Добавить `'corsheaders'` в конец списка `INSTALLED_APPS`
   - Добавить `'corsheaders.middleware.CorsMiddleware'` в список `MIDDLEWARE` (в самое начало, перед `CommonMiddleware` и другими)
   - Прописать настройку `CORS_ALLOW_ALL_ORIGINS = True` (для режима разработки)
3. Упростить код:
   После настройки библиотеки можно полностью удалить логику обработки `OPTIONS` запросов и ручное добавление заголовков `Access-Control-*` из `views.py`.