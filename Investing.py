import requests
import apimoex
import sqlite3
from sqlite3 import Error as e


# поиск цены акции по тикеру
def share_price(ticker):
    with requests.Session() as session:
        data = apimoex.get_board_history(session, ticker.upper())
        price = data[-1]['CLOSE']
        return price


# подключение к бд
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except e:
        print(f"The error '{e}' occurred")

    return connection


# создание таблицы для пользователя
def create_table(user_id):
    table_name = "user_" + str(user_id)
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute(f"DROP TABLE {table_name}")
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, stock TEXT, price_of_purchase FLOAT, price FLOAT, amount INTEGER DEFAULT 1)")
    print(f"Table '{table_name}' has been created successfully")
    connection.commit()
    connection.close()


# задаем депозит
def insert_main(user_id, dep):
    table_name = 'main'
    try:
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute(
            f"INSERT INTO {table_name} (id, deposit) VALUES (?, ROUND(?, 2))", (user_id, dep))
        print("Депозит записан!")
        connection.commit()
        return True
    except sqlite3.Error as e:
        print('Депозит не записан:', e)
        return False
    finally:
        if connection:
            connection.close()


# покупка акции и внесение данных
def insert_data(user_id, stock, price_of_purchase):
    table_name = "user_" + str(user_id)
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    # Проверяем, есть ли уже такая акция в таблице
    query_is_stock_exist = f"SELECT stock, AVG(price_of_purchase), amount FROM {table_name} WHERE stock = ?"
    cursor.execute(query_is_stock_exist, (stock.upper(),))
    stock_data = cursor.fetchone()
    if stock_data[0]:
        # Если акция уже есть в таблице, увеличиваем количество и усредняем стоимость
        amount = stock_data[2] + 1
        avg_stock_price = (
            stock_data[1] * stock_data[2] + price_of_purchase) / amount

        query_insert_exist_stock = f"UPDATE {table_name} SET price_of_purchase = ?, amount = ? WHERE stock = ?"
        cursor.execute(query_insert_exist_stock,
                       (round(avg_stock_price, 2), amount, stock.upper()))
    else:
        # Иначе добавляем новую запись
        query_insert_new_stock = f"INSERT INTO {table_name} (stock, price_of_purchase) VALUES (?, ?)"
        cursor.execute(query_insert_new_stock,
                       (stock.upper(), price_of_purchase))

    connection.commit()
    connection.close()

    print('Data inserted successfully')

# продажа акций
def update_data(user_id, stock, price_of_sale, amount_buy):
    table_name = "user_" + str(user_id)
    try:
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        # Проверяем, есть ли уже такая акция в таблице
        query_is_stock_exist = f"SELECT stock, ROUND(AVG(price_of_purchase), 2), amount FROM {table_name} WHERE stock = ?"
        cursor.execute(query_is_stock_exist, (stock.upper(),))
        stock_data = cursor.fetchone()
        if stock_data:
            # Если акция есть в таблице, уменьшаем количество акций
            quantity_of_stock = stock_data[2] - amount_buy
            print(amount_buy)
            print(stock_data[2])
            print(quantity_of_stock)
            # Проверяем, все ли акции проданы
            if quantity_of_stock == 0:
                # Удаляем запись
                query_delete_stock = f"DELETE FROM {table_name} WHERE stock = ?"
                cursor.execute(query_delete_stock, (stock.upper(),))
        else:
            # Иначе выводим ошибку
            print(f"Stock {stock.upper()} not found in table {table_name}")
            return

        # Вносим данные о продаже акций
        query_add_sale = f"UPDATE {table_name} SET stock = ?, price = ?, amount = ? WHERE stock = ?"
        cursor.execute(query_add_sale, (stock.upper(),
                       price_of_sale, quantity_of_stock, stock.upper()))

        connection.commit()
        print('Data updated successfully')

    except sqlite3.Error as error:
        print("Error while working with SQLite:", error)

    finally:
        if connection:
            connection.close()


# вносим изменения в депозит
def change_deposit(id, diff):
    table_name = "main"
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    dep12 = f"SELECT deposit FROM {table_name} WHERE id = ?"
    cursor.execute(dep12, (id,))
    deposit = cursor.fetchone()[0]

    new_deposit = deposit + diff
    update_query = f"UPDATE {table_name} SET deposit = ? WHERE id = ?"
    cursor.execute(update_query, (round(new_deposit, 2), id))
    connection.commit()

    connection.close()
    print('Депозит обновлен')


def info_deposit():
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT deposit FROM main")
    info_deposit = cursor.fetchone()
    return info_deposit[0]


def info_stock(id):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute(f"SELECT stock, price_of_purchase, amount FROM user_{id}")
    info_stock = cursor.fetchall()
    str_info_stock = str(info_stock)[1:-1]
    str_info_stock = str_info_stock.replace('(', '')
    str_info_stock = str_info_stock.replace('), ', '\n')
    str_info_stock = str_info_stock.replace(')', '')
    str_info_stock = str_info_stock.replace("'", "")
    str_info_stock = str_info_stock.replace(', ', '   |   ')

    str_info_stock = 'Тикер | Средняя цена | Количество\n' + str_info_stock

    # str_info_stock = str_info_stock.replace(', ', '\\|    ')
    # str_info_stock = str_info_stock.replace('|', ' \\|')
    # str_info_stock = str_info_stock.replace('.', '\\.')
    try:
        return str_info_stock
    except IndexError:
        return 'Акций нет в твоем портфеле'
