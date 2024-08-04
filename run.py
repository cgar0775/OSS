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

from urllib.parse import urlparse

from datetime import datetime, timedelta, date

from dbfunc import CallEmployeeInfo, CreateCustomerAcc,CreateBusinessAcc, loginCheck, CallBusinessInfo, CheckBusinessName, CheckUsername, CallCustomerInfo, CreateService, GetBusinessServices, UpdateAvailability, CallBusinessName, CheckRole, UpdateDescription, GetHours, getBusinessBookings


import inputvalidation
from flask_session import Session
import redis
import re

import pytz

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

# Timezone Configuration
est = pytz.timezone('America/New_York')  # EST is part of the America/New_York timezone


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
            bname = CallBusinessName(username)[0]
            g.data = CallBusinessInfo(bname)
            # print("g.data: ")
            # print(g.data)
        elif g.role == "Employee":
            g.data = CallEmployeeInfo(username)
        
        elif g.role == "Administrator":
            g.data = CallEmployeeInfo(username)
        
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
         phonenumber = request.form['phone number']
         firstname = request.form['firstname']
         lastname = request.form['lastname']
         country = request.form['country']
         state = request.form['state']
         city = request.form['city']
         address = request.form['address']
         email = request.form['email']
         
            
         errors = []

         #Validate Input, Error Messages will flash to BSignUp
         is_valid_username, username_error = inputvalidation.validate_username(username)
         is_valid_password, password_error = inputvalidation.validate_password(password)
         is_valid_businessname, businessname_error = inputvalidation.validate_businessname(businessname)
         is_valid_phonenumber, phonenumber_error = inputvalidation.validate_phonenum(phonenumber)
         is_valid_name, name_error = inputvalidation.validate_name(firstname, lastname)
         is_valid_location, location_error = inputvalidation.validate_location(country, state, city)
         is_valid_address, address_error = inputvalidation.validate_address(address)

         if not is_valid_username:
            errors.append(username_error)

         if not is_valid_password:
            errors.append(password_error)

         if not is_valid_businessname:
             errors.append(businessname_error)

         if not is_valid_phonenumber:
             errors.append(phonenumber_error)

         if not is_valid_name:
           errors.extend(name_error)
            
         if not is_valid_location:
             errors.extend(location_error)

         if not is_valid_address:
            errors.append(address_error)

         if CheckBusinessName(businessname):
             errors.append("Invalid Business Name: Business already exists")
         
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
         phonenumber = inputvalidation.format_phonenum(phonenumber)
                 
         dbfunc.CreateBusinessAcc(username,password,businessname,country,state,city,address,email,phonenumber)
         full_address = f"{address}, {city}, {state}, {country}"
         # Print the address for debugging purposes
         # print(f"Address: {full_address}")
    
        # Use Google Geocoding API to convert address to coordinates
         geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={full_address}&key={API_KEY}"
         response = requests.get(geocode_url)
         geocode_data = response.json()

         if geocode_data['status'] == 'OK':
            location = geocode_data['results'][0]['geometry']['location']
            user_lat = location['lat']
            user_lng = location['lng']
            
            #if username doesn't exist
            dbfunc.AddCoordinates(username, user_lat, user_lng)
            
         #Return customer to login page after sucessful account creation
         return redirect(url_for('login'))
         
    return render_template('Bsignup.html')


