import re
import os
import nltk
import zipfile
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


# Проверяем наличие необходимых ресурсов NLTK перед их загрузкой
try:
    nltk.data.find('punkt')
    nltk.data.find('stopwords')
    nltk.data.find('wordnet')
# Загружаем необходимые ресурсы для обработки
# текстовых данных из Natural Language Toolkit
except LookupError:
    nltk.download('punkt')  # токенизатор 
    nltk.download('stopwords')  # список стоп-слов
    nltk.download('wordnet')  # модуль для лемматизации

# Получаем путь к текущей папке скриптов src/
current_dir = os.path.dirname(os.path.abspath(__file__))  # для .py
# current_dir = os.getcwd()  # для .ipynb

# Находим папку проекта относительно папки src/
project_path = os.path.abspath(os.path.join(current_dir, os.pardir))
print(f"Путь к папке проекта '{project_path}'")

# Задаём путь к папке данных относительно папки проекта
data_folder = os.path.join(project_path, 'data')

# Задаём пути и имена файлов для сохранения в папке data/
input_file = 'filtered_data.csv'
input_zip_path = os.path.join(data_folder, input_file[:-4] + '.zip')
input_csv_path = os.path.join(data_folder, input_file)
output_file = 'preprocessed_data.csv'
output_path = os.path.join(data_folder, output_file)

# Проверяем наличие ZIP-архива
if os.path.exists(input_zip_path):
    # Извлекаем содержимое архива
    with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
        if input_file in zip_ref.namelist():
            zip_ref.extract(input_file, data_folder)
    input_file_path = input_zip_path
else:
    input_file_path = input_csv_path

# Загружаем файл с отфильтрованными данными
data = pd.read_csv(input_file_path)

# Создаём список столбцов интересов пользователей
interest_col = ['about', 'activities', 'books', 'games', 'interests']

# Функция предобработки текстовых данных
def preprocess_text(text):
    # Токенизируем текст на отдельные слова
    tokens = word_tokenize(text)
    
    # Задаём стоп-слова для русского и английского языков
    # (общие слова, не несущие смысловой нагрузки в контексте анализа)
    stop_words_ru = set(stopwords.words('russian'))
    stop_words_en = set(stopwords.words('english'))
    
    # Объединяем стоп-слова
    stop_words = stop_words_ru.union(stop_words_en)
    
    # Удаляем стоп-слова
    tokens = [word for word in tokens if word not in stop_words]
    
    # Инициализируем лемматизатор
    lemmatizer = WordNetLemmatizer()
    
    # Лемматизируем слова (приводим к их базовой форме - лемме)
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

# Задаём список для хранения предобработанных интересов
preprocessed_interests = []

# Применяем функцию предобработки текста к каждому набору интересов
# (из списка столбцов interest_col) для каждой строки в DataFrame
for _, row in data.iterrows():
    # Объединяем интересы в одну строку
    combined_interests = ' '.join([str(row[col]) for col in interest_col])
    preprocessed = preprocess_text(combined_interests)
    # Добавляем предобработанные интересы в список preprocessed_interests
    preprocessed_interests.append(preprocessed)

# Добавляем предобработанные интересы в DataFrame
data['preprocessed_interests'] = preprocessed_interests

# Удаляем столбцы interest_col
data.drop(columns=interest_col, inplace=True)

# Функция для очистки текста от лишних символов
def clean_text(text):
    # Применяем только к непустым (не NaN) значениям
    if not pd.isnull(text):
        # Заменяем 'nan' на ''
        text = re.sub(r'\b(nan)', '', text)
        
        # Удаляем повторяющиеся слова
        text = re.sub(r'\b(\w+)(\s+\1)+\b', r'\1', text)
        
        # Заменяем подряд идущие пробелы на один
        text = re.sub(r'\s+', ' ', text)
                
        # Удаляем пробелы в начале и конце строки
        text = re.sub(r'^\s+|\s+$', '', text)
    return text

# Применяем функцию очистки к столбцу 'preprocessed_interests'
data['preprocessed_interests'] = data['preprocessed_interests'].apply(clean_text)
print("Интересы очищены от лишних символов")

# Проверка и удаление строк с пустыми значениями в столбце 'preprocessed_interests'
data = data[data['preprocessed_interests'].str.strip().astype(bool)]
print("Строки с незаполненными интересами удалены")

# Сохраняем отфильтрованные данные в файл CSV
data.to_csv(output_path, index=False)
print(f"Файл {output_file} сохранён")