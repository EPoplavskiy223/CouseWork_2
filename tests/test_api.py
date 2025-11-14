import os
import sys
import unittest
from unittest.mock import Mock, patch

from src.API_interaction import HeadHunterAPI, Vacancy

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))


class TestHeadHunterAPI(unittest.TestCase):
    """Тесты для класса HeadHunterAPI"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.api = HeadHunterAPI()

        # Тестовые данные API
        self.mock_api_response = {
            "items": [
                {
                    "name": "Python Developer",
                    "alternate_url": "https://hh.ru/vacancy/1",
                    "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                    "snippet": {"requirement": "Experience with Python"},
                    "employer": {"name": "Tech Company"},
                },
                {
                    "name": "Data Scientist",
                    "alternate_url": "https://hh.ru/vacancy/2",
                    "salary": {"from": 120000, "to": None, "currency": "RUR"},
                    "snippet": {"requirement": "Machine learning"},
                    "employer": {"name": "Data Company"},
                },
            ]
        }

    @patch("API_interaction.requests.get")
    def test_get_vacancies_with_query(self, mock_get):
        """Тест поиска вакансий с запросом"""

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_api_response
        mock_get.return_value = mock_response

        result = self.api.get_vacancies("python")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Python Developer")

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]["params"]["text"], "python")
        self.assertEqual(call_args[1]["params"]["per_page"], 100)

    @patch("API_interaction.requests.get")
    def test_get_vacancies_without_query(self, mock_get):
        """Тест поиска вакансий без запроса"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_api_response
        mock_get.return_value = mock_response

        result = self.api.get_vacancies()

        self.assertEqual(len(result), 2)
        mock_get.assert_called_once()

    @patch("API_interaction.requests.get")
    def test_get_vacancies_api_error(self, mock_get):
        """Тест обработки ошибки API"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = self.api.get_vacancies("python")

        self.assertEqual(result, [])

    @patch("API_interaction.requests.get")
    def test_get_vacancies_connection_error(self, mock_get):
        """Тест обработки ошибки соединения"""
        mock_get.side_effect = Exception("Connection error")

        result = self.api.get_vacancies("python")

        self.assertEqual(result, [])


class TestVacancy(unittest.TestCase):
    """Тесты для класса Vacancy"""

    def setUp(self):
        """Тестовые данные для вакансий"""
        self.sample_data_full = {
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/1",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            "snippet": {"requirement": "Experience with Python, Django"},
            "employer": {"name": "Tech Company"},
        }

        self.sample_data_no_salary = {
            "name": "Volunteer",
            "alternate_url": "https://hh.ru/vacancy/2",
            "salary": None,
            "snippet": {"requirement": None},
            "employer": {"name": "Non-profit"},
        }

    def test_vacancy_creation_with_salary(self):
        """Тест создания вакансии с зарплатой"""
        vacancy = Vacancy(self.sample_data_full)

        self.assertEqual(vacancy.title, "Python Developer")
        self.assertEqual(vacancy.url, "https://hh.ru/vacancy/1")
        self.assertEqual(vacancy.company, "Tech Company")
        self.assertEqual(vacancy.salary_value, 125000)
        self.assertIn("Средняя зарплата: 125000", vacancy.salary_display)

    def test_vacancy_creation_without_salary(self):
        """Тест создания вакансии без зарплаты"""
        vacancy = Vacancy(self.sample_data_no_salary)

        self.assertEqual(vacancy.title, "Volunteer")
        self.assertEqual(vacancy.salary_value, 0)
        self.assertEqual(vacancy.salary_data["salary_display"], "Зарплата не указана")

    def test_vacancy_comparison(self):
        """Тест сравнения вакансий по зарплате"""

        high_salary_data = self.sample_data_full.copy()
        high_salary_data["salary"] = {"from": 200000, "to": 300000, "currency": "RUR"}

        vacancy_normal = Vacancy(self.sample_data_full)
        vacancy_high = Vacancy(high_salary_data)
        vacancy_no_salary = Vacancy(self.sample_data_no_salary)

        self.assertTrue(vacancy_high > vacancy_normal)
        self.assertTrue(vacancy_normal < vacancy_high)
        self.assertTrue(vacancy_normal > vacancy_no_salary)
        self.assertFalse(vacancy_normal == vacancy_high)

    def test_vacancy_to_dict(self):
        """Тест преобразования вакансии в словарь"""
        vacancy = Vacancy(self.sample_data_full)
        vacancy_dict = vacancy.to_dict()

        self.assertEqual(vacancy_dict["title"], "Python Developer")
        self.assertEqual(vacancy_dict["url"], "https://hh.ru/vacancy/1")
        self.assertEqual(vacancy_dict["company"], "Tech Company")
        self.assertIn("salary_data", vacancy_dict["salary"])

    def test_all_vacancies_list(self):
        """Тест создания списка вакансий"""
        data_list = [self.sample_data_full, self.sample_data_no_salary]
        vacancies = Vacancy.all_vacancies_list(data_list)

        self.assertEqual(len(vacancies), 2)
        self.assertIsInstance(vacancies[0], Vacancy)
        self.assertIsInstance(vacancies[1], Vacancy)

    def test_vacancy_string_representation(self):
        """Тест строкового представления вакансии"""
        vacancy = Vacancy(self.sample_data_full)
        vacancy_str = str(vacancy)

        self.assertIn("Python Developer", vacancy_str)
        self.assertIn("Tech Company", vacancy_str)
        self.assertIn("Средняя зарплата: 125000", vacancy_str)

    def test_salary_validation_scenarios(self):
        """Тест различных сценариев валидации зарплаты"""

        data_only_from = {
            "name": "Test",
            "alternate_url": "test",
            "salary": {"from": 100000, "to": None, "currency": "RUR"},
            "snippet": {"requirement": ""},
            "employer": {"name": "Test"},
        }
        vacancy_only_from = Vacancy(data_only_from)
        self.assertEqual(vacancy_only_from.salary_value, 100000)

        data_only_to = {
            "name": "Test",
            "alternate_url": "test",
            "salary": {"from": None, "to": 100000, "currency": "RUR"},
            "snippet": {"requirement": ""},
            "employer": {"name": "Test"},
        }
        vacancy_only_to = Vacancy(data_only_to)
        self.assertEqual(vacancy_only_to.salary_value, 75000)


if __name__ == "__main__":
    unittest.main()
