from flask import Flask, request, jsonify
import json
import uuid
import random
from datetime import datetime

# Flask 
server_app = Flask(__name__)

# ============ БД В ПАМЯТИ ============
class Database:
    def __init__(self):
        self.users = [
            {"id": 1, "name": "Иван Иванов", "role": "admin", "active": True},
            {"id": 2, "name": "Петр Петров", "role": "user", "active": True},
            {"id": 3, "name": "Анна Сидорова", "role": "manager", "active": False}
        ]
        self.orders = [
            {"id": 101, "user_id": 1, "product": "Ноутбук", "status": "доставлен"},
            {"id": 102, "user_id": 2, "product": "Телефон", "status": "в обработке"}
        ]
        self.products = [
            {"id": 1, "name": "Ноутбук", "price": 50000, "stock": 10},
            {"id": 2, "name": "Телефон", "price": 30000, "stock": 25},
            {"id": 3, "name": "Планшет", "price": 40000, "stock": 5}
        ]
        self.requests_log = []

db = Database()

# ============ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============
def handle_users(method, data):
    """Обработка пользователей"""
    if method == 'GET':
        return {
            'action': 'получение пользователей',
            'data': db.users,
            'message': f'Найдено {len(db.users)} пользователей'
        }
    
    elif method == 'POST':
        if 'name' not in data or 'role' not in data:
            return {'action': 'создание пользователя', 'error': 'Нет name или role'}
        
        user_id = len(db.users) + 1
        user = {"id": user_id, **data, "active": True}
        db.users.append(user)
        
        return {
            'action': 'создание пользователя',
            'data': user,
            'message': f'Пользователь {user["name"]} создан с ID {user_id}'
        }
    
    elif method == 'PUT':
        user_id = data.get('id')
        if not user_id:
            return {'action': 'обновление пользователя', 'error': 'Нет ID пользователя'}
        
        for user in db.users:
            if user["id"] == user_id:
                user.update(data)
                return {
                    'action': 'обновление пользователя',
                    'data': user,
                    'message': f'Пользователь ID {user_id} обновлен'
                }
        
        return {'action': 'обновление пользователя', 'error': 'Пользователь не найден'}
    
    elif method == 'DELETE':
        user_id = data.get('id')
        if not user_id:
            return {'action': 'удаление пользователя', 'error': 'Нет ID пользователя'}
        
        db.users = [u for u in db.users if u["id"] != user_id]
        return {
            'action': 'удаление пользователя',
            'data': {'deleted_id': user_id},
            'message': f'Пользователь ID {user_id} удален'
        }
    
    return {'action': 'работа с пользователями'}

def handle_products(method, data):
    """Обработка товаров"""
    if method == 'GET':
        return {
            'action': 'получение товаров',
            'data': db.products,
            'message': f'Товаров: {len(db.products)}'
        }
    return {'action': 'работа с товарами'}

def handle_orders(method, data):
    """Обработка заказов"""
    if method == 'GET':
        return {
            'action': 'получение заказов',
            'data': db.orders,
            'message': f'Заказов: {len(db.orders)}'
        }
    
    elif method == 'POST':
        if 'user_id' not in data or 'product' not in data:
            return {'action': 'создание заказа', 'error': 'Нет user_id или product'}
        
        order_id = len(db.orders) + 101
        order = {
            "id": order_id,
            **data,
            "status": "принят",
            "order_date": datetime.now().isoformat(),
            "tracking_number": f"TRACK-{random.randint(10000, 99999)}"
        }
        db.orders.append(order)
        
        return {
            'action': 'создание заказа',
            'data': order,
            'message': f'Заказ №{order_id} создан. Трек: {order["tracking_number"]}'
        }
    
    return {'action': 'работа с заказами'}

def handle_calculation(method, data):
    """Расчет стоимости"""
    if method == 'POST':
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return {'action': 'расчет стоимости', 'error': 'Нет ID товара'}
        
        # поиск товара
        product = None
        for p in db.products:
            if p['id'] == product_id:
                product = p
                break
        
        if not product:
            return {'action': 'расчет стоимости', 'error': 'Товар не найден'}
        
        # расчет
        unit_price = product['price']
        total = unit_price * quantity
        discount = 0.1 if quantity >= 3 else 0
        discount_amount = total * discount
        final_price = total - discount_amount
        
        result = {
            'product_name': product['name'],
            'product_id': product_id,
            'unit_price': unit_price,
            'quantity': quantity,
            'total_without_discount': total,
            'discount_percent': discount * 100,
            'discount_amount': discount_amount,
            'final_price': final_price,
            'currency': 'RUB',
            'calculation_time': datetime.now().isoformat()
        }
        
        return {
            'action': 'расчет стоимости',
            'data': result,
            'message': f'Стоимость {quantity} шт.: {final_price:.2f} руб. (скидка {discount*100}%)'
        }
    
    return {'action': 'расчеты'}

