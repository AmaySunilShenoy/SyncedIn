from flask import Flask, url_for, redirect, render_template, g, request,session, jsonify, flash
from flask_caching import Cache
from random import randint
import os
import sqlite3
from flask_pymongo import PyMongo, ObjectId
import datetime
from models.wtforms_class import SignUpForm, LogInForm, ApplicationForm
from models.mongo_functions import get_jobs, get_job_by_id, save_job_to_user, unsave_job_from_user, get_saved_jobs, search_jobs, create_application, get_applications, delete_job, delete_user_application, get_application_by_id
from models.sqlite_functions import auth, add_user, existing_data, get_by_id

from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from werkzeug.utils import secure_filename
import logging


from models.user_class import User
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
app = Flask(__name__)
cache.init_app(app)
app.secret_key = '12231232213'



#================================================================ MONGO DB ================================================================
app.config["MONGO_URI"] = "mongodb://localhost:27017/jobs"
app.config['PROFILE_PICS'] = os.path.join(app.root_path,'static','images','profile_pictures')
app.config['CV'] = os.path.join(app.root_path,'static','images','cv')
app.config['DATABASE'] = os.path.join(app.root_path,'users.db')
db = PyMongo(app).db
job_collection = db.job_listing
save_collection = db.saved_jobs
application_collection = db.applications



cart_count = 0
# ================================================================================================================================================================================================================================================================
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user = get_by_id(user_id)
    if user:
        return User(*user)
    else:
        pass

# ================================================================ Flask Routes ================================================================
cache=Cache(app,config={'CACHE_TYPE': 'simple'})


# logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')
# print('Log available in app.log')
# @app.before_request
# def log_request_info():
#     logging.info('Request Method : %s', request.method)
#     logging.info('Request url : %s', request.url)
#     logging.info('Request Headers : %s', dict(request.headers))
#     logging.info('Request Data : %s', request.data)

# @app.after_request
# def log_response_info(response):
#     logging.info('Response Status: %s', response.status)
#     logging.info('Request Headers : %s', dict(request.headers))
#     return response

@app.route('/')
def welcome():
    if session.get('isAuthenticated') == True:
        return redirect('/home')
    return render_template('welcome.html')

