# flake8: noqa: E402
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from src.user_interaction import (
    condition_format_print_in_file,
    format_print,
    save_vacancies,
    search_vacancies_api,
    search_vacancies_file,
    title_menu,
    top_vacancies_by_salary,
    user_input_int,
    user_input_search,
    user_interaction,
)


class TestUserInteraction(unittest.TestCase):
    """Тесты для модуля user_interaction"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.sample_vacancies = [
            {
                "title": "Python Developer",
                "company": "Tech Company",
                "salary": {
                    "salary_display": "Зарплата от: 100000",
                    "salary_value": 100000,
                },
                "description": "Experience with Python",
                "url": "https://hh.ru/vacancy/1",
            },
            {
                "title": "Data Scientist",
                "company": "Data Corp",
                "salary": {
                    "salary_display": "Средняя зарплата: 125000",
                    "salary_value": 125000,
                },
                "description": "Machine learning skills",
                "url": "https://hh.ru/vacancy/2",
            },
        ]

    def test_user_input_int_valid(self):
        """Тест ввода корректного числа"""
        with patch("builtins.input", return_value="5"):
            result = user_input_int()
            self.assertEqual(result, 5)

    def test_user_input_int_with_custom_prompt(self):
        """Тест ввода числа с кастомным приглашением"""
        with patch("builtins.input", return_value="10"):
            result = user_input_int("Введите количество: ")
            self.assertEqual(result, 10)

    @patch("builtins.print")
    def test_user_input_int_retry_on_invalid(self, mock_print):
        """Тест повторных попыток при неверном вводе"""
        with patch("builtins.input", side_effect=["invalid", "abc", "3"]):
            result = user_input_int()
            self.assertEqual(result, 3)
            mock_print.assert_called_with("Введите число")

    def test_user_input_search_with_text(self):
        """Тест ввода поискового запроса"""
        with patch("builtins.input", return_value="python developer"):
            result = user_input_search()
            self.assertEqual(result, "python developer")

    def test_user_input_search_empty(self):
        """Тест пустого ввода"""
        with patch("builtins.input", return_value=""):
            result = user_input_search()
            self.assertIsNone(result)

    def test_user_input_search_with_custom_prompt(self):
        """Тест ввода с кастомным приглашением"""
        with patch("builtins.input", return_value="https://hh.ru/vacancy/1"):
            result = user_input_search("Введите URL: ")
            self.assertEqual(result, "https://hh.ru/vacancy/1")

    @patch("builtins.print")
    def test_title_menu(self, mock_print):
        """Тест отображения меню"""
        title_menu()

        calls = mock_print.call_args_list
        menu_texts = [c[0][0] for c in calls]

        self.assertIn("======== Меню вакансий ========", menu_texts)
        self.assertTrue(
            any(
                "1. Поиск вакансий по ключевому слову из hh.ru" in str(text)
                for text in menu_texts
            )
        )
        self.assertTrue(any("6. Выход" in str(text) for text in menu_texts))

    @patch("builtins.print")
    def test_format_print(self, mock_print):
        """Тест форматированного вывода вакансий"""
        format_print(self.sample_vacancies)

        output = "\n".join(str(c[0][0]) for c in mock_print.call_args_list)

        self.assertIn("Вакансия №1", output)
        self.assertIn("Python Developer", output)
        self.assertIn("Tech Company", output)
        self.assertIn("Зарплата от: 100000", output)
        self.assertIn("Experience with Python", output)

    @patch("src.user_interaction.json_manager")
    def test_top_vacancies_by_salary(self, mock_json_manager):
        """Тест получения топ-N вакансий по зарплате"""
        mock_json_manager.read_json.return_value = self.sample_vacancies

        with patch("src.user_interaction.format_print") as mock_format_print:
            top_vacancies_by_salary(1)

            mock_format_print.assert_called_once()
            called_data = mock_format_print.call_args[0][0]
            self.assertEqual(len(called_data), 1)
            self.assertEqual(called_data[0]["title"], "Data Scientist")

    @patch("src.user_interaction.json_manager")
    def test_condition_format_print_in_file(self, mock_json_manager):
        """Тест вывода всех вакансий из файла"""
        mock_json_manager.read_json.return_value = self.sample_vacancies

        with patch("src.user_interaction.format_print") as mock_format_print:
            condition_format_print_in_file()

            mock_format_print.assert_called_once_with(self.sample_vacancies)

    @patch("src.user_interaction.json_manager")
    def test_save_vacancies_with_objects(self, mock_json_manager):
        """Тест сохранения вакансий из объектов"""
        mock_vacancy = MagicMock()
        mock_vacancy.to_dict.return_value = self.sample_vacancies[0]

        save_vacancies(vacancy_obj=[mock_vacancy])

        mock_json_manager.add_vacancy.assert_called_once_with(self.sample_vacancies[0])

    @patch("src.user_interaction.json_manager")
    def test_save_vacancies_with_dicts(self, mock_json_manager):
        """Тест сохранения вакансий из словарей"""
        save_vacancies(vacancy_dict=[self.sample_vacancies[0]])

        mock_json_manager.add_vacancy.assert_called_once_with(self.sample_vacancies[0])

    @patch("src.user_interaction.cl_api")
    @patch("src.user_interaction.cl_vacancy")
    @patch("src.user_interaction.save_vacancies")
    def test_search_vacancies_api(self, mock_save, mock_cl_vacancy, mock_cl_api):
        """Тест поиска вакансий через API"""
        mock_api_response = [{"name": "Python Developer"}]
        mock_cl_api.get_vacancies.return_value = mock_api_response

        mock_vacancy_list = [MagicMock()]
        mock_cl_vacancy.all_vacancies_list.return_value = mock_vacancy_list

        search_vacancies_api("python")

        mock_cl_api.get_vacancies.assert_called_once_with("python")
        mock_cl_vacancy.all_vacancies_list.assert_called_once_with(mock_api_response)
        mock_save.assert_called_once_with(vacancy_obj=mock_vacancy_list)

    @patch("src.user_interaction.json_manager")
    @patch("src.user_interaction.save_vacancies")
    @patch("src.user_interaction.format_print")
    def test_search_vacancies_file_by_salary(
        self, mock_format, mock_save, mock_json_manager
    ):
        """Тест поиска в файле по зарплате"""
        mock_json_manager.filtered_vacancies.return_value = [self.sample_vacancies[0]]

        search_vacancies_file("100000")

        mock_json_manager.filtered_vacancies.assert_called_once_with(salary_min=100000)
        mock_save.assert_called_once_with(vacancy_dict=[self.sample_vacancies[0]])
        mock_format.assert_called_once_with([self.sample_vacancies[0]])

    @patch("src.user_interaction.json_manager")
    @patch("src.user_interaction.save_vacancies")
    @patch("src.user_interaction.format_print")
    def test_search_vacancies_file_by_description(
        self, mock_format, mock_save, mock_json_manager
    ):
        """Тест поиска в файле по описанию"""
        mock_json_manager.filtered_vacancies.return_value = [self.sample_vacancies[0]]

        search_vacancies_file("python")

        mock_json_manager.filtered_vacancies.assert_called_once_with(
            description="python"
        )
        mock_save.assert_called_once_with(vacancy_dict=[self.sample_vacancies[0]])
        mock_format.assert_called_once_with([self.sample_vacancies[0]])

    @patch("src.user_interaction.json_manager")
    def test_search_vacancies_file_none_search(self, mock_json_manager):
        """Тест поиска с пустым запросом"""
        result = search_vacancies_file(None)

        self.assertEqual(result, "Введите что-то и попробуйте еще раз")

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("src.user_interaction.user_input_int")
    @patch("src.user_interaction.user_input_search")
    @patch("src.user_interaction.search_vacancies_api")
    @patch("src.user_interaction.condition_format_print_in_file")
    def test_user_interaction_option_1(
        self,
        mock_condition_print,
        mock_search_api,
        mock_user_search,
        mock_user_int,
        mock_print,
        mock_input,
    ):
        """Тест опции 1 - поиск по ключевому слову"""
        mock_user_int.side_effect = [1, 6]
        mock_user_search.return_value = "python"

        user_interaction()

        mock_search_api.assert_called_once_with("python")
        mock_condition_print.assert_called_once()

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("src.user_interaction.user_input_int")
    @patch("src.user_interaction.top_vacancies_by_salary")
    def test_user_interaction_option_2(
        self, mock_top_salary, mock_user_int, mock_print, mock_input
    ):
        """Тест опции 2 - топ вакансий по зарплате"""
        mock_user_int.side_effect = [2, 5, 6]

        user_interaction()

        mock_top_salary.assert_called_once_with(5)

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("src.user_interaction.user_input_int")
    @patch("src.user_interaction.user_input_search")
    @patch("src.user_interaction.search_vacancies_file")
    def test_user_interaction_option_3(
        self, mock_search_file, mock_user_search, mock_user_int, mock_print, mock_input
    ):
        """Тест опции 3 - поиск по описанию"""
        mock_user_int.side_effect = [3, 6]
        mock_user_search.return_value = "developer"

        user_interaction()

        mock_search_file.assert_called_once_with("developer")

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("src.user_interaction.user_input_int")
    @patch("src.user_interaction.json_manager")
    @patch("src.user_interaction.format_print")
    def test_user_interaction_option_4(
        self,
        mock_format_print,
        mock_json_manager,
        mock_user_int,
        mock_print,
        mock_input,
    ):
        """Тест опции 4 - показать все вакансии"""
        mock_user_int.side_effect = [4, 6]
        mock_json_manager.read_json.return_value = self.sample_vacancies

        user_interaction()

        mock_json_manager.read_json.assert_called_once()
        mock_format_print.assert_called_once_with(self.sample_vacancies)

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("src.user_interaction.user_input_int")
    @patch("src.user_interaction.user_input_search")
    @patch("src.user_interaction.json_manager")
    def test_user_interaction_option_5(
        self, mock_json_manager, mock_user_search, mock_user_int, mock_print, mock_input
    ):
        """Тест опции 5 - удалить вакансию"""
        mock_user_int.side_effect = [5, 6]
        mock_user_search.return_value = "https://hh.ru/vacancy/1"

        user_interaction()

        mock_json_manager.delete_vacancy.assert_called_once_with(
            "https://hh.ru/vacancy/1"
        )

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("src.user_interaction.user_input_int")
    def test_user_interaction_invalid_option(
        self, mock_user_int, mock_print, mock_input
    ):
        """Тест обработки неверной опции меню"""
        mock_user_int.side_effect = [99, 6]

        user_interaction()
        error_printed = any(
            "Введите категорию из предложенных" in str(c[0][0])
            for c in mock_print.call_args_list
        )
        self.assertTrue(error_printed)

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("src.user_interaction.user_input_int")
    def test_user_interaction_exception_handling(
        self, mock_user_int, mock_print, mock_input
    ):
        """Тест обработки исключений в основном цикле"""
        mock_user_int.side_effect = Exception("Test error")

        try:
            user_interaction()
        except Exception:
            self.fail("user_interaction не обработал исключение")

        error_printed = any(
            "Ошибка: Test error" in str(c[0][0]) for c in mock_print.call_args_list
        )
        self.assertTrue(error_printed)
