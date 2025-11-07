from src.API_interaction import HeadHunterAPI, Vacancy
from src.File_manager import JSONFileHandler

# if __name__ == "__main__":
#     vac = Vacancy
#     api = HeadHunterAPI()
#
#     vacancy_list = api.get_vacancies()
#     vacancy_dict = vac.all_vacancies_list(vacancy_list)
#     q = (sorted(vacancy_dict))
#
#     for vacancy in q:
#         print(vacancy)


if __name__ == "__main__":
    vac = Vacancy
    api = HeadHunterAPI()

    json_manager = JSONFileHandler()

    vacancy_list = api.get_vacancies("python")
    vacancy_dict = vac.all_vacancies_list(vacancy_list)
    del_vacancy = json_manager.delete_vacancy()

    for item in vacancy_dict:
        add_vacancy = json_manager.add_vacancy(item.to_dict())

    # critical = json_manager.filtered_vacancies(title=)
    # pprint(critical, sort_dicts=False)
    # filter_criteria = json_manager.filtered_vacancies(title='python', salary_min=10000)
    # pprint(filter_criteria, sort_dicts=False)
