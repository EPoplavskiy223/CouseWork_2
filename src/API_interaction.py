from abc import ABC, abstractmethod
from typing import Any

import requests


class Job(ABC):
    """Абстрактный класс для работы с API сервисов вакансий"""

    @abstractmethod
    def get_vacancies(self, search_query: str) -> list:
        """Получить вакансии по поисковому запросу"""
        pass

    @abstractmethod
    def _connect(self, search_query: dict) -> Any:
        """Подключается к АПИ и возвращает переданные данные """
        pass


class HeadHunterAPI(Job):
    """Класс для работы с сайтом hh.ru"""

    def __init__(self) -> None:
        self.__hh_API = "https://api.hh.ru/vacancies"

    def _connect(self, search_query: dict) -> list[str | int] | None | Any:
        """Запрос для получения листа с вакансиями"""

        try:
            response = requests.get(self.__hh_API, params=search_query)

            if response.status_code == 200:
                return response.json()
            else:
                return ["Ошибка, статус запроса:", response.status_code]

        except Exception as e:
            print("Ошибка ->", e)

    def get_vacancies(self, search_query: str = None) -> list:
        """Простой сбор параметров для запроса к _connect с выводом ключа items"""
        param = {}

        if search_query:
            param["area"] = 1
            param["text"] = search_query
            param["per_page"] = 100
            data = self._connect(param)
            if data is None:
                return []
            result = data.get("items", [])
            return result
        else:
            param["area"] = 1
            param["per_page"] = 100
            data = self._connect(param)
            if data is None:
                return []
            result = data.get("items", [])
            return result


class Vacancy:

    __slots__ = [
        "title",
        "company",
        "url",
        "salary",
        "salary_value",
        "salary_display",
        "salary_data",
        "description",
    ]

    def __init__(self, data: dict) -> None:

        self.title = self._title_validate(data.get("name"))
        self.url = self._url_validate(data.get("alternate_url"))

        self.salary_data = self._salary_validate(data.get("salary"))
        self.salary_display = f"{self.salary_data['salary_display']} {self.salary_data.get('salary_currency')}"
        self.salary_value = self.salary_data["salary_value"]

        snippet = data.get("snippet") or {}
        employer = data.get("employer") or {}
        self.description = self._description_validate(snippet.get("requirement"))
        self.company = self._company_validate(employer.get("name"))

    @staticmethod
    def _title_validate(data: dict | None) -> str | dict:
        """Проверка валидности названия вакансии"""
        if data is None:
            return "Не указано"
        else:
            return data

    @staticmethod
    def _url_validate(data: dict | None) -> str | dict:
        """Проверка валидности ссылки на вакансию"""
        if data is None:
            return "Ссылка не указана"
        else:
            return data

    @staticmethod
    def _salary_validate(data: dict | None) -> dict:
        """Проверка валидности на указанный доход и подсчет потенциального дохода"""
        if data is not None:
            if data["from"] is not None and data["to"] is not None:
                salary_data = round((data["from"] + data["to"]) / 2)
                return {
                    "salary_data": salary_data,
                    "salary_display": f"Средняя зарплата: {salary_data}",
                    "salary_value": salary_data,
                    "salary_currency": data.get("currency"),
                }
            elif data["from"] is not None:
                return {
                    "salary_data": data["from"],
                    "salary_display": f"Зарплата от: {data['from']}",
                    "salary_value": data["from"],
                    "salary_currency": data.get("currency"),
                }
            else:
                return {
                    "salary_data": data["to"],
                    "salary_display": f"Зарплата до: {data['to']}",
                    "salary_value": data["to"] * 0.75,
                    "salary_currency": data.get("currency"),
                }
        else:
            return {
                "salary_data": 0,
                "salary_display": "Зарплата не указана",
                "salary_value": 0,
            }

    @staticmethod
    def _description_validate(data: dict | None) -> str | dict:
        if data is None:
            return "Требования не указаны"
        else:
            return data

    @staticmethod
    def _company_validate(data: dict | None) -> str | dict:
        if data is None:
            return "Компания не указана"
        else:
            return data

    @staticmethod
    def all_vacancies_list(data_list) -> list:
        """Распаковка листа вакансий и передача в магический метод"""
        vacancies = []
        for data_dict in data_list:
            vacancy_obj = Vacancy(data_dict)
            vacancies.append(vacancy_obj)
        return vacancies

    def __str__(self):
        return (
            f"Компания : {self.company}\n"
            f"Вакансия : {self.title}\n"
            f"Ссылка : {self.url}\n"
            f"{self.salary_display}\n"
            f"Требование : {self.description}\n"
        )

    def __gt__(self, other) -> bool:
        return self.salary_value > other.salary_value

    def __lt__(self, other) -> bool:
        return self.salary_value < other.salary_value

    def __eq__(self, other) -> bool:
        return self.salary_value == other.salary_value

    def to_dict(self) -> dict:
        """Преобразует объект Vacancy в словарь"""
        return {
            "title": self.title,
            "url": self.url,
            "salary": self.salary_data,
            "company": self.company,
            "description": self.description,
        }