@app.route('/Csignup', methods = ['GET','POST'])
def Csignup():
    if request.method == 'POST':
         username = request.form['username']
         password = request.form['password']
         phonenumber = request.form['phone number']
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
         is_valid_phonenumber, phonenumber_error = inputvalidation.validate_phonenum(phonenumber)
         is_valid_name, name_error = inputvalidation.validate_name(firstname, lastname)
         is_valid_location, location_error = inputvalidation.validate_location(country, state, city)
         is_valid_address, address_error = inputvalidation.validate_address(address)

         if not is_valid_username:
            errors.append(username_error)

         if not is_valid_password:
            errors.append(password_error)
         
         if not is_valid_phonenumber:
             errors.append(phonenumber_error)

         if not is_valid_name:
            errors.extend(name_error)
            
         if not is_valid_location:
             errors.extend(location_error)

         if not is_valid_address:
            errors.append(address_error)
        
         if dbfunc.CheckUsername(username):
                errors.append("Invalid Username: User already exists")
                
         if errors:
            for error in errors:
                flash(error)
            return redirect(url_for('Csignup'))
        
        
         firstname = firstname.capitalize()
         lastname = lastname.capitalize()
         country = country.capitalize()
         state = state.capitalize()
         city = city.capitalize()
         phonenumber = inputvalidation.format_phonenum(phonenumber)


         dbfunc.CreateCustomerAcc(username,password,firstname,lastname,country,state,city,address,email,phonenumber)
         full_address = f"{address}, {city}, {state}, {country}"
         # Print the address for debugging purposes
         # print(f"Address: {full_address}")
    
        # Use Google Geocoding API to convert address to coordinates
         geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={full_address}&key={API_KEY}"
         response = requests.get(geocode_url)
         geocode_data = response.json()

         if geocode_data['status'] == 'OK':
            location = geocode_data['results'][0]['geometry']['location']
            user_lat = location['lat']
            user_lng = location['lng']
            
            #if username doesn't exist
            dbfunc.AddCoordinates(username, user_lat, user_lng)
            
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
        CustomerInfo = CallCustomerInfo(username)
        name = CustomerInfo[1]

        # nearby_business = dbfunc.CallBusinessGeo(username)
        # return render_template('home.html', name = name)

        nearby_businesses = dbfunc.CallBusinessGeo(username)
        businesses = []
        
        for business in nearby_businesses:
            business_name = business[1]
            business_services = GetBusinessServices(business_name)
            services = []
            
            for service in business_services:
                service_name = service[1]  # Extract 'Haircut' from ('Test123', 'Haircut', 300.0, 3, '300:0', 0)
                service_price = service[2]  # Extract the price (300.0)
                services.append({
                    'name': service_name,
                    'price': service_price
                })
            print("service", service)
            businesses.append({
                'username': business[0],
                'name': business_name,
                'services': services,
                'profile_url': url_for('businessViewProfilePage', username=business[0])
            })
            print("nearby", nearby_businesses)
            print("business", businesses)
            
        return render_template('home.html', name=name, nearby_businesses=businesses)

    # Check to see if it is an employee
    
    
    # return render_template('home.html', name = "name")
    return render_template('home.html')

@app.route('/search', methods=['GET', 'POST'])
def searchPage():
    username = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not username:
        return redirect(url_for('login'))

    user_coords = dbfunc.CheckCoordinates(username)
    if not user_coords:
        return render_template('search.html', error="Unable to fetch user location")

    user_lat, user_lng = user_coords

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if not query:
            return render_template('search.html', error="Search query cannot be empty")

        try:
            # Fetch all businesses within a 20-mile radius of the user
            nearby_businesses = dbfunc.CallBusinessGeo(username)
            matching_businesses = []

            for business in nearby_businesses:
                business_username = business[0]
                business_name = business[1]
                services = GetBusinessServices(business_username)

                for service in services:
                    if query.lower() in service[1].lower():  # Case-insensitive search
                        matching_businesses.append({
                            'username': business_username,
                            'business_name': business_name,
                            'service_name': service[1],  # Assuming service[1] is the service name
                            'service_price': service[2]  # Assuming service[2] is the price
                        })

            if not matching_businesses:
                return render_template('templates/search.html', error="No matching services found.")

            return render_template('templates/search.html', businesses=matching_businesses)

        except Exception as e:
            app.logger.error(f"Error fetching businesses for query '{query}': {str(e)}")
            return render_template('templates/search.html', error="Error fetching businesses")

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
    
    print(CheckRole(username)[0])

    # TODO: Make this faster
    # Get all of the bookings for the business
    if CheckRole(username)[0] == 'Business':
        name = CallBusinessName(username)[0]
        allBookings = dbfunc.getBusinessBookings(name)
        bookingData = []

        # print(allBookings)
        for booking in allBookings:
            # print(dbfunc.CallCustomerInfo(booking[2])) 
            customerName = dbfunc.CallCustomerInfo(booking[2])[1] + " " + dbfunc.CallCustomerInfo(booking[2])[2]
            tempData = [booking[0], customerName , str(booking[3])[:10], str(booking[3])[11:], str(booking[4])[11:], dbfunc.CallCustomerInfo(booking[2])[8], dbfunc.CallCustomerInfo(booking[2])[7]]

            bookingData.append(tempData)

        # print (bookingData)
        return render_template("templates/bBookings.html", bookings = bookingData)

    if CheckRole(username)[0] == 'Customer':
        name = username
        allBookings = dbfunc.getUserBookings(name)
        print(allBookings)
        bookingData = []
        bookingIdData = {}
        

        for booking in allBookings: 
            price = "$" + str(dbfunc.GetService(booking[0], booking[1])[4][0]) + "0"
            # print(price)
            bookingData.append([booking[0], booking[1], str(booking[3])[:10],str(booking[3])[11:], str(booking[4])[11:], price, booking[6]])
            
            print(booking[6])

        # for booking in allBookings:
            # tempData = [book,]
        return render_template('templates/bookings.html', bookings = bookingData)

    # return render_template('templates/Bbookings.html')
    return