@app.route('/login', methods=["POST", "GET"])
def login():
    if session.get('isAuthenticated') == True:
        return redirect('/home')
    form = LogInForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user = auth(username, password)
            if user:
                user_obj = load_user(user[0])
                login_user(user_obj)
                
                session['isAuthenticated'] =True
                if user[1] == 1:
                    session['isAdmin'] = True
                    return redirect('/jobs')
                return redirect('/home')
            else:
                flash('Your credentials are incorrect!', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST','GET'])
def logout():
    logout_user()
    session['isAuthenticated'] = False
    session['isAdmin'] = False
    return redirect('/login')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if session.get('isAuthenticated') == True:
        return redirect('/home')
    usernames = existing_data('username')
    emails = existing_data('email')

    form = SignUpForm(existing_usernames=usernames,existing_emails=emails)

    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        profile_picture = form.profile_picture.data
        is_admin = 0
        if profile_picture:
            profile_picture_name = secure_filename(profile_picture.filename)
            profile_path = os.path.join(app.config['PROFILE_PICS'],profile_picture_name)
            profile_picture.save(profile_path)
            profile_relative_path = os.path.join('profile_pictures',profile_picture.filename)
        else:
            profile_relative_path = 'profile_pictures/default-profile-pic.jpg'
        userid = add_user(firstname,lastname,username, email, password,profile_relative_path,is_admin)
        if userid:
            user_obj = load_user(userid[0])
            login_user(user_obj)
            flash('Your account has been created successfully!', 'success')
            session['isAuthenticated'] = True
            return redirect('/home')
        else:
            return redirect('/signup')
    return render_template("signup.html", form=form)



@app.route('/home', methods=['POST','GET'])
@login_required
async def home():
    if session.get('isAdmin') == True:
        return redirect('/jobs')
    application_form = ApplicationForm()
    all_jobs = get_jobs(job_collection,save_collection,current_user.id).json
    jobs = []
    for _ in range(0,10):
        jobs.append(all_jobs[randint(0, len(all_jobs)-1)])  
    return render_template('home.html', user=current_user, jobs = jobs, form=application_form)

@app.route('/saved', methods=['POST','GET'])
@login_required
async def saved():
    if session.get('isAdmin') == True:
        return redirect('/jobs')
    form = ApplicationForm()

    if session.get('jobs'):
        jobs = session['jobs']
        session.pop('jobs',None)
    else:
        jobs = get_saved_jobs(job_collection,save_collection,current_user.id).json

    return render_template('saved.html', user=current_user, jobs = jobs,form=form)

@app.route('/jobs', methods=['POST','GET'])
@login_required
async def jobs():
    form = ApplicationForm()
    jobs = get_jobs(job_collection,save_collection,current_user.id).json
    return render_template('job.html', user=current_user, jobs = jobs, search=False,form=form)

@app.route('/applications', methods=['POST','GET'])
@login_required
async def applications():
    form = ApplicationForm()
    if session.get('isAdmin') == True:
        applications = get_applications(application_collection,job_collection,save_collection,'admin').json

    else:
        applications = get_applications(application_collection,job_collection,save_collection,current_user.id).json
    return render_template('applications.html', user=current_user, applications = applications,form=form)

@app.route('/job/<job_id>', methods=['POST','GET'])
@login_required
async def job(job_id):
    job = get_job_by_id(job_collection,job_id).json
    return job

@app.route('/application/<application_id>', methods=['POST','GET'])
@login_required
async def application(application_id):
    application = get_application_by_id(application_collection,application_id).json
    return application

@app.route('/save/<job_id>', methods=['POST','GET'])
@login_required
async def savejob(job_id):
    flash('Job Saved Successfully', 'success')
    return save_job_to_user(save_collection,job_id,current_user.id)

@app.route('/unsave/<job_id>', methods=['POST','GET'])
@login_required
async def unsavejob(job_id):
    return unsave_job_from_user(save_collection,job_id,current_user.id)

@app.route('/search', methods=['POST','GET'])
@login_required
async def search():

    form = ApplicationForm()

    search_term = request.form['search_term']
    if request.referrer == 'http://127.0.0.1:2000/saved':
        jobs = search_jobs(search_term,job_collection,save_collection,current_user.id,onlySaved=True).json
        session['jobs'] = jobs
        return redirect('/saved')
    else:
        jobs = search_jobs(search_term,job_collection,save_collection,current_user.id).json
        return render_template('job.html', user=current_user, jobs = jobs,search=search_term,form=form)

@app.route('/apply/<job_id>', methods=['POST','GET'])
@login_required
async def apply(job_id):
    form = ApplicationForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        print(firstname)
        lastname = form.lastname.data
        email = form.email.data
        phone = form.phone.data
        address = form.address.data
        cv = form.cv.data
        comments = form.comments.data
        if cv:
            cv_name = secure_filename(cv.filename)
            cv_path = os.path.join(app.config['CV'],cv_name)
            cv.save(cv_path)
            cv_relative_path = os.path.join('cv',cv.filename)
        else:
            cv_relative_path = None
        application_details = {'firstname': firstname, 'lastname': lastname, 'email': email, 'phone': phone, 'address': address, 'cv_relative_path': cv_relative_path, 'comments': comments}
        create_application(application_collection,job_collection,save_collection,job_id,current_user.id,application_details)
        flash('Your application has been submitted successfully!', 'success')
        return redirect('/home')
    else:
        flash('Your application has not been submitted successfully!', 'danger')
        print('no')
        return redirect('/home')

@app.route('/delete/<job_id>', methods=['POST','GET'])
@login_required
async def delete(job_id):
    if session.get('isAdmin'):
        return delete_job(job_collection,save_collection,application_collection,job_id)
    else:
        return redirect('/home')

@app.route('/delete_application/<application_id>', methods=['POST','GET'])
@login_required
async def delete_application(application_id):
    if session.get('isAdmin'):
        print('in delete admin')
        return delete_user_application(application_collection,application_id,isAdmin=True)
    print('in delete regular')
    return delete_user_application(application_collection,application_id)

@app.route('/user/<user_id>', methods=['POST','GET'])
@login_required
async def user(user_id):
    if session.get('isAdmin'):
        user_info = get_by_id(user_id)
        return user_info
    else:
        return redirect('/home')


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True,port=2000)
