from src.API_interaction import HeadHunterAPI, Vacancy
from src.File_manager import JSONFileHandler

json_manager = JSONFileHandler()
cl_api = HeadHunterAPI()
cl_vacancy = Vacancy


def user_interaction() -> None:
    """Основной цикл для передачи параметров пользователя"""
    try:
        while True:
            title_menu()
            num = user_input_int()
            if num in (1, 2, 3, 4, 5, 6):
                if num == 1:
                    request = user_input_search()
                    search_vacancies_api(request)
                    condition_format_print_in_file()

                elif num == 2:
                    quantity_user_input = user_input_int(
                        "Введите количество вакансий -> "
                    )
                    top_vacancies_by_salary(quantity_user_input)

                elif num == 3:
                    request = user_input_search()

                    search_vacancies_api(request)
                    search_vacancies_file(request)

                elif num == 4:
                    format_print(json_manager.read_json())

                elif num == 5:
                    json_manager.delete_vacancy(
                        user_input_search("Введите URL Удаляемой вакансии -> ")
                    )

                elif num == 6:
                    break
            else:
                print(f"\nВведите категорию из предложенных\n{'⇣ ' * 20}\n")
    except Exception as e:
        print(f"Ошибка: {e}")


def top_vacancies_by_salary(quantity: int) -> None:
    """Сортировка по зарплате из файла"""
    data = json_manager.read_json()
    sorted_data = sorted(data, key=lambda x: x["salary"]["salary_value"], reverse=True)
    format_print(sorted_data[:quantity])


def condition_format_print_in_file():
    """читает вакансии из файла и форматирует вывод"""
    data = json_manager.read_json()
    format_print(data)


def format_print(data):
    """Преобразует вывод вакансий"""
    score = 0
    for vacancy in data:
        score += 1
        print(
            f"\nВакансия №{score}.\n"
            f"Должность: {vacancy['title']}\n"
            f"Компания: {vacancy['company']}\n"
            f"{vacancy['salary']['salary_display']}\n"
            f"Требования: {vacancy['description']}\n"
            f"Ссылка: {vacancy['url']}\n"
        )


def save_vacancies(vacancy_obj=None, vacancy_dict=None):
    """Сохранение вакансий с их преобразованием в словарь"""
    if vacancy_obj:
        for item in vacancy_obj:
            vacancy_dict = item.to_dict()
            json_manager.add_vacancy(vacancy_dict)
    else:
        for item in vacancy_dict:
            json_manager.add_vacancy(item)


def search_vacancies_api(search=None):
    """Поиск вакансий по запросу с последующим сохранением"""
    search_connect = cl_api.get_vacancies(search)
    vacancy_str = cl_vacancy.all_vacancies_list(search_connect)
    save_vacancies(vacancy_obj=vacancy_str)


def search_vacancies_file(search):
    """Поиск по параметрам из файла"""
    if search is None:
        return "Введите что-то и попробуйте еще раз"

    try:
        search_int = int(search)
        result = json_manager.filtered_vacancies(salary_min=search_int)
        save_vacancies(vacancy_dict=result)
        return format_print(result)

    except ValueError:
        result = json_manager.filtered_vacancies(description=search)
        save_vacancies(vacancy_dict=result)
        return format_print(result)


def title_menu():
    """Выводит главное меню"""
    menu = {
        "title_print": "======== Меню вакансий ========",
        1: "Поиск вакансий по ключевому слову из hh.ru",
        2: "Показать топ N вакансий по зарплате",
        3: "Поиск вакансий по описанию",
        4: "Показать все вакансии",
        5: "Удалить вакансию",
        6: "Выход",
    }

    for k, v in menu.items():
        if k == "title_print":
            print(v)
            continue
        print(f"{k}. {v}")


def user_input_int(title="Ваш выбор -> "):
    """Проверка вводимого пользователем числа с текстом по умолчанию"""
    while True:
        user_input = input(f"{title}")
        try:
            return int(user_input)
        except ValueError:
            print("Введите число")


def user_input_search(title="Введите запрос -> "):
    """Ввод запроса с текстом по умолчанию"""
    user_input = input(f"{title}")
    if user_input:
        return user_input
    else:
        return None


