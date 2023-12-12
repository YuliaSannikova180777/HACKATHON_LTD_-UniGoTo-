import os
import zipfile
import pandas as pd
from joblib import Parallel, delayed
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Получаем путь к текущей папке скриптов src/
current_dir = os.path.dirname(os.path.abspath(__file__))  # для .py
# current_dir = os.getcwd()  # для .ipynb

# Находим папку проекта относительно папки src/
project_path = os.path.abspath(os.path.join(current_dir, os.pardir))
print(f"Путь к папке проекта '{project_path}'")

# Задаём путь к папке данных относительно папки проекта
data_folder = os.path.join(project_path, 'data')

# Задаём пути и имена файлов для сохранения результатов
input_file = 'preprocessed_data.csv'
input_zip_path = os.path.join(data_folder, input_file[:-4] + '.zip')
input_csv_path = os.path.join(data_folder, input_file)
output_folder = os.path.join(project_path, 'recommendations')

# Создаём папку для хранения отобранных рекомендаций, если её нет
os.makedirs(output_folder, exist_ok=True)

# Проверяем наличие ZIP-архива
if os.path.exists(input_zip_path):
    # Извлекаем содержимое архива
    with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
        if input_file in zip_ref.namelist():
            zip_ref.extract(input_file, data_folder)
    input_file_path = input_zip_path
else:
    input_file_path = input_csv_path

# Загружаем файл с 10000 отфильтрованных данных
data = pd.read_csv(input_file_path, nrows=10000)

# Обрабатываем пропущенные значения в столбце 'preprocessed_interests'
data['preprocessed_interests'].fillna('', inplace=True)

# Создаём разреженную матрицу TF-IDF для преобразования строк интересов пользователей
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = csr_matrix(tfidf_vectorizer.fit_transform(data['preprocessed_interests']))

# Задаём порог для сохранения косинусных сходств
# threshold = 0.5  # Мало относящиеся сходства отбросим

# Модель рекомендации на основе TF-IDF и косинусного сходства
# вычисляет оценку сходства между векторами в диапазоне от 0 до 1
def calculate_cosine_similarity(index):
    print(f"Вычисление косинусного сходства для строки {index}")
    return cosine_similarity(tfidf_matrix[index], tfidf_matrix)

# Вычисляем косинусное сходство параллельным способом
num_cores = 10  # Количество ядер процессора
cosine_sims = Parallel(n_jobs=num_cores)(delayed(calculate_cosine_similarity)(i) for i in range(tfidf_matrix.shape[0]))

# Сохраняем в файлы рекомендаций только те сходства, которые превышают порог
for idx, cosine_sim in enumerate(cosine_sims):
    # Преобразуем матрицу сходства в плоский список
    similarity_values = cosine_sim.flatten()
    
    similarities = pd.DataFrame({'cosine_similarity': similarity_values})
    
    # Добавляем индексы университетов как первый столбец
    similarities.insert(0, 'university', range(len(similarity_values)))
    
    # Сохраняем датафрейм в файл рекомендаций
    similarities.to_csv(os.path.join(output_folder, f'user_{idx}_similarities.csv'), index=False)
    print(f"Файл с рекомендациями 'user_{idx}_similarities.csv' сохранён")

print("Все файлы с рекомендациями сохранены в папке 'recommendations/'")

# Задаём путь к папке рекомендаций относительно папки проекта
recommendations_folder = os.path.join(project_path, 'recommendations')

# Получение списка файлов в папке рекомендаций
file_list = os.listdir(recommendations_folder)

# Считываем 10 первых файлов рекомендаций
for file in file_list[:10]:
    if file.endswith('.csv'):  # Убеждаемся, что файлы - это CSV-файлы
        file_path = os.path.join(recommendations_folder, file)
        # Загружаем данны из CSV файла
        data = pd.read_csv(file_path)
        
        # Сортируем по убыванию сходства
        data.sort_values(by='cosine_similarity', ascending=False, inplace=True)

        # Получаем ТОП-20 рекомендованных ВУЗов
        recommended_universities = data.head(20)['university'].tolist()
        
        # Извлекаем индекс из имени файла
        idx = file.split('_')[1]

        # Вывод ТОП-20 рекомендованных ВУЗов для данного файла
        print(f"Для строки {idx}, ТОП-20 рекомендованных ВУЗов: {recommended_universities}")