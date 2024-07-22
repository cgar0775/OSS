#imports
from flask import Flask, render_template, request, redirect, url_for, flash, session
import oracledb
from database import OracleConfig
from dotenv import load_dotenv
import oracledb
from database import OracleConfig
from dotenv import load_dotenv

from dbfunc import CreateCustomerAcc,CreateBusinessAcc, loginCheck, CallBusinessInfo, CheckBusinessName, CheckUsername, CallCustomerInfo, CreateService, GetBusinessServices,CreateEmployee,UpdateAvailability
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
        
        #validate login with the db
        if not loginCheck(username,password):
            flash("Login Invalid, please try again")
            return redirect(url_for('login'))
        
        #add logic for to select for customer or business

        # Set session variable for logged-in user
        #--indicates that the user is logged in--#
        session['logged_in'] = True

        #--stores the logged-in username--#
        session['username'] = username
        
        
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

         if CheckBusinessName(businessname):
             errors.append("Invalid Business Name: Business already exists")
            
         if CheckUsername(username):
             errors.append("Invalid Username: User already exists")

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
        
         if CheckUsername(username):
             errors.append("Invalid Username: User already exists")

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
    #Check if the login cache works
    username = session.get('username')
    # print(username)
    username = "otest"
    CustomerInfo = CallCustomerInfo(username)
    print(CustomerInfo)
    # name = "Olivia"
    #BusinessInfo = CallBusinessInfo(username)
    #name = BusinessInfo[0]
    name = CustomerInfo[1]
    return render_template('home.html', name = name)

@app.route('/search')
def searchPage():

    return render_template('templates/search.html')

@app.route('/profile')
def profilePage():

    return render_template('Components/profile.html')

@app.route('/bookings')
def bookingPage():

    
    # return render_template('templates/Bbookings.html')
    return render_template('templates/bookings.html')

@app.route('/employees')
def employeePage():




    return render_template('templates/bEmployees.html')


@app.route('/business/view')
def redirectToHome():
    return redirect('/home')

@app.route('/business/view/<username>',  methods = ['GET','POST'])
def businessViewProfilePage(username):

    # General Business Information
    businessInfo = CallBusinessInfo(username)
    
    businessName = businessInfo[0]
    businessAddress = businessInfo[3] + ", " + businessInfo[2]

    stars = "4"

    # Get array for services

    # Time Table

    # Map

    # Reviews

    return render_template('templates/bProfile.html', businessName = businessName, businessAddress=businessAddress, stars=stars, title='View Buisness')


@app.route('/business/edit')
def businessEditProfilePage():


    return render_template('templates/bEdit.html', 
            title="Edit Profile")

@app.route('/profile/view')
def customerViewProfilePage():

    customerName = "Olivia Bisset"
    customerAddress = "11351 W. Broward Blvd"

    return render_template('templates/cProfile.html', customerName=customerName, customerAddress=customerAddress)


@app.route('/profile/edit')
def customerEditProfilePage(): 

    # return render_template('templates/cEdit.html')
    return render_template('templates/bEdit.html')

@app.route('/services')
def servicePage():

    print(GetBusinessServices("Pozie Jewelry"))
    print(len(GetBusinessServices("Pozie Jewelry")))

    return render_template('templates/servicePage.html', service=GetBusinessServices("Pozie Jewelry"))

@app.route('/add-service', methods = ['GET','POST'])
def addService():

    if request.method == "POST":
       print("Hello there")

    return render_template('templates/addService.html')

@app.route('/submit-form', methods=['POST', 'GET'])
def addServiceFunction():
    print(request.form)
    name = request.form.get('name')
    price = request.form.get('price')
    slots = request.form.get('slots')
    bName = "Pozie Jewelry" #for test

    print(name + " " + price+ " " + bName + " " + slots)

    
    CreateService(bName, name, price, slots)


    return redirect(url_for('servicePage'))

@app.route('/update-form', methods=['POST', 'GET'])
def updateTime():

    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    breakStart = request.form.get("break-start")
    breakEnd = request.form.get("break-end")

    for i in days:
        startLabel = i + '-start'    
        endLabel = i + '-end'    
        
        print(request.form.get(startLabel))
        print(request.form.get(endLabel))

        # UpdateAvailability('Pozie Jewelry', 'thingy4', i, startLabel, endLabel, breakStart, breakEnd)

    return redirect(url_for('servicePage'))

@app.route('/<businessname>/service/<serviceName>')

# @app.route('/service')
def singleServicePage(businessname, serviceName):
    # print(Get)
    return render_template("templates/sView.html", businessName=businessname, serviceName=serviceName)

@app.route('/<businessname>/service/edit/<serviceName>')
def singleServiceEditPage(businessname, serviceName):


    return render_template("templates/sEdit.html")

@app.route('/employee/add')
def addEmployee():

    if request.method == 'POST':

        eusername = request.form['username']
        password = request.form['password']
        efname = request.form['firstname']
        elname = request.form['lastname']
        role = request.form['checkbox']

        errors = []
         
        #Validate Input, Error Messages will flash to CSignUp
        is_valid_username, username_error = inputvalidation.validate_username(eusername)
        is_valid_password, password_error = inputvalidation.validate_password(password)
        is_valid_name, name_error = inputvalidation.validate_name(efname, elname)

        if CheckUsername(eusername):
            errors.append("Invalid Username: User already exists")

        if not is_valid_username:
             errors.append(username_error)

        if not is_valid_password:
            errors.append(password_error)

        if not is_valid_name:
            errors.extend(name_error)

        if errors:
            for error in errors:
                flash(error)
            return redirect(url_for('bAddEmployee'))

        efname = efname.capitalize()
        elname = elname.capitalize()

        #invoke database to get business name based on current logged in user session because only buiness admins can make employee acc.
        BusinessInfo = CallBusinessInfo(session.get('username'))
        bname = BusinessInfo[0]

        CreateEmployee(bname,eusername,password,efname,elname,role)

    return render_template("templates/bAddEmployee.html")

# Add service page code here
# @app.route()

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    session.pop('username',None)
    flash('You have been logged out.')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)