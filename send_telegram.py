import requests

TELEGRAM_TOKEN = "7492480842:AAFcwTRve8yolNVvPb1OAkiustwIz35mZII"
TELEGRAM_CHAT_ID = "532350689"

def send_order_to_telegram(order):
    """
    Отправляет информацию о заказе в Telegram
    """

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram токен или chat_id не указаны")
        return

    message = f"📦 Новый заказ #{order.id}\n\n"
    message += f"👤 Клиент: {order.customer_name}\n"
    message += f"📞 Телефон: {order.phone}\n"
    message += f"📍 Адрес: {order.address}\n"
    message += "🛒 Товары:\n"

    for item in order.items.all():
        message += f"• {item.product.name} — {item.quantity} шт. × {item.product.price} сум\n"

    message += f"\n💰 Итого: {order.total_price} сум"

    url = f"https://api.telegram.org/bot {TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Сообщение успешно отправлено в Telegram")
        else:
            print(f"❌ Ошибка при отправке: {response.text}")
    except Exception as e:
        print(f"⚠️ Не удалось отправить сообщение: {e}")
