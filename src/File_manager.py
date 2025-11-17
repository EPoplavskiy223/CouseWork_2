import json
import os
from abc import ABC, abstractmethod


class FileHandler(ABC):

    @abstractmethod
    def add_vacancy(self, vacancy):
        pass

    @abstractmethod
    def filtered_vacancies(
        self, title=None, salary_min=None, company=None, description=None
    ):
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy):
        pass


class JSONFileHandler(FileHandler):

    def __init__(self, filename=r"data/vacancies.json"):
        self.__filename = filename
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Проверяет наличие файла и создает его если нет"""
        if not os.path.exists(self.__filename):
            with open(self.__filename, "w", encoding="utf-8") as file:
                json.dump([], file)

    def read_json(self):
        """Читает файл формата JSON"""
        try:
            with open(self.__filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print("Ошибка", e)

    def _save_json(self, data):
        """Сохранение вакансий в JSON файл"""
        with open(self.__filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def add_vacancy(self, vacancy):
        """Добавление и проверка вакансий"""
        data_json = self.read_json()
        if vacancy.get("title") is None:
            return

        for item in data_json:
            if item.get("url") == vacancy.get("url"):
                return

        data_json.append(vacancy)
        self._save_json(data_json)

    def filtered_vacancies(
        self, title=None, salary_min=None, company=None, description=None
    ):
        """Поиск по категории в вакансии"""
        result = []
        data_json = self.read_json()

        for vacancy in data_json:
            comparison = True
            if title:
                if title.lower() not in vacancy["title"].lower():
                    comparison = False
            if salary_min:
                if vacancy["salary"]["salary_data"] < salary_min:
                    comparison = False
            if company:
                if company.lower() not in vacancy["company"].lower():
                    comparison = False
            if description:
                if description.lower() not in vacancy["description"].lower():
                    comparison = False

            if comparison:
                result.append(vacancy)

        return result

    def delete_vacancy(self, vacancy=None):
        """Удаление вакансии по URL или полная очистка файла"""
        data_json = self.read_json()
        result = []
        if vacancy is not None:
            for item in data_json:
                if item.get("url") != vacancy:
                    result.append(item)
                else:
                    print(
                        "Вакансия удалена:\n",
                        json.dumps(item, ensure_ascii=False, indent=4),
                    )

            self._save_json(result)
        else:
            self._save_json(result)
            print("Все вакансии удалены")
