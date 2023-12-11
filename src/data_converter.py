import os
import pandas as pd


# Задаём список для считывания нужных столбцов
col_names = ['country_id',
             'country_title',
             'city_id',
             'city_title',
             'about',
             'activities',
             'books',
             'games',
             'interests',
             'education_form',
             'education_status',
             'university_id',
             'university_name',
             'faculty_id',
             'faculty_name',
             'graduation_year']

current_directory = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
file_path = os.path.join(current_directory, '1.csv')

# Считываем только указанные столбцы
data = pd.read_csv(file_path, usecols=col_names)

# Переносим указанные столбцы в конец таблицы
data = data[[col for col in data.columns
             if col not in ['country_id', 'country_title', 'city_id', 'city_title']] +
            ['university_id', 'faculty_id', 'graduation_year', 'country_id', 'country_title', 'city_id', 'city_title']]

# Переименовываем столбцы
data.rename(columns={'university_id': 'university', 'faculty_id': 'faculty', 'graduation_year': 'graduation'}, inplace=True)

# Просмотр первых нескольких строк данных
print(data.head())

data.to_csv('all_pages_data 698501-700000.csv', index=False, encoding='utf-8')
