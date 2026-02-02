from flask import Flask, render_template, request
import json
import requests
from datetime import datetime

# фласк
client_app = Flask(__name__)

# ============ КОНФИГ ============
SERVER_URL = "http://127.0.0.1:5000" 

@client_app.template_filter('tojson_pretty')
def tojson_pretty_filter(data):
    """Фильтр для красивого вывода JSON с кириллицей"""
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except:
        return str(data)

# ============ ВЕБ-ИНТЕРФЕЙС КЛИЕНТА ============
@client_app.route('/')
def index():
    """Главная страница с формой"""
    return render_template('index.html')

@client_app.route('/send', methods=['POST'])
def send():
    """Обработка формы и отправка запроса на сервер"""
    try:
        # забираем данные
        method = request.form.get('method', 'POST')
        endpoint = request.form.get('endpoint', '/api/users')
        data_text = request.form.get('data', '{}').strip()
        
        # парсинг джсон
        data_obj = {}
        if data_text:
            try:
                data_obj = json.loads(data_text)
            except json.JSONDecodeError:
                # если не джсон то как текст
                data_obj = {"text": data_text}
        
        print(f"[CLIENT {datetime.now().strftime('%H:%M:%S')}] 📤 Отправка запроса на сервер...")
        print(f"   Метод: {method}")
        print(f"   Эндпоинт: {endpoint}")
        print(f"   Данные: {json.dumps(data_obj, ensure_ascii=False)}")
        
        # url api
        api_url = f"{SERVER_URL}/api/process"
        payload = {
            'method': method,
            'endpoint': endpoint,
            'data': data_obj
        }
        
        # запрос
        response = requests.post(
            api_url, 
            json=payload, 
            timeout=10,
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )
        
        # обработка ответа сервера
        result = response.json()
        
        print(f"[CLIENT {datetime.now().strftime('%H:%M:%S')}] 📥 Ответ от сервера получен")
        print(f"   Статус: {result.get('status')}")
        print(f"   Сообщение: {result.get('message')}")
        
        return render_template('result.html', result=result)
            
    except requests.exceptions.ConnectionError:
        error_result = {
            'status': 'error',
            'error': f'Не удалось подключиться к серверу {SERVER_URL}',
            'message': 'Проверьте, что сервер запущен'
        }
        print(f"[CLIENT {datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка подключения к серверу")
        return render_template('result.html', result=error_result)
    
    except requests.exceptions.Timeout:
        error_result = {
            'status': 'error',
            'error': 'Таймаут соединения с сервером',
            'message': 'Сервер не ответил вовремя'
        }
        print(f"[CLIENT {datetime.now().strftime('%H:%M:%S')}] ⏰ Таймаут соединения")
        return render_template('result.html', result=error_result)
    
    except Exception as e:
        error_result = {
            'status': 'error',
            'error': f'Ошибка клиента: {str(e)}',
            'message': 'Проверьте правильность введенных данных'
        }
        print(f"[CLIENT {datetime.now().strftime('%H:%M:%S')}] ❌ Ошибка: {str(e)}")
        return render_template('result.html', result=error_result)

def run_client(host='127.0.0.1', port=5001):
    """Запуск клиента"""
    print("=" * 60)
    print("ЗАПУСК КЛИЕНТА (веб-интерфейс)")
    print(f"   Адрес: http://{host}:{port}")
    print(f"   Сервер API: {SERVER_URL}")
    print("")
    print(" Инструкция:")
    print("   1. Сначала запустите сервер: python server.py")
    print("   2. Затем откройте браузер: http://localhost:5001")
    print("   3. Отправляйте запросы через веб-форму")
    print("=" * 60)
    
    client_app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    run_client()