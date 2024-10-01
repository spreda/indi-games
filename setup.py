# -*- coding: utf-8 -*-
import os
import sys
import venv

VENV_DIR = 'venv' # Директория виртуального окружения
PIP_PATH = os.path.join(VENV_DIR, 'Scripts', 'pip')  # Путь к pip в виртуальном окружении
PYTHON_PATH = os.path.join(VENV_DIR, 'Scripts', 'python')  # Путь к интерпретатору в виртуальном окружении

def create_virtualenv():
    if not os.path.exists(VENV_DIR):
        print(f"Создание виртуального окружения в {VENV_DIR}...")
        venv.create(VENV_DIR, with_pip=True)
        print("Виртуальное окружение создано.")

def install_dependencies():
    print("Установка зависимостей...")
    result = os.system(f"{PIP_PATH} install -r requirements.txt")
    if result == 0:
        print("Зависимости успешно установлены.")
    else:
        print("Ошибка при установке зависимостей.")
        sys.exit(1)

def add_site_packages_to_path():
    site_packages_path = os.path.join(VENV_DIR, 'Lib', 'site-packages')
    if os.path.exists(site_packages_path):
        sys.path.insert(0, site_packages_path)
        print(f"Добавлен {site_packages_path} в sys.path")
    else:
        print(f"Не удалось найти {site_packages_path}. Убедитесь, что виртуальное окружение существует.")
        sys.exit(1)

def load_env_variables(env_file='.env'):
    if not os.path.exists(env_file):
        print(f"Файл {env_file} не найден.")
        sys.exit(1)
    
    add_site_packages_to_path()  # Добавляем site-packages в sys.path перед импортом dotenv
    import dotenv
    dotenv.load_dotenv(env_file)
    print(f"Переменные окружения загружены из {env_file}.")

def main():
    env_file = sys.argv[1] if len(sys.argv) > 1 else '.env'

    if not os.path.exists(VENV_DIR):
        print(f"Создание виртуального окружения в {VENV_DIR}...")
        create_virtualenv()
        install_dependencies()

    print("Загружаем переменные окружения...")
    load_env_variables(env_file)

    print("Запуск приложения...")
    os.system(f"{PYTHON_PATH} main.py")

if __name__ == '__main__':
    main()
