# import requests
import json
import re
import time

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from SKU_read import sku_list


def add_or_update_review_to_json(sku, review_text, review_time):
    try:
        # Проверка наличия файла и его содержимого
        try:
            with open('parsing_control.json', 'r', encoding='UTF-8') as json_file:
                reviews_dict = json.load(json_file)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            # Если файл пустой или не существует, создаем пустой словарь
            reviews_dict = {}

        # Добавление или обновление данных
        if sku in reviews_dict:
            # Если запись для данного sku уже существует, обновляем данные
            reviews_dict[sku]['review_text'] = review_text
            reviews_dict[sku]['review_time'] = review_time
            print(f"Данные для SKU {sku} успешно обновлены в JSON файле.")
        else:
            # Если записи для данного sku нет, добавляем новую
            reviews_dict[sku] = {'review_text': review_text, 'review_time': review_time}
            print(f"Данные для SKU {sku} успешно добавлены в JSON файл.")

        # Запись обновленных данных в JSON файл
        with open('parsing_control.json', 'w', encoding='UTF-8') as json_file:
            json.dump(reviews_dict, json_file, ensure_ascii=False, indent=4)

    except Exception as e:
        print("Ошибка при обновлении данных в JSON файле:", e)


def get_review_data_from_json(sku):
    try:
        with open('parsing_control.json', 'r', encoding='UTF-8') as json_file:
            reviews_dict = json.load(json_file)

            if sku in reviews_dict:
                review_data = reviews_dict[sku]
                review_text = review_data['review_text']
                review_time = review_data['review_time']
                return review_text, review_time
            else:
                print(f"SKU {sku} не найден в JSON файле.")
                return None, None
    except FileNotFoundError:
        print("JSON файл не найден.")
        return None, None
    except Exception as e:
        print("Ошибка при чтении JSON файла:", e)
        return None, None


def check_sku_in_json(sku):
    try:
        with open('parsing_control.json', 'r', encoding='UTF-8') as json_file:
            data = json_file.read()
            if not data:  # Если файл пустой, вернуть False
                return False
            reviews_dict = json.loads(data)
            if str(sku) in reviews_dict:
                return True
            else:
                return False
    except FileNotFoundError:
        print("JSON файл не найден.")
        return False
    except json.decoder.JSONDecodeError:
        print("Ошибка при чтении JSON файла: файл пустой или содержит некорректные данные.")
        return False
    except Exception as e:
        print("Ошибка при чтении JSON файла:", e)
        return False


def get_product_info(sku_list):
    details = []
    url = f'https://www.wildberries.ru/catalog/'
    service = r"chromedriver.exe"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('-profile')
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-agent={UserAgent().random}")  # Use a random User-Agent
    driver = webdriver.Chrome(options=chrome_options)
    for sku in sku_list:
        driver.get(f'{url}{sku}/detail.aspx')
        time.sleep(7)
        product_name = driver.find_element(By.CLASS_NAME, 'product-page__title')
        # Прокрутите страницу к этому элементу
        actions = ActionChains(driver)
        actions.move_to_element(product_name).perform()

        # Получите текст элемента product_name
        product_name_text = product_name.text
        product_rating = driver.find_element(By.CLASS_NAME, 'product-review__rating').text
        time.sleep(5)

        # Параметры прокрутки
        scroll_interval = 200  # Интервал прокрутки в пикселях
        max_scroll_attempts = 10  # Максимальное количество попыток прокрутки
        scroll_attempts = 0
        while scroll_attempts < max_scroll_attempts:
            # Прокрутка страницы вниз до конца
            driver.execute_script(f"window.scrollBy(0, {scroll_interval});")
            time.sleep(1)
            try:
                driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div/div[3]/'
                                              'div/div[3]/div[8]/div[3]/a').click()
                time.sleep(5)
                # Если элемент найден, прервать цикл
                break
            except NoSuchElementException:
                # Если элемент не найден, увеличим количество попыток и продолжим прокрутку
                scroll_attempts += 1

        if check_sku_in_json(sku):
            last_reviews = driver.find_elements(By.CLASS_NAME, 'comments__item')

            # Получение данных из элемента с индексом 0
            first_review_element_null = last_reviews[0]
            first_review_HTML_null = first_review_element_null.get_attribute('outerHTML')
            soup_null = BeautifulSoup(first_review_HTML_null, 'html.parser')
            time_element_null = soup_null.find("span", class_="feedback__date")
            time_review_null = time_element_null.get("content")
            review_element_null = soup_null.find("p", class_="feedback__text")
            review_null = review_element_null.get_text(strip=True)

            review_data_from_json = get_review_data_from_json(str(sku))
            print(review_data_from_json)
            if time_review_null == review_data_from_json[1] and review_null == review_data_from_json[0]:
                continue
            else:
                for last_review in last_reviews:

                    last_review_HTML = last_review.get_attribute('outerHTML')
                    soup = BeautifulSoup(last_review_HTML, 'html.parser')

                    # Извлекаем время
                    time_element = soup.find("span", class_="feedback__date")
                    time_review = time_element.get("content")

                    # Извлекаем рейтинг
                    rating_element = soup.find("span", class_="feedback__rating")
                    rating = int(re.search(r'\bstar(\d+)\b', rating_element["class"][2]).group(1))

                    # Извлекаем отзыв
                    review_element = soup.find("p", class_="feedback__text")
                    review = review_element.get_text(strip=True)
                    print(time_review, rating, review)

                    if last_review == len(last_reviews):
                        pass

                    # Проверка на совпадение с предыдущим отзывом
                    if review == review_data_from_json[1] and time_review == review_data_from_json[0]:
                        # Если отзыв такой же, прекращаем поиск
                        break

                    if rating <= 4:
                        details.append({
                            'sku': sku,
                            'product_name': product_name_text,
                            'product_rating': product_rating,

                            'review_text': review,
                            'review_stars': rating,
                        })
                add_or_update_review_to_json(sku, review_text=review_null, review_time=time_review_null)
        else:
            last_reviews = driver.find_elements(By.CLASS_NAME, 'comments__item')
            for last_review in last_reviews:
                last_review_HTML = last_review.get_attribute('outerHTML')

                # Создаем объект BeautifulSoup для парсинга HTML
                soup = BeautifulSoup(last_review_HTML, 'html.parser')

                # Извлекаем время
                time_element = soup.find("span", class_="feedback__date")
                time_review = time_element.get("content")

                # Извлекаем отзыв
                review_element = soup.find("p", class_="feedback__text")
                review = review_element.get_text(strip=True)

                add_or_update_review_to_json(sku, review_text=review, review_time=time_review)
                continue

        print(details)
        return details


sku_info = get_product_info(sku_list)
