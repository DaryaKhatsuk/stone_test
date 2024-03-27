import pandas as pd


def read_sku_from_excel(file_path):
    try:
        # Чтение файла Excel
        df = pd.read_excel(file_path)
        # Получение списка SKU из столбца 'SKU' (если столбец называется иначе, укажите его имя)
        sku_list = df['SKU'].tolist()
        return sku_list
    except Exception as e:
        print("Ошибка при чтении файла Excel:", e)
        return []


# Путь к вашему файлу Excel
file_path = "SKU.xlsx"

# Чтение SKU из файла Excel
sku_list = read_sku_from_excel(file_path)

# Печать списка SKU для проверки
print("Список SKU из файла Excel:", sku_list)