@app.route('/deleteBookingFunction')
def deleteBooking():
    data = request.json
    print(data.get("bookingID"))


    return jsonify()

@app.route('/employees')
def employeePage():
    # Get user information
    username = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not username: 
        print("Empty Username!")
        return redirect(url_for('login'))

    if g.role == "Business":
        
        BusinessInfo = CallBusinessName(username)
        bname = BusinessInfo[0]
        employees = dbfunc.CallBusinessEmployees(bname)

    elif g.role == "Administrator":
        
        bname = dbfunc.CallEmployeeInfo(username)[3]
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
    print("Current username: " , currentUsername)
    print("username: ", username)
    
    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect(url_for('login'))

    # debuig this - there might be an error!!!

    # General Business Information
    businessInfo = dbfunc.CallBusinessInfo(username)
    print("businessInfo")
    print(businessInfo)
    print(dbfunc.CallBusinessInfo(username))
    print(dbfunc.CallBusinessName(username))
    if dbfunc.CallBusinessInfo(username) != None: 
        businessInfo = dbfunc.CallBusinessInfo(username)
    else:
        businessInfo = dbfunc.CallBusinessInfo(username)
    print(CallBusinessName(username))
    # print(bus)
    # businessInfo = CallBusinessInfo(username)
    # businessInfo = CallBusinessInfo(CallBusinessName(username)[0])
    # print(businessInfo)
    
    businessName = businessInfo[0]
    businessAddress = businessInfo[3] + ", " + businessInfo[2]
    businessUsername = businessInfo[6]


    # stars = "4"

    # Get array for services

    arrServices = GetBusinessServices(businessName)
    
    # get descriptions
    #serviceDescription = dbfunc.GetDescription(arrServices, business_username)

    # Time Table

    # Map
    bcoords = dbfunc.CheckCoordinates(businessUsername)
    b_lat, b_lng = bcoords
    print(b_lat, b_lng)
    fullAddress = businessInfo[5] + " " + businessInfo[4] + " " + businessInfo[3] + ", " + businessInfo[2]
    print(fullAddress)
    #If we want to do direction maps??
    user_coords = dbfunc.CheckCoordinates(currentUsername)
    user_lat, user_lng = user_coords
    
    # Reviews

    return render_template('templates/bProfile.html', businessName = businessName, businessAddress=businessAddress, title='View Buisness', businessUsername=businessUsername, arrServices=arrServices, api_key=API_KEY, b_lat=b_lat, b_lng=b_lng, fullAddress=fullAddress)


@app.route('/business/edit')
def businessEditProfilePage():
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect(url_for('login'))

    return render_template('templates/bEdit.html', title="Edit Profile")

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
    print(GetBusinessServices(CallBusinessName(currentUsername)[0]))
    
    return render_template('templates/servicePage.html', service=[[row[1], "$" + str(row[2]) + "0", row[3], str(row[4]) + "0"]for row in GetBusinessServices(CallBusinessName(currentUsername)[0])], nextLink=[CallBusinessName(currentUsername)])
    # return render_template('templates/servicePage.html', service=GetBusinessServices(CallBusinessName(currentUsername)[0]))

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
    time = request.form.get('time')

    bName = CallBusinessName(currentUsername)[0]

    # print(name + " " + price + " " + bName + " " + slots)

    # Create the swervice with both the given and known information
    CreateService(bName, name, price, slots, time, "0")


    # Retrieve break times
    break_start = request.form.get('break-start')
    break_end = request.form.get('break-end')


    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # UpdateAvailability(bName, name, 'Monday', '03.00', '04.00', '05.00', '06.00')
    
    for i in days:
        startLabel = i.lower() + '-start'    
        endLabel = i.lower() + '-end'   
        # print(request.form.get(startLabel))
        if request.form.get(startLabel) != "":  
            # Add to the database
            UpdateAvailability(bName, name, i, request.form.get(startLabel).replace(':','.'), request.form.get(endLabel).replace(':','.'), break_start.replace(':','.'), break_end.replace(':','.'))
        else:
            # TODO: Updaet this with the default hours for the business 
            UpdateAvailability(bName, name, i, '10.00', '17.00', '12.00', '13.00')
            
        
    # come back to this
    UpdateDescription(name, bName, request.form.get('description'))

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
def singleServicePage(businessname, serviceName):
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect('/login')

    # Get avalible service times 
    print("hi there")
    print(GetHours(serviceName, businessname))

    hours = GetHours(serviceName, businessname)

    # print(Get)
    return render_template("templates/sView.html", businessName=businessname, serviceName=serviceName, hours=hours)

