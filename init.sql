-- Таблица пользователей
CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    fio VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'user'
);

-- Таблица курсов
CREATE TABLE Courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL
);

-- Таблица заявок
CREATE TABLE Applications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(id) ON DELETE CASCADE,
    course_id INT REFERENCES Courses(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'Новая'
);

-- Таблица отзывов
CREATE TABLE Reviews (
    id SERIAL PRIMARY KEY,
    application_id INT REFERENCES Applications(id) ON DELETE CASCADE,
    text TEXT NOT NULL
);

-- Опционально добавляем администратора, чтобы потом не мучаться
INSERT INTO Users(login, password, fio, phone, email, role)
VALUES ('Admin', 'хэш_пароля_KorokNET', 'Администратор', '8(000)000-00-00', 'admin@korochki.est', 'admin');
