#imports
import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
import oracledb
import requests
from database import OracleConfig
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session, g
import oracledb
# import requests
from database import OracleConfig
from dotenv import load_dotenv
import dbfunc

from dbfunc import CreateCustomerAcc,CreateBusinessAcc, loginCheck, CallBusinessInfo, CheckBusinessName, CheckUsername, CallCustomerInfo, CreateService, GetBusinessServices, UpdateAvailability, CallBusinessName, CheckRole

import inputvalidation
from flask_session import Session
import redis

app = Flask(__name__)
app.secret_key = 'your_secret_key'

#loading the env file
load_dotenv()

#global variable setup
database= OracleConfig()

#Google Maps API_KEY
API_KEY= os.getenv('API_KEY')

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


# run.py General Functions 

@app.before_request
def before_request():
    username = session.get('username')
    if username:
        
        g.role = CheckRole(username)[0]
        if g.role == "Business":
            g.data = CallBusinessInfo(CallBusinessName(username)[0])
            # print("g.data: ")
            # print(g.data)
        elif g.role == "Customer":
            g.data = CallCustomerInfo(username)

@app.route("/")
def hello_world():
    # See if they are logged in and then redirect them
    return render_template('splash.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':

        #handling login logic
        username = request.form['username']
        password = request.form['password']
        
        #validate login with the db
        if not dbfunc.loginCheck(username,password):
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
            

         # if dbfunc.CheckUsername(username):
        #  if CheckUsername(username):
         
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

         dbfunc.CreateBusinessAcc(username,password,businessname,country,state,city,address,email)
         
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
        
         if dbfunc.CheckUsername(username):
                errors.append("Invalid Username: User already exists")
                
        #  if CheckUsername(username):

         if errors:
            for error in errors:
                flash(error)
            return redirect(url_for('Csignup'))
        
        
         firstname = firstname.capitalize()
         lastname = lastname.capitalize()
         country = country.capitalize()
         state = state.capitalize()
         city = city.capitalize()

         dbfunc.CreateCustomerAcc(username,password,firstname,lastname,country,state,city,address,email)

        #Return customer to login page after sucessful account creation
         return redirect(url_for('login'))
             
    return render_template('Csignup.html')

@app.route('/home')
def homePage():
    # Get user information
    username = session.get('username')
    print(username)
    # username = "otest"
    #CustomerInfo = dbfunc.CallCustomerInfo(username)
    #print(CustomerInfo)
    # name = "Olivia"
    #BusinessInfo = CallBusinessInfo(username)
    #name = BusinessInfo[0]
    #name = CustomerInfo[1]
    #CustomerInfo = dbfunc.CallCustomerInfo(username)
    #name = CustomerInfo[1]
    #BusinessInfo = dbfunc.CallBusinessInfo(username)
    #name = BusinessInfo[0]
    #print(name)
    #return render_template('home.html', name = name)

    # If they are not logged in, redirect them to the login page
    if not username: 
        print("Empty Username!")
        return redirect(url_for('login'))
    
    # if they are logged in, what type of account???
    

    if CallBusinessName(username):
    # if CallBusinessInfo(CallBusinessName(username)[0]):
        
        BuisnessInfo = CallBusinessInfo(CallBusinessName(username)[0])

        
        
        
        return render_template('bHome.html', name = "name") #Change this to the buisness home page!!!
        

    if CheckRole(username)[0] == 'Customer':
        # print("Username: " + str(username))
        CustomerInfo = CallCustomerInfo(username)
        # print(CustomerInfo)
        name = CustomerInfo[1]
        return render_template('home.html', name = name)

    # Check to see if it is an employee
    
    
    # return render_template('home.html', name = "name")
    return render_template('home.html')

@app.route('/search')
def searchPage():
    # Get user information
    username = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not username: 
        print("Empty Username!")
        return redirect(url_for('login'))

    return render_template('templates/search.html')

@app.route('/profile')
def profilePage():
    # Get user information
    username = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not username: 
        print("Empty Username!")
        return redirect(url_for('login'))

    return render_template('templates/cEdit.html')

@app.route('/bookings')
def bookingPage():

    # Get user information
    username = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not username: 
        print("Empty Username!")
        return redirect(url_for('login'))

    # return render_template('templates/Bbookings.html')
    return render_template('templates/bookings.html')

@app.route('/employees')
def employeePage():
    # Get user information
    username = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not username: 
        print("Empty Username!")
        return redirect(url_for('login'))
    
    BusinessInfo = CallBusinessName(username)
    bname = BusinessInfo[0]
    
    employees = dbfunc.CallBusinessEmployees(bname)

    return render_template('templates/bEmployees.html', employees = employees)


# Redirect to the current logged in buisness view page
@app.route('/business/view')
def redirectToHome():
    redir = '/business/view/' + CallBusinessName(session.get('username'))[0]
    return redirect(redir)

@app.route('/business/view/<username>',  methods = ['GET','POST'])
def businessViewProfilePage(username):

    # Get user information
    currentUsername = session.get('username')
    print(currentUsername)

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect(url_for('login'))

    # debuig this - there might be an error!!!

    # General Business Information
    businessInfo = dbfunc.CallBusinessInfo(username)
    print(CallBusinessName(username))
    businessInfo = CallBusinessInfo(username)
    # businessInfo = CallBusinessInfo(CallBusinessName(username)[0])
    # print(businessInfo)
    
    businessName = businessInfo[0]
    businessAddress = businessInfo[3] + ", " + businessInfo[2]
    businessUsername = businessInfo[6]

    stars = "4"

    # Get array for services

    arrServices = GetBusinessServices(businessName)
    print("arrServices")
    print(arrServices)

    # Time Table

    # Map

    # Reviews

    return render_template('templates/bProfile.html', businessName = businessName, businessAddress=businessAddress, stars=stars, title='View Buisness', businessUsername=businessUsername, arrServices=arrServices)


@app.route('/business/edit')
def businessEditProfilePage():
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect(url_for('login'))

    return render_template('templates/bEdit.html', 
            title="Edit Profile")

@app.route('/profile/view')
def customerViewProfilePage():
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect(url_for('login'))

    customerName = "Olivia Bisset"
    customerAddress = "11351 W. Broward Blvd"

    return render_template('templates/cProfile.html', customerName=customerName, customerAddress=customerAddress)


@app.route('/profile/edit')
def customerEditProfilePage(): 
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect(url_for('login'))

    # return render_template('templates/cEdit.html')
    return render_template('templates/bEdit.html')

@app.route('/services')
def servicePage():
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect(url_for('login'))

    print(CallBusinessName(currentUsername))
    # print(CallBusinessInfo(CallBusinessName(currentUsername)))

    return render_template('templates/servicePage.html', service=GetBusinessServices(CallBusinessName(currentUsername)[0]))

@app.route('/add-service', methods = ['GET','POST'])
def addService():
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect(url_for('login'))

    if request.method == "POST":
       print("Hello there")

    return render_template('templates/addService.html')

def checkLogin():
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect('/login')

@app.route('/submit-form', methods=['POST', 'GET'])
def addServiceFunction():
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect('/login')
    print(request.form)
    name = request.form.get('name')
    price = request.form.get('price')
    slots = request.form.get('slots')
    bName = CallBusinessName(currentUsername)[0]

    # print(name + " " + price + " " + bName + " " + slots)

    # Create the swervice with both the given and known information
    CreateService(bName, name, price, slots)


    return redirect(url_for('servicePage'))

@app.route('/update-form', methods=['POST', 'GET'])
def updateTime():
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect('/login')

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
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect('/login')

    # Get avalible service times 

    # print(Get)
    return render_template("templates/sView.html", businessName=businessname, serviceName=serviceName)

@app.route('/<businessname>/service/edit/<serviceName>')
def singleServiceEditPage(businessname, serviceName):
# Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect('/login')

    return render_template("templates/sEdit.html")

@app.route('/employee/add', methods = ['GET','POST'])
def addEmployee():
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect('/login')

    if request.method == 'POST':

        eusername = request.form['username']
        password = request.form['password']
        efname = request.form['firstname']
        elname = request.form['lastname']
        role = request.form.get('role')

        #the following below allows for role to checked or unchecked without yeilding a badRequestError 
        #role_checked = 'role' in request.form
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
            return redirect('/employee/add')

        efname = efname.capitalize()
        elname = elname.capitalize()

        #invoke database to get business name based on current logged in user session because only buiness admins can make employee acc.
        #BusinessInfo = dbfunc.CallBusinessInfo(session.get('username'))
        BusinessInfo = dbfunc.CallBusinessName(currentUsername)
        bname = BusinessInfo[0]

        #Add role based on checked box
        dbfunc.CreateEmployee(bname,eusername,password,efname,elname,role)
        #dbfunc.CreateEmployee(eusername,password,efname,elname,bname,role_checked)

        flash("Employee account created successfully.")
        return redirect('/employee/add')
    
    return render_template("templates/bAddEmployee.html")

# Add service page code here
# @app.route()

#Trial for maps
@app.route('/maps')
def viewMap():
    username = session.get('username')
    CustomerInfo = dbfunc.CallCustomerInfo(username)
    return render_template('maps.html', api_key = API_KEY)

#Geocoding Location for maps
@app.route('/get-user-location')
def get_user_location():
    username = session.get('username')
    customer_info = dbfunc.CallCustomerInfo(username)
    address = f"{customer_info[6]}, {customer_info[5]}, {customer_info[4]}, {customer_info[3]}" 

    # Print the address for debugging purposes
    # print(f"Address: {address}")
    
    # Use Google Geocoding API to convert address to coordinates
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}"
    response = requests.get(geocode_url)
    geocode_data = response.json()

    if geocode_data['status'] == 'OK':
        location = geocode_data['results'][0]['geometry']['location']
        user_lat = location['lat']
        user_lng = location['lng']
        # This is not working
        dbfunc.AddCoordinates(username, user_lat, user_lng)
        
        return jsonify({'lat': user_lat, 'lng': user_lng})
    else:
        return jsonify({'error': 'Unable to geocode address'})
    
#Need a function to grab all businesses in the area??
@app.route('/get-nearby-businesses')
def get_nearby_businesses():
    username = session.get('username')
    user_coords = dbfunc.CheckCoordinates(username)

    if not user_coords:
        return jsonify({'error': 'User coordinates not found'})

    user_lat, user_lng = user_coords
    nearby_businesses = dbfunc.CallBusinessGeo(username)

    if not nearby_businesses:
        return jsonify([])

    return jsonify(nearby_businesses)


@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    session.pop('username',None)
    flash('You have been logged out.')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)