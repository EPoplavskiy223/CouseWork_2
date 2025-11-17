import json
import os
import shutil
import sys
import tempfile
import unittest

from src.File_manager import JSONFileHandler

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))


class TestJSONFileHandler(unittest.TestCase):
    """Тесты для класса JSONFileHandler"""

    def setUp(self):
        """Создание временной папки для тестовых файлов"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "vacancies.json")
        self.file_handler = JSONFileHandler(self.test_file)

        self.sample_vacancy_1 = {
            "title": "Python Developer",
            "url": "https://hh.ru/vacancy/1",
            "salary": {"salary_data": 100000, "salary_display": "Зарплата: 100000"},
            "company": "Tech Company",
            "description": "Python experience required",
        }

        self.sample_vacancy_2 = {
            "title": "Data Scientist",
            "url": "https://hh.ru/vacancy/2",
            "salary": {"salary_data": 120000, "salary_display": "Зарплата: 120000"},
            "company": "Data Corp",
            "description": "Machine learning skills",
        }

    def tearDown(self):
        """Очистка после тестов"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_add_vacancy(self):
        """Тест добавления вакансии"""
        self.file_handler.add_vacancy(self.sample_vacancy_1)

        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Python Developer")

    def test_add_duplicate_vacancy(self):
        """Тест добавления дубликата вакансии"""
        self.file_handler.add_vacancy(self.sample_vacancy_1)
        self.file_handler.add_vacancy(self.sample_vacancy_1)

        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(len(data), 1)

    def test_filter_vacancies_by_title(self):
        """Тест фильтрации по названию"""
        self.file_handler.add_vacancy(self.sample_vacancy_1)
        self.file_handler.add_vacancy(self.sample_vacancy_2)

        result = self.file_handler.filtered_vacancies(title="Python")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Python Developer")

    def test_filter_vacancies_by_salary(self):
        """Тест фильтрации по зарплате"""
        self.file_handler.add_vacancy(self.sample_vacancy_1)
        self.file_handler.add_vacancy(self.sample_vacancy_2)

        result = self.file_handler.filtered_vacancies(salary_min=110000)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Data Scientist")

    def test_filter_vacancies_by_description(self):
        """Тест фильтрации по описанию"""
        self.file_handler.add_vacancy(self.sample_vacancy_1)
        self.file_handler.add_vacancy(self.sample_vacancy_2)

        result = self.file_handler.filtered_vacancies(description="machine")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Data Scientist")

    def test_delete_vacancy(self):
        """Тест удаления вакансии"""
        self.file_handler.add_vacancy(self.sample_vacancy_1)
        self.file_handler.add_vacancy(self.sample_vacancy_2)

        self.file_handler.delete_vacancy("https://hh.ru/vacancy/1")

        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["url"], "https://hh.ru/vacancy/2")

    def test_delete_all_vacancies(self):
        """Тест очистки всех вакансий"""
        self.file_handler.add_vacancy(self.sample_vacancy_1)
        self.file_handler.add_vacancy(self.sample_vacancy_2)

        self.file_handler.delete_vacancy()

        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(len(data), 0)


if __name__ == "__main__":
    unittest.main()
