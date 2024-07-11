#imports
from flask import Flask, render_template, request, redirect, url_for, flash, session
import oracledb
from database import OracleConfig
from dotenv import load_dotenv
import oracledb
from database import OracleConfig
from dotenv import load_dotenv
from dbfunc import CreateCustomerAcc,CreateBusinessAcc, loginCheck
import inputvalidation
from flask_session import Session
import redis

app = Flask(__name__)
app.secret_key = 'your_secret_key'

#loading the env file
load_dotenv()

#global variable setup
database= OracleConfig()

# Configure server-side session storage

#--Specifies the session type... here it is redis--#
app.config['SESSION_TYPE'] = 'redis'

#--False if the session should be non-permanent--#
app.config['SESSION_PERMANENT'] = False

#--Adds an extra layer of security by signing the session cookies--#
app.config['SESSION_USE_SIGNER'] = True

#--Prefix for session keys in the storage backend--#
app.config['SESSION_KEY_PREFIX'] = 'session:'

#--Configures Redis as the storage backend--#
app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0)

#initializes the session management in flask application
Session(app)

#With this configuration, user sessions are stored in Redis, 
#which ensures that the session persists across different requests
#and even server restarts, retaining the user login state


@app.route("/")
def hello_world():
    return render_template('splash.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':

        #handling login logic
        username = request.form['username']
        password = request.form['password']
        
        #The code below is unncessary... we need to validate user names against database
        # Validate input
        is_valid_username, username_error = inputvalidation.validate_username(username)
        is_valid_password, password_error = inputvalidation.validate_password(password)

        # we need to create a function called loginCheck to compare against DB

        #We will have to reconfigure lines 69-84
        #[error, error, error... etc] = errors
        errors = []

        if not is_valid_username:
            errors.append(username_error)

        if not is_valid_password:
            errors.append(password_error)

        #validate login with the db
        if not loginCheck(username,password):
            errors.append("Login Invalid, please try again")

        if errors:
            for error in errors:
                flash(error)
            return redirect(url_for('login'))

        # Set session variable for logged-in user

        #--indicates that the user is logged in--#
        session['logged_in'] = True

        #--stores the logged-in username--#
        session['username'] = username
        
       # if not is_valid_username:
            #flash(username_error)
           # return redirect(url_for('login'))
        
        #if not is_valid_password:
            #flash(password_error)
           # return redirect(url_for('login'))
        
        #print("hi there")
        #Redirects to home page if login is successful
        
        return redirect(url_for('homePage'))
        #return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/Bsignup', methods = ['GET','POST'])
def Bsignup():
    if request.method == 'POST':
         username = request.form['username']
         password = request.form['password']
         businessname = request.form['business name']
         firstname = request.form['firstname']
         lastname = request.form['lastname']
         country = request.form['country']
         state = request.form['state']
         city = request.form['city']
         address = request.form['address']
         email = request.form['email']

         errors = []
        
         #Validate Input, Error Messages will flash to CSignUp
         is_valid_username, username_error = inputvalidation.validate_username(username)
         is_valid_password, password_error = inputvalidation.validate_password(password)
         is_valid_businessname, businessname_error = inputvalidation.validate_businessname(businessname)
         is_valid_name, name_error = inputvalidation.validate_name(firstname, lastname)
         is_valid_location, location_error = inputvalidation.validate_location(country, state, city)
         is_valid_address, address_error = inputvalidation.validate_address(address)


         if not is_valid_username:
            errors.append(username_error)

         if not is_valid_password:
            errors.append(password_error)

         if not is_valid_businessname:
             errors.append(businessname_error)

         if not is_valid_name:
           errors.extend(name_error)
            
         if not is_valid_location:
             errors.extend(location_error)

         if not is_valid_address:
            errors.append(address_error)

        #Flash errors... retain users in sign up screen
         if errors:
            for error in errors:
                flash(error)
            return redirect(url_for('Bsignup'))

         country = country.capitalize()
         state = state.capitalize()
         city = city.capitalize()

         CreateBusinessAcc(username,password,businessname,country,state,city,address,email)
         
         #Return customer to login page after sucessful account creation
         return redirect(url_for('login'))
         
    return render_template('Bsignup.html')


@app.route('/Csignup', methods = ['GET','POST'])
def Csignup():
    if request.method == 'POST':
         username = request.form['username']
         password = request.form['password']
         firstname = request.form['firstname']
         lastname = request.form['lastname']
         country = request.form['country']
         state = request.form['state']
         city = request.form['city']
         address = request.form['address']
         email = request.form['email']

         #[error, error, error... etc] = errors
         errors = []
         
         #Validate Input, Error Messages will flash to CSignUp
         is_valid_username, username_error = inputvalidation.validate_username(username)
         is_valid_password, password_error = inputvalidation.validate_password(password)
         is_valid_name, name_error = inputvalidation.validate_name(firstname, lastname)
         is_valid_location, location_error = inputvalidation.validate_location(country, state, city)
         is_valid_address, address_error = inputvalidation.validate_address(address)

         if not is_valid_username:
            errors.append(username_error)

         if not is_valid_password:
            errors.append(password_error)

         if not is_valid_name:
            errors.extend(name_error)
            
         if not is_valid_location:
             errors.extend(location_error)

         if not is_valid_address:
            errors.append(address_error)

        #Flash errors... retain users in sign up screen
         if errors:
            for error in errors:
                flash(error)
            return redirect(url_for('Csignup'))
        
        
         firstname = firstname.capitalize()
         lastname = lastname.capitalize()
         country = country.capitalize()
         state = state.capitalize()
         city = city.capitalize()

         CreateCustomerAcc(username,password,firstname,lastname,country,state,city,address,email)

        #Return customer to login page after sucessful account creation
         return redirect(url_for('login'))
             
    return render_template('Csignup.html')

@app.route('/home')
def homePage():
    name = "Olivia"
    return render_template('home.html', name = name)

@app.route('/search')
def searchPage():

    return render_template('search.html')

@app.route('/profile')
def profilePage():

    return render_template('Components/profile.html')

@app.route('/bookings')
def bookingPage():

    return render_template('templates/bookings.html')

@app.route('/business/view')
def businessViewProfilePage():
    
    businessName = "Publix"
    businessAddress = "123 Happy Street"

    stars = "4"


    return render_template('templates/bProfile.html', businessName = businessName, businessAddress=businessAddress, stars=stars, title='View Buisness')


@app.route('/business/edit')
def businessEditProfilePage():


    return render_template('templates/bEdit.html', 
            title="Edit Profile")

@app.route('/profile/view')
def customerViewProfilePage():

    return render_template('templates/cProfile.html')

if __name__ == '__main__':
    app.run(debug=True)