@app.route('/<businessname>/service/edit/<serviceName>', methods=['GET', 'POST'])
def singleServiceEditPage(businessname, serviceName):
# Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        print("Empty Username!")
        return redirect('/login')
    
    if request.method == 'POST':
        updateService(businessname, serviceName)

    # Get Current Service Information
    currentService = dbfunc.GetService(serviceName, businessname)
    currentServiceDescription = dbfunc.GetDescription(serviceName, businessname)
    return render_template("templates/sEdit.html", currentService=currentService, currentServiceDescription=currentServiceDescription)

def updateService(businessname, serviceName): 

    currentService = dbfunc.GetService(serviceName, businessname)

    # TODO: See if this is right
    information = {'name': currentService[0][0], 'service': currentService[1][0], 'price': currentService[2][0], 'slots': currentService[3][0 ], 'time': currentService[4][0], 'discount': currentService[5][0]}
    print(information)
    dbfunc.UpdateService(information['service'], information['name'], information["price"], information['slots'], information['time'], "0")

    for i in request.form:
        
        if request.form.get(i) != "":
            # new data
            information[i] = request.form.get(i)

    # update the service:
    print(information)
    print(information['service'])

    dbfunc.UpdateService(information['service'], information['name'], information["price"], information['slots'], information['time'], "0")

    print('hello thereß')

    return

@app.route('/<businessname>/service/delete/<serviceName>')
def deleteService(businessname, serviceName):
    
    # Delete the service bookings TODO


    # Delete the service
    dbfunc.DeleteService(serviceName, businessname)     

    return redirect(url_for('servicePage'))

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
    user_coords = dbfunc.CheckCoordinates(username)

    if not user_coords:
        app.logger.error(f"Coordinates not found for user {username}")
        return jsonify({'error': 'User coordinates not found'}), 404

    user_lat, user_lng = user_coords
    return jsonify({'lat': user_lat, 'lng': user_lng})
    
#Need a function to grab all businesses in the area??
@app.route('/get-nearby-businesses')
def get_nearby_businesses():
    username = session.get('username')
    user_coords = dbfunc.CheckCoordinates(username)

    if not user_coords:
        app.logger.error(f"Coordinates not found for user {username}")
        return jsonify({'error': 'User coordinates not found'}), 404

    user_lat, user_lng = user_coords

    try:
        nearby_businesses = dbfunc.CallBusinessGeo(username)
    except Exception as e:
        app.logger.error(f"Error fetching nearby businesses for {username}: {str(e)}")
        return jsonify({'error': 'Error fetching nearby businesses'}), 500

    if not nearby_businesses:
        return jsonify([])

    formatted_businesses = [{
        'username': business[0],
        'name': business[1],
        'lat': dbfunc.CheckCoordinates(business[0])[0],
        'lng': dbfunc.CheckCoordinates(business[0])[1]
        
    } for business in nearby_businesses]

    return jsonify(formatted_businesses)

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    session.pop('username',None)
    flash('You have been logged out.')
    return redirect('/')



