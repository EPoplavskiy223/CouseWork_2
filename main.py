from src.API_interaction import Vacancy, HeadHunterAPI

if __name__ == "__main__":
    vac = Vacancy
    api = HeadHunterAPI()

    vacancy_list = api.get_vacancies("Разработчик")
    vacancy_dict = vac.all_vacancies_list(vacancy_list)
    # q = (sorted(vacancy_dict))

    for vacancy in vacancy_dict:
        print(vacancy)