import os
import zipfile
import shutil
import pandas as pd


# Получаем путь к текущей папке скриптов src/
current_dir = os.path.dirname(os.path.abspath(__file__))  # для .py
# current_dir = os.getcwd()  # для .ipynb

# Находим папку проекта относительно папки src/
project_path = os.path.abspath(os.path.join(current_dir, os.pardir))
print(f"Путь к папке проекта '{project_path}'")

# Задаём пути к папкам относительно папки проекта
folder_path = os.path.join(project_path, 'raw_data')
extracted_folder = os.path.join(project_path, 'extracted_data')

# Получаем список файлов в папке
files = os.listdir(folder_path)

# Задаём список столбцов, которые должны содержать значения типа integer
int_col_names = ['university', 'faculty', 'graduation', 'country_id', 'city_id']

# Создаём множество для хранения уникальных файлов с ошибками
error_file_set = set()

# Создаём словарь для хранения всех строк, которые требуется удалить из файлов
rows_to_remove = {}

# Считываем каждый файл CSV из архива ZIP
for file in files:
    if file.endswith('.zip'):
        file_path = os.path.join(folder_path, file)
        
        # Открываем архив ZIP
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Ищем первый файл CSV внутри архива и читаем его
            for zip_file in zip_ref.namelist():
                if zip_file.endswith('.csv'):
                    with zip_ref.open(zip_file) as csv_file:
                        try:
                            # Считываем только указанные столбцы
                            df = pd.read_csv(csv_file, usecols=int_col_names)
                            
                            for col in int_col_names:
                                # Находим значения, которые не являются целыми числами
                                non_int_values = df[~df[col].astype(str).str.isdigit()][col].unique()
                                
                                for val in non_int_values:
                                    # Добавляем название файла с ошибкой во множество файлов с ошибками
                                    error_file_set.add(file)
                                    
                                    # Проверяем, существует ли уже данное значение в словаре rows_to_remove
                                    if file not in rows_to_remove:
                                        rows_to_remove[file] = set()
                                    
                                    # Добавляем значения для удаления из файла
                                    rows_to_remove[file].add(val)
                                    
                        except pd.errors.ParserError as e:
                            # Добавляем название файла с ошибкой во множество файлов с ошибками
                            error_file_set.add(file)
                            print(f"Ошибка разбора файла {file}: {str(e)}")
                    break  # Прерываем цикл, чтобы прочитать только первый CSV-файл из архива

# Создаём папку для разархивированных данных, если её нет
os.makedirs(extracted_folder, exist_ok=True)

# Извлекаем содержимое ZIP-архивов и заменяем файлы с ошибками
for file in os.listdir(folder_path):
    if file.endswith('.zip'):
        file_path = os.path.join(folder_path, file)
        
        # Определяем, является ли файл ошибочным
        if file in error_file_set:
            # Если файл ошибочный, то заменяем его
            try:
                # Извлекаем содержимое архива
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extracted_folder)
                
                # Путь к извлечённому файлу
                extracted_file_path = os.path.join(extracted_folder, file.replace('.zip', '.csv'))
                
                # Загрузка файла в DataFrame
                df = pd.read_csv(extracted_file_path)
                
                # Проверяем, есть ли строки, которые нужно удалить из данного файла
                if file in rows_to_remove:
                    # Удаляем строки, содержащие значения для удаления
                    df = df[~df.isin(rows_to_remove[file]).any(axis=1)]
                    
                    # Перезапись файла без удалённых строк
                    df.to_csv(extracted_file_path, index=False)
                    print(f"Удалены строки из файла {extracted_file_path}")
                    
                # Удаляем временную папку с извлечёнными данными
                shutil.rmtree(extracted_folder)
                
                # Переименовываем обработанный файл внутри архива
                with zipfile.ZipFile(file_path, 'a') as zip_ref:
                    zip_ref.write(extracted_file_path, arcname=file.replace('.zip', '.csv'))
                    
                print(f"Файл {file} успешно обновлён в архиве")
            except Exception as e:
                print(f"Ошибка при обработке файла {file}: {str(e)}")
        else:
            print(f"Файл {file} не требует замены")