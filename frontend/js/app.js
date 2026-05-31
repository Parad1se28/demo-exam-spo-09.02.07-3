const API_URL = 'http://127.0.0.1:8000/api';

function clearError() {
    document.querySelectorAll('.error-text').forEach(el => el.style.display = 'none');
}

const registerForm = document.getElementById('registerForm');

if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();   // Останавливаем перезагрузку страницы
        clearError();

        let isValid = true;

        // Собираем значение
        const login = document.getElementById('regLogin').value.trim();
        const password = document.getElementById('regPassword').value;
        const fio = document.getElementById('regFio').value.trim();
        const phone = document.getElementById('regPhone').value.trim();
        const email = document.getElementById('regEmail').value.trim();

        // Валидация логина 
        if (!/^[a-zA-Z0-9]{6,}$/.test(login)) {
            document.getElementById('errLogin').style.display = 'block';
            isValid = false;
        }

        // Валидация пароля (мин 8)
        if (password.length < 8) {
            document.getElementById('errPassword').style.display = 'block';
            isValid = false;
        }

        // Валидация ФИО (кириллица + пробелы)
        if (!/^[А-Яа-яЁё\s]+$/.test(fio)) {
            document.getElementById('errFio').style.display = 'block';
            isValid = false;
        }

        if (!isValid) return;

        const requestData = {
            login: login,
            password: password,
            fio: fio,
            phone: phone,
            email: email
        };

        try {
            const response = await fetch(`${API_URL}/register/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            const data =await response.json();

            if (response.status == 201) {
                alert('Регистрация прошла успешно!');   // Перекидываем на логин
            } else {
                const serverErr = document.getElementById('serverError');
                serverErr.textContent = data.error;
                serverErr.style.display = 'block';
            }
        }
        catch (error) {
            console.error("Ошибка сети:", error);
            alert("Ошибка соединения с сервером");
        }
    })
}

// Логика авторизации
const loginForm = document.getElementById('loginForm');

if (loginForm) {
    loginForm.addEventListener('submit', async(e) => {
        e.preventDefault();

        const loginError = document.getElementById('loginError');
        loginError.style.display = 'none';

        const login = document.getElementById('logLogin').value.trim();
        const password = document.getElementById('logPassword').value;

        try {
            const response = await fetch(`${API_URL}/login/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({login, password})
            });

            const data = await response.json();

            if (response.status == 200) {
                // Сохраняем "сессию" (токен) в браузере
                localStorage.setItem('user_id', data.user_id);
                localStorage.setItem('role', data.role);
                localStorage.setItem('login', data.login);

                // Распределение по страницам 
                if (data.role === 'admin') {
                    window.location.href = 'admin.html';
                } else {
                    window.location.href = 'profile.html';
                }
            } else {
                loginError.textContent = data.error;
                loginError.style.display = 'block';
            }
        } catch (error) {
            console.error("Ошибка сети:", error);
            alert("Ошибка соединения с сервером");
        }

    })
}

// --- Логика Личного Кабинета (profile.html) ---

