from flask import jsonify
import datetime
from flask_pymongo import ObjectId


def get_jobs(collection):
    jobs = list(collection.find())
    job_list = []
    for job in jobs:
        job_data = {
            'job_id': str(job['_id']),
            "company_name": job['company_name'],
            "job_name": job['job_name'],
            "job_description": job['job_description'],
            "duration": job['duration'],
            "when_needed": job['when_needed'],
            "average_pay": job['average_pay'],
            "part_time": job['part_time'],
            "location": job['location'],
            "latitude": job['latitude'],
            "longitude": job['longitude']
        }
        job_list.append(job_data)
    return jsonify(job_list)


def get_product_by_id(collection,product_id):
    product = collection.find_one({'_id':ObjectId(product_id)})
    product_data = {
            'product_id': str(product['_id']),
            'title': product['title'],
            'description': product['description'],
            'price': product['price'],
            'image': product['image'],
            'category' : product['category']
        }
    return jsonify(product_data)

def get_products_by_category(collection,category):
    if category == 'all':
        result = list(collection.find())
    else:
        result = list(collection.find({'category': category}))
    product_list = []
    for product in result:
        product_data = {
            'product_id': str(product['_id']),
            'title': product['title'],
            'description': product['description'],
            'price': product['price'],
            'image': product['image'],
            'category' : product['category']
        }
        product_list.append(product_data)
    return jsonify(product_list)



def add_product_to_user_cart(collection,product_id,user_id):
    item = {
        'product_id':ObjectId(product_id),
        'user_id':user_id,
    }
    try:
        result = collection.insert_one(item)
        return True
    except:
        return False

def get_product_count_in_cart(collection,user_id,product_id):
    count = len(list(collection.find({'user_id':user_id,'product_id':ObjectId(product_id)})))
    return count

def get_cart_count(collection,user_id):
    count = len(list(collection.find({'user_id':user_id})))
    return count

def get_all_products_in_cart(collection1,collection2,user_id):
    products = list(collection1.find({'user_id':user_id}))
    product_list = []
    unique_items = []
    total_count = 0
    total_price = 0
    for product_dict in products:
        if product_dict['product_id'] not in unique_items:
            unique_items.append(product_dict['product_id'])
            product = get_product_by_id(collection2,str(product_dict['product_id'])).json
            product_count = len(list(collection1.find({'product_id' : ObjectId(product_dict['product_id'])})))
            total_count += product_count
            total_price += product_count * product['price']
            product_data = {
                'item_id' : str(product_dict['_id']),
                'product_id': str(product['product_id']),
                'title': product['title'],
                'description': product['description'],
                'price': product['price'],
                'image': product['image'],
                'category' : product['category'],
                'count': product_count
        }
            product_list.append(product_data)
    return jsonify(product_list), total_count, total_price

def place_order(collection,address,card_number,expiry_date,cvv,user_id):
    order = {
        'address':address,
        'user_id':user_id,
        'card_number':card_number,
        'expiry date':expiry_date,
        'cvv':cvv
    }
    try:
        result = collection.insert_one(order)
        return True
    except:
        return False


def delete_cart_item(collection,product_id):
    try:
        collection.delete_one({'product_id':ObjectId(product_id)})
        return True
    except:
        return False

def clear_cart(collection,user_id):
    try:
        collection.delete_many({'user_id':user_id})
        return True
    except:
        return False