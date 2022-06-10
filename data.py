import json

def users():
    with open('users.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data

def orders():
    with open('orders.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data

def offers():
    with open('offers.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data