def handle_general(method, data):
    """Общая обработка"""
    result = {}
    
    if isinstance(data, dict):
        result['полученные_данные'] = data
        result['количество_полей'] = len(data)
        
        if 'name' in data:
            result['приветствие'] = f"Привет, {data['name']}!"
        
        if 'amount' in data and isinstance(data['amount'], (int, float)):
            result['сумма_с_налогом'] = data['amount'] * 1.2
    
    # логика по методам
    if method == 'POST':
        result['действие'] = 'создано'
        result['id'] = random.randint(1000, 9999)
    
    elif method == 'PUT':
        result['действие'] = 'обновлено'
    
    elif method == 'DELETE':
        result['действие'] = 'удалено'
    
    elif method == 'GET':
        result['действие'] = 'получено'
    
    return {
        'action': f'обработка данных ({method})',
        'data': result,
        'message': 'Данные успешно обработаны'
    }

# ============ ЭНДПОИНТЫ СЕРВЕРА ============
@server_app.route('/api/health', methods=['GET'])
def health():
    """Проверка работы сервера"""
    print(f"[SERVER {datetime.now().strftime('%H:%M:%S')}] GET /api/health")
    return jsonify({
        'status': 'healthy',
        'service': 'client-server-module',
        'timestamp': datetime.now().isoformat()
    })

@server_app.route('/api/process', methods=['POST'])
def process_request():
    """Основной обработчик запросов"""
    try:
        data = request.get_json()
        if not data:
            print(f"[SERVER {datetime.now().strftime('%H:%M:%S')}] POST /api/process -> ERROR: Нет данных")
            return jsonify({'error': 'Нет данных', 'status': 'error'}), 400
        
        method = data.get('method', 'GET')
        endpoint = data.get('endpoint', '/')
        input_data = data.get('data', {})
        
        request_id = str(uuid.uuid4())
        
        print(f"\n{'='*50}")
        print(f"[SERVER {datetime.now().strftime('%H:%M:%S')}] 📨 ЗАПРОС:")
        print(f"   ID: {request_id}")
        print(f"   Метод: {method}")
        print(f"   Эндпоинт: {endpoint}")
        print(f"   Данные: {json.dumps(input_data, ensure_ascii=False)}")
        print(f"{'='*50}")
        
        # определение обработчика
        result = {}
        if endpoint.startswith('/api/users'):
            result = handle_users(method, input_data)
        elif endpoint.startswith('/api/products'):
            result = handle_products(method, input_data)
        elif endpoint.startswith('/api/orders'):
            result = handle_orders(method, input_data)
        elif endpoint.startswith('/api/calculate'):
            result = handle_calculation(method, input_data)
        else:
            result = handle_general(method, input_data)
        
        # ответ
        response = {
            'request_id': request_id,
            'status': 'success',
            'method_used': method,
            'endpoint_used': endpoint,
            'server_action': result.get('action', 'обработка'),
            'data': result.get('data'),
            'message': result.get('message'),
            'timestamp': datetime.now().isoformat()
        }
        
        if 'error' in result:
            response['status'] = 'error'
            response['error'] = result['error']
            print(f"[SERVER {datetime.now().strftime('%H:%M:%S')}]  ОШИБКА: {result['error']}")
        else:
            print(f"[SERVER {datetime.now().strftime('%H:%M:%S')}]  УСПЕХ: {result.get('action')}")
            if result.get('data'):
                print(f"   Результат: {json.dumps(result['data'], ensure_ascii=False)}")
        
        print(f"{'='*50}\n")
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"[SERVER {datetime.now().strftime('%H:%M:%S')}]  КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

def run_server(host='127.0.0.1', port=5000):
    """Запуск сервера"""
    print("=" * 60)
    print("    ЗАПУСК СЕРВЕРА")
    print(f"   Адрес: http://{host}:{port}")
    print("    Доступные эндпоинты:")
    print("   GET  /api/health     - проверка работы")
    print("   POST /api/process    - обработка запросов")
    print("")
    print("   Примеры использования через curl:")
    print("   curl http://localhost:5000/api/health")
    print("   curl -X POST http://localhost:5000/api/process \\")
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"method": "GET", "endpoint": "/api/users", "data": {}}\'')
    print("=" * 60)
    
    server_app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    run_server()