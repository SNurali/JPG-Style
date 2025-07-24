import requests

def get_usd_to_uzs_rate():
    try:
        response = requests.get('https://cbu.uz/uz/arkhiv-kursov-valyut/json/USD/')
        data = response.json()
        rate = float(data[0]['Rate'].replace(',', ''))  # Убираем запятую, если есть
        return rate
    except Exception as e:
        print(f"Ошибка при получении курса: {e}")
        return 12500  # Фиксированный курс по умолчанию
