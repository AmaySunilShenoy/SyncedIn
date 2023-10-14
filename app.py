from flask import Flask, url_for, redirect, render_template, g, request,session, jsonify, flash
from flask_caching import Cache
import sqlite3
import os
from flask_pymongo import PyMongo, ObjectId
import datetime
from models.wtforms_class import SignUpForm, LogInForm, PaymentForm
from models.mongo_functions import get_jobs
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
app.config['PRODUCT_PICS'] = os.path.join(app.root_path,'static','images','product_images')
db = PyMongo(app).db
job_collection = db.job_listing

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


logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')
print('Log available in app.log')
@app.before_request
def log_request_info():
    logging.info('Request Method : %s', request.method)
    logging.info('Request url : %s', request.url)
    logging.info('Request Headers : %s', dict(request.headers))
    logging.info('Request Data : %s', request.data)

@app.after_request
def log_response_info(response):
    logging.info('Response Status: %s', response.status)
    logging.info('Request Headers : %s', dict(request.headers))
    return response


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
                return redirect('/home')
            else:
                flash('Your credentials are incorrect!', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST','GET'])
def logout():
    logout_user()
    return redirect('/login')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if session.get('isAuthenticated') == True:
        return redirect('/home')
    usernames = existing_data('username')
    emails = existing_data('email')

    form = SignUpForm(existing_usernames=usernames,existing_emails=emails)

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        profile_picture = form.profile_picture.data
        if profile_picture:
            profile_picture_name = secure_filename(profile_picture.filename)
            profile_path = os.path.join(app.config['PROFILE_PICS'],profile_picture_name)
            profile_picture.save(profile_path)
            profile_relative_path = os.path.join('profile_pictures',profile_picture.filename)
        else:
            profile_relative_path = 'profile_pictures/default-profile-pic.jpg'
        add_user(username, email, password,profile_relative_path)

        flash('Your account has been created successfully!', 'success')
        session.set('isAuthenticated',True)
        return redirect('/login')
    return render_template("signup.html", form=form)

@app.route('/home', methods=['POST','GET'])
@login_required
async def home():
    jobs = get_jobs(job_collection).json
    return render_template('home.html', user=current_user, jobs = jobs)

@app.route('/products/<category>', methods=['POST','GET'])
@login_required
def category(category):
    cart_count = get_cart_count(cart,current_user.id)
    if category not in ['pet','fashion','smartphones','furniture','all']:
        return render_template('category.html',user=current_user,category=category,cart_count=cart_count,isValid=False)
    else:
        if cache.get(f'{category}'):
            product_list = cache.get(f'{category}')
        else:
            product_list = get_products_by_category(products,category).json
            cache.set(f'{category}',product_list)
        return render_template('category.html',user=current_user,product_list=product_list,category=category,cart_count=cart_count,isValid=True)


@app.route('/product/<product_id>', methods=['POST','GET'])
@login_required
def product(product_id):
    cart_count = get_cart_count(cart,current_user.id)
    product_count_in_cart = get_product_count_in_cart(cart,current_user.id,product_id)
    if cache.get(f'{product_id}'):
        product = cache.get(f'{product_id}')
        return render_template('product.html', user=current_user,product=product, cart_count=cart_count,product_count_in_cart=product_count_in_cart)
    else:
        product = get_product_by_id(products,product_id).json
        cache.set(f'{product_id}', product)
        return render_template('product.html', user=current_user,product=product, cart_count=cart_count,product_count_in_cart=product_count_in_cart)

@app.route('/cart', methods=['POST','GET'])
@login_required
def cart_page():
    paymentform = PaymentForm()
    if request.method == 'POST':
        if paymentform.validate_on_submit():
            address = paymentform.address.data
            card_number = paymentform.card_number.data
            expiry_date = paymentform.expiry_date.data
            cvv = paymentform.cvv.data
            place_order(orders,address,card_number,expiry_date,cvv,current_user.id)
            print(clear_cart(cart, current_user.id))
            flash('Your order has been placed!', 'success')
        else:
            print('not validate')

    cart_count = get_cart_count(cart,current_user.id)
    products_in_cart, total_count, total_price = get_all_products_in_cart(cart,products,current_user.id)
    return render_template('cart.html',user=current_user,cart_products=products_in_cart.json,cart_count=cart_count,total_count=total_count,total_price=total_price,paymentform=paymentform)


@app.route('/addtocart', methods=['POST'])
@login_required
def addtocart():
    product_id = request.form['product_id']
    try:
        add_product_to_user_cart(cart,product_id,current_user.id)
        if request.referrer:
            flash('Item Added to Cart Successfully', 'success')
            return redirect(request.referrer)
        else:
            flash('Item Added to Cart Successfully', 'success')
            return redirect('/home')
    except:
        print('adding to cart failed')

@app.route('/removefromcart',methods=['POST'])
@login_required
def removefromcart():
    product_id = request.form['product_id']
    try:
        print(delete_cart_item(cart,product_id))
        if request.referrer:
            flash('Item Deleted from Cart', 'danger')
            return redirect(request.referrer)
        else:
            flash('Item Deleted from Cart','danger')
            return redirect('/home')
    except:
        print('deleting from cart failed')

@app.route('/clearcart',methods=['GET','POST'])
@login_required
def clearcart():
    try:
        clear_cart(cart, current_user.id)
        if request.referrer:
            flash('Cart Cleared', 'danger')
            return redirect(request.referrer)
        else:
            flash('Cart Cleared','danger')
            return redirect('/home')
    except:
        print('clear cart failed')

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True,port=2000)