// 1. Проверка авторизации
const welcomeText = document.getElementById('welcomeText');
if (welcomeText) { // Если мы на странице профиля
    const userId = localStorage.getItem('user_id');
    const userLogin = localStorage.getItem('login');
    
    // Если нет id в хранилище - выкидываем на логин
    if (!userId) {
        window.location.href = 'login.html';
    } else {
        welcomeText.textContent = `Привет, ${userLogin}!`;
    }

    // Кнопка выхода
    document.getElementById('logoutBtn').addEventListener('click', () => {
        localStorage.clear();
        window.location.href = 'login.html';
    });

    // 2. Логика Слайдера (Модуль 2: каждые 3 секунды)
    const slides = document.querySelectorAll('.slide');
    let currentSlide = 0;
    let slideInterval;

    function showSlide(index) {
        slides.forEach(s => s.classList.remove('active'));
        slides[index].classList.add('active');
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    }

    function prevSlide() {
        currentSlide = (currentSlide - 1 + slides.length) % slides.length;
        showSlide(currentSlide);
    }

    if (slides.length > 0) {
        document.getElementById('nextSlide').addEventListener('click', nextSlide);
        document.getElementById('prevSlide').addEventListener('click', prevSlide);
        slideInterval = setInterval(nextSlide, 3000); // Автопереключение
    }

    // 3. Загрузка заявок пользователя
    async function loadApplications() {
        const listDiv = document.getElementById('applicationsList');
        try {
            const res = await fetch(`${API_URL}/applications/?user_id=${userId}`);
            const data = await res.json();
            
            listDiv.innerHTML = ''; // Очищаем
            
            if (data.applications.length === 0) {
                listDiv.innerHTML = '<p style="font-size: 14px; color: #777;">У вас пока нет заявок.</p>';
                return;
            }

            data.applications.forEach(app => {
                const card = document.createElement('div');
                card.className = 'app-card';
                card.innerHTML = `
                    <p><strong>Курс:</strong> ${app.course_title}</p>
                    <p style="font-size: 14px; color: #555;">Дата начала: ${app.start_date}</p>
                    <p style="font-size: 14px; color: #555;">Оплата: ${app.payment_method}</p>
                    <div style="margin-top: 5px;">
                        <span class="status-badge status-new">${app.status}</span>
                    </div>
                `;
                listDiv.appendChild(card);
            });
        } catch (e) {
            listDiv.innerHTML = '<p style="color: red;">Ошибка загрузки заявок</p>';
        }
    }

    loadApplications(); // Вызываем при загрузке страницы

    // 4. Создание новой заявки
    const appForm = document.getElementById('appForm');
    appForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const errDate = document.getElementById('errDate');
        errDate.style.display = 'none';

        const courseId = document.getElementById('courseSelect').value;
        const startDateRaw = document.getElementById('startDate').value.trim();
        const paymentMethod = document.getElementById('paymentMethod').value;

        // Валидация даты ДД.ММ.ГГГГ
        const dateRegex = /^(\d{2})\.(\d{2})\.(\d{4})$/;
        const match = startDateRaw.match(dateRegex);
        
        if (!match) {
            errDate.style.display = 'block';
            return;
        }

        // Превращаем ДД.ММ.ГГГГ в ГГГГ-ММ-ДД для базы данных (PostgreSQL)
        const sqlDate = `${match[3]}-${match[2]}-${match[1]}`;

        const reqData = {
            user_id: userId,
            course_id: courseId,
            start_date: sqlDate,
            payment_method: paymentMethod
        };

        try {
            const res = await fetch(`${API_URL}/applications/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(reqData)
            });

            if (res.status === 201) {
                alert('Заявка отправлена!');
                appForm.reset();
                loadApplications(); // Перезагружаем список
            } else {
                alert('Ошибка при создании заявки');
            }
        } catch (e) {
            alert('Ошибка соединения с сервером');
        }
    });
}

// --- Логика Панели Администратора (admin.html) ---

const adminAppsList = document.getElementById('adminAppsList');

if (adminAppsList) {
    const role = localStorage.getItem('role');
    
    // Защита маршрута: пускаем только админа
    if (role !== 'admin') {
        window.location.href = 'login.html';
    }

    document.getElementById('logoutAdminBtn').addEventListener('click', () => {
        localStorage.clear();
        window.location.href = 'login.html';
    });

    let allApplications = []; // Сохраняем все заявки для локальной фильтрации

    // Функция отрисовки заявок
    function renderAdminApps(appsToRender) {
        adminAppsList.innerHTML = '';
        
        if (appsToRender.length === 0) {
            adminAppsList.innerHTML = '<p>Заявок не найдено.</p>';
            return;
        }

        appsToRender.forEach(app => {
            const card = document.createElement('div');
            card.className = 'app-card';
            
            // Определяем, какие опции выбраны по умолчанию
            const selectedNew = app.status === 'Новая' ? 'selected' : '';
            const selectedProg = app.status === 'Идет обучение' ? 'selected' : '';
            const selectedDone = app.status === 'Обучение завершено' ? 'selected' : '';

            card.innerHTML = `
                <p><strong>Студент:</strong> ${app.fio} <br> <span style="color: #666; font-size: 12px;">📞 ${app.phone}</span></p>
                <p><strong>Курс:</strong> ${app.course_title}</p>
                <p><strong>Старт:</strong> ${app.start_date} | <strong>Оплата:</strong> ${app.payment_method}</p>
                
                <div style="margin-top: 10px; display: flex; align-items: center;">
                    <select class="status-select" id="status_${app.id}">
                        <option value="Новая" ${selectedNew}>Новая</option>
                        <option value="Идет обучение" ${selectedProg}>Идет обучение</option>
                        <option value="Обучение завершено" ${selectedDone}>Обучение завершено</option>
                    </select>
                    <button class="update-btn" onclick="updateStatus(${app.id})">Сохранить</button>
                </div>
            `;
            adminAppsList.appendChild(card);
        });
    }

    // Загрузка заявок с сервера
    async function loadAllApplications() {
        try {
            const res = await fetch(`${API_URL}/admin_applications/`);
            const data = await res.json();
            allApplications = data.applications || [];
            renderAdminApps(allApplications); // Отрисовываем все
        } catch (error) {
            adminAppsList.innerHTML = '<p style="color: red;">Ошибка загрузки данных</p>';
        }
    }

    // Логика фильтрации при изменении select
    document.getElementById('statusFilter').addEventListener('change', (e) => {
        const selectedFilter = e.target.value;
        if (selectedFilter === 'Все') {
            renderAdminApps(allApplications);
        } else {
            const filteredApps = allApplications.filter(app => app.status === selectedFilter);
            renderAdminApps(filteredApps);
        }
    });

    // Функция обновления статуса (вызывается по клику на кнопку в карточке)
    window.updateStatus = async function(appId) {
        const newStatus = document.getElementById(`status_${appId}`).value;
        
        try {
            const res = await fetch(`${API_URL}/admin_applications/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ app_id: appId, status: newStatus })
            });

            if (res.status === 200) {
                alert('Статус успешно изменен!');
                loadAllApplications(); // Перезагружаем список, чтобы обновить фильтры
            } else {
                alert('Ошибка при обновлении статуса');
            }
        } catch (error) {
            alert('Ошибка сети');
        }
    }

    // Первичная загрузка
    loadAllApplications();
}