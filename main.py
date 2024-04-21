import requests
import time
import pymysql 
import mysql.connector

# 替換成您的API金鑰
api_key = 'AIzaSyBX8nzXsygxsOIWwrG_cdnv20K0FiKiH_4'
location = '25.083, 121.555'
radius = '1000'  # 搜索範圍（以米為單位）
keyword = '義大利麵'  # 指定搜尋關鍵字
language = 'zh-TW'  # 指定語言為中文

def fetch_place_details(api_key, place_id, language):
    detail_url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = {
        'place_id': place_id,
        'fields': 'formatted_phone_number,formatted_address',
        'key': api_key,
        'language': language
    }
    response = requests.get(detail_url, params=params)
    details = response.json()

    # 獲取電話號碼和完整地址
    phone = details.get('result', {}).get('formatted_phone_number', 'No Contact Info')
    address = details.get('result', {}).get('formatted_address', 'No Address Info')
    return phone, address

def fetch_places(api_key, location, radius, keyword, language, page_token=None):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'location': location,
        'radius': radius,
        'keyword': keyword,
        'key': api_key,
        'language': language
    }
    if page_token:
        params['pagetoken'] = page_token

    response = requests.get(url, params=params)
    results = response.json()

    places = results.get('results', [])
    for place in places:
        name = place.get('name')
        place_id = place.get('place_id')
        rating = place.get('rating', 'No Rating')
        
        # 獲取電話號碼和完整地址
        phone, address = fetch_place_details(api_key, place_id, language)
        insert_to_mysql(place_id, name, address, rating, phone)
        
        print(f'Name: {name}, Address: {address}, Rating: {rating}, Phone: {phone}')
        

    # 檢查是否有下一頁
    page_token = results.get('next_page_token')
    return page_token

    
def insert_to_mysql(place_id, name, address, rating, phone):
    db_setting = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "password",  # 替换成您的密码
        "db": "restaurant",  # 确保数据库名正确
        "charset": "utf8"
    }
    
    try:
        #connection = connect_to_database()
                

        connection = mysql.connector.connect(
        host="localhost",
        user="local_user",
        password="password",
        database="food"
        )

        mycursor = connection.cursor()
        mycursor.execute("SHOW TABLES")
        for x in mycursor:
                print(x)
        mycursor.execute("CREATE DATABASE IF NOT EXISTS food")
        if connection:
            cursor = connection.cursor()
            query = """INSERT INTO places (place_id, name, address, rating) 
           VALUES (%s, %s, %s, %s) 
           ON DUPLICATE KEY UPDATE 
           name=VALUES(name), address=VALUES(address), rating=VALUES(rating);"""
            cursor.execute(query, (place_id, name, address, rating))
            connection.commit()
    except mysql.connector.Error as e:
        print(f"Error while inserting to MySQL: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == '__main__':
    # 初始請求
    page_token = fetch_places(api_key, location, radius, keyword, language)

    # 如果存在下一頁，則繼續請求
    while page_token:
        time.sleep(2)  # 等待token變得有效
        page_token = fetch_places(api_key, location, radius, keyword, language, page_token=page_token)