@app.route('/run_python', methods=['POST'])
def run_python():
    data = request.get_json()

    # print(data)
    print("asjksdfhkjs")
    print(data['dateInfo'])
    # print(data['dateInfo'][:-1])

    date_obj = data['dateInfo'][:-1]
    date_obj = datetime.strptime(data['dateInfo'][:-1]  , "%Y-%m-%dT%H:%M:%S.%f")


    year = date_obj.year
    month = date_obj.month
    day = date_obj.day
    hour = date_obj.hour
    minute = date_obj.minute
    second = date_obj.second
    microsecond = date_obj.microsecond

    # print(year)\
    # CHATGBT Function
    def get_month_code(month_number):
        # Ensure the input is an integer between 1 and 12
        if 1 <= month_number <= 12:
            # Create a datetime object for the first day of the given month
            date = datetime(2024, month_number, 1)  # Year doesn't matter here
            # Format the month as a 3-letter uppercase code
            month_code = date.strftime('%b').upper()
            return month_code
            
    # Get the bookings for that date
    hours = dbfunc.GetHoursDay("hair appointment", "TestB", "Monday") #TODO: Make this dynamic

    

    # Show all of the timeslots

    # Calculate time slots
    timeSlots = []
    time_format = "%H:%M"  # Time format
    startHours = datetime.strptime(hours[0][3], time_format)
    endHours = datetime.strptime(hours[0][4], time_format)
    breakStart = datetime.strptime(hours[0][5], time_format)
    breakEnd = datetime.strptime(hours[0][6], time_format)



    # TODO: Make this faster
    while startHours < endHours: 
        # is this time already booked? 
        if startHours.hour > 12:
            time = str(day) + "-" + get_month_code(month) + "-" + str(year) + " " + str(startHours.hour - 12) + ":" + str(startHours.minute)
        else: 
            time = str(day) + "-" + get_month_code(month) + "-" + str(year) + " " + str(startHours.hour) + ":" + str(startHours.minute)
        currentBookings = dbfunc.getBusinessBookingsOnDate("TestB", time)
        if currentBookings == []:
            timeSlots.append(startHours)
            # print(startHours.minute)
            startHours_est = est.localize(startHours)
            timeSlots[len(timeSlots) - 1] = datetime(year, month, day, startHours.hour, startHours.minute, startHours.second)
            timeSlots[len(timeSlots) - 1] = startHours_est
            timeSlots[len(timeSlots) - 1] += timedelta(minutes=4) #IDK why this needs to be here, but it does
        
        timeDelta = timedelta(minutes=30) #TODO: Make this dynamic
        startHours += timeDelta


    #         # print(len(timeSlots))
    return jsonify(result=timeSlots)

@app.route('/run_python_function', methods=['POST'])
def run_python_function():
    data = request.json  # Get JSON data sent from JavaScript
    button_id = data.get('buttonId')  # Extract button id from the data

    username = session.get('username')
    

    parsed_url = urlparse(data.get("location"))

    # Extract different components
    scheme = parsed_url.scheme  # e.g., 'http'
    netloc = parsed_url.netloc  # e.g., '127.0.0.1:5000'
    path = parsed_url.path      # e.g., '/TestB/service/test1s'
    query = parsed_url.query    # e.g., '' (empty if no query string)
    fragment = parsed_url.fragment  # e.g., '' (empty if no fragment)

    # Split the path into components
    path_components = path.strip('/').split('/')
    
    # Extract specific path components
    service = path_components[0] if len(path_components) > 0 else None
    test = path_components[1] if len(path_components) > 1 else None
    test_detail = path_components[2] if len(path_components) > 2 else None

    # Regular expression to capture the components
    pattern = r'(\w{3}) (\w{3}) (\d{2}) (\d{4}) (\d{2}:\d{2}:\d{2}) GMT([+-]\d{4}) \((.*)\)'

    # Match the pattern
    match = re.match(pattern, data.get("date"))

    if match:
        day_of_week = match.group(1)
        month = match.group(2)
        day = match.group(3)
        year = match.group(4)
        # time = match.group(5)
        time = data.get("buttonId")
        time2 = datetime.strptime(time, '%H:%M') + timedelta(minutes = 20)
        new_time_str = time2.strftime('%H:%M')

        timezone_offset = match.group(6)
        timezone_name = match.group(7)

        
        # Combine date and time
        # date_time_str = f"{day} {month} {year} {time}"
        date_time_str = f"{month} {day} {year} {time}"
        print("TOMATO")
        print(date_time_str)
        # date_time_str2 = f"{day} {month} {year} {time2}"
        date_time_str2 = f"{month} {day} {year} {new_time_str}"
        print(date_time_str2)
        # print(date_time_str2)
        
        # Parse the combined string into a datetime object
        date_time_obj = datetime.strptime(date_time_str, '%b %d %Y %H:%M')
        # date_time_obj2 = datetime.strptime(date_time_str2, '%d %b %Y %H:%M:%S')
        
    
    date_time_obj2 = date_time_obj + timedelta(minutes = 20)
    # print(date_time_obj2)
    # print(date_time_str2)

    print("========")
    test_detail = test_detail.replace("%20", " ")
    print(test_detail)
    service = service.replace("%20", " ")
    print(service)
    # username = "otest"
    print(username)
    print("========")

    

    dbfunc.CreateBooking(test_detail, service, username, date_time_str, date_time_str2, "null")
    # result = my_python_function(button_id)

    print(dbfunc.getUserBookings("ctest"))
    result="hi there"
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(debug=True)