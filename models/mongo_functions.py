from flask import jsonify
import datetime
from flask_pymongo import ObjectId
import re
from models.sqlite_functions import get_by_id as get_user_by_id



def get_jobs(job_collection,save_collection,user_id):
    jobs = list(job_collection.find())
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
            "longitude": job['longitude'],
            "saved": if_job_saved(save_collection,job['_id'],user_id)
        }
        job_list.append(job_data)
    return jsonify(job_list)


def get_job_by_id(job_collection,job_id,user_id=None,save_collection=None):
    job = job_collection.find_one({'_id':ObjectId(job_id)})
    if job:
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
                "longitude": job['longitude'],
                "saved": if_job_saved(save_collection,job['_id'],user_id) if user_id else None
            }
        return jsonify(job_data)
    else:
        return jsonify({"data":False})

def save_job_to_user(collection,job_id,user_id):
    item = {
        'job_id':ObjectId(job_id),
        'user_id':user_id,
        'date_applied':datetime.datetime.now()
    }
    try:
        result = collection.insert_one(item)
        return jsonify({"data":True})
    except:
        return jsonify({"data":False})
    
def unsave_job_from_user(collection,job_id,user_id):
    try:
        collection.delete_one({'job_id':ObjectId(job_id),'user_id':user_id})
        return jsonify({"data":True})
    except:
        return jsonify({"data":False})
    
def if_job_saved(collection,job_id,user_id):
    count = len(list(collection.find({'job_id':ObjectId(job_id),'user_id':user_id})))
    if count == 0:
        return False
    else:
        return True
    
def get_saved_jobs(job_collection,save_collection,user_id):
    jobs = list(save_collection.find({'user_id':user_id}))
    job_list = []
    for job in jobs:
        job_data = get_job_by_id(job_collection,str(job['job_id']),user_id,save_collection).json
        job_list.append(job_data)
    return jsonify(job_list)

def search_jobs(search_term, job_collection, save_collection, user_id, onlySaved=False):
    regex_pattern = re.compile(f".*{search_term}.*", re.IGNORECASE)

    job_filter = {
        "$or": [
            {"company_name": {"$regex": regex_pattern}},
            {"job_name": {"$regex": regex_pattern}},
            {"job_desc": {"$regex": regex_pattern}},
            {"duration": {"$regex": regex_pattern}},
            {"location": {"$regex": regex_pattern}},
        ]
    }

    jobs = list(job_collection.find(job_filter))

    job_list = []
    
    for job in jobs:
        if not onlySaved or if_job_saved(save_collection, str(job['_id']), user_id):
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
                "longitude": job['longitude'],
                "saved": if_job_saved(save_collection, str(job['_id']), user_id)
            }
            job_list.append(job_data)

    return jsonify(job_list)


def create_application(collection,job_collection,save_collection, job_id, user_id, application):
    item = {
        'job_id':ObjectId(job_id),
        'job_details': get_job_by_id(job_collection, job_id, user_id, save_collection).json,
        'user_id':user_id,
        'application_details':application,
        'status':'Pending Review',
        'date_applied':datetime.datetime.now()
    }
    try:
        result = collection.insert_one(item)
        return jsonify({"data":True})
    except:
        return jsonify({"data":False})
    
# User / Admin
def get_applications(collection,job_collection,save_collection, user_id):
    if user_id == 'admin':
        applications = list(collection.find())
    else:
        applications = list(collection.find({'user_id':user_id}))
    application_list = []
    for application in applications:
        application_data = {
            'job_id': str(application['job_id']),
            'application_id': str(application['_id']),
            'user_id': str(application['user_id']),
            'user_info': get_user_by_id(application['user_id']),
            'application_details': application['application_details'],
            'status': application['status'],
            'date_applied': application['date_applied'],
            'job_details': application['job_details']
        }
        application_list.append(application_data)
    return jsonify(application_list)

def get_application_by_id(collection,application_id):
    application = collection.find_one({'_id':ObjectId(application_id)})
    if application:
        application_data = {
            'job_id': str(application['job_id']),
            'application_id': str(application['_id']),
            'user_id': str(application['user_id']),
            'user_info': get_user_by_id(application['user_id']),
            'application_details': application['application_details'],
            'status': application['status'],
            'date_applied': application['date_applied'],
            'job_details': application['job_details']
        }
        return jsonify(application_data)
    else:
        return jsonify({"data":False})

def delete_user_application(application_collection,application_id,isAdmin=False):
    if isAdmin:
        try:
            application = application_collection.find_one({'_id':ObjectId(application_id)})
            print(application)
            application_collection.update_many({'_id': ObjectId(application_id)}, {'$set': {'status': 'Rejected'}})
            return jsonify({"data":True})
        except:
            return jsonify({"data":False})
    else:
        try:
            application_collection.delete_one({'_id':ObjectId(application_id)})
            return jsonify({"data":True})
        except:
            return jsonify({"data":False})

# Admin

def delete_job(collection, save_collection, application_collection, job_id):
    try:
        application_collection.update_many({'job_id': ObjectId(job_id)}, {'$set': {'status': 'Job Deleted'}})
        save_collection.delete_many({'job_id': ObjectId(job_id)})
        collection.delete_one({'_id': ObjectId(job_id)})
        return jsonify({"data": True})
    except:
        return jsonify({"data": False})


# Admin