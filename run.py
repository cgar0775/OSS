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
from math import radians, cos, sin, asin, sqrt
import dbfunc

from urllib.parse import urlparse
from werkzeug.utils import secure_filename


from datetime import datetime, timedelta, date

from dbfunc import CreateCustomerAcc,CreateBusinessAcc, loginCheck, CallBusinessInfo, CheckBusinessName, CheckUsername, CallCustomerInfo, CreateService, GetBusinessServices, UpdateAvailability, CallBusinessName, CheckRole, UpdateDescription, GetHours, getBusinessBookings,getReviews


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


app.config['UPLOAD_FOLDER'] = 'static/images/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
# app.config['username'] = ""

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
        g.username = username
        g.role = CheckRole(username)[0]
        if g.role == "Business":
            bname = CallBusinessName(username)[0]
            g.data = CallBusinessInfo(bname)
            # #print("g.data: ")
            # #print(g.data)
        elif g.role == "Employee":
            g.data = dbfunc.CallEmployeeInfo(username)
        
        elif g.role == "Administrator":
            g.data = dbfunc.CallEmployeeInfo(username)
        
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
        session['s_nearby_businesses_t']=False
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
         # ##print the address for debugging purposes
         # #print(f"Address: {full_address}")
    
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
         # #print the address for debugging purposes
         # #print(f"Address: {full_address}")
    
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
    
    #print(username)
    # username = "otest"
    #CustomerInfo = dbfunc.CallCustomerInfo(username)
    ##print(CustomerInfo)
    # name = "Olivia"
    #BusinessInfo = CallBusinessInfo(username)
    #name = BusinessInfo[0]

    # If they are not logged in, redirect them to the login page
    if not username: 
        #print("Empty Username!")
        return redirect(url_for('login'))
    
    # if they are logged in, what type of account???
    

    if CheckRole(username)[0] == 'Customer':
        CustomerInfo = CallCustomerInfo(username)
        name = CustomerInfo[1]

        # nearby_business = dbfunc.CallBusinessGeo(username)
        # return render_template('home.html', name = name)
        if not session.get('s_nearby_businesses_t'):
            nearby_businesses = dbfunc.CallBusinessGeo(username)
            businesses = []
            connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
            cursor=connection.cursor()
            for business in nearby_businesses:
                business_name = business[3]
                businessInfo = dbfunc.CallBusinessInfoUnbound(business_name,connection,cursor)
                address = f"{businessInfo[5]} {businessInfo[4]} {businessInfo[3]}, {businessInfo[2]}"
                business_services = dbfunc.GetBusinessServicesUnbound(business_name,connection,cursor)
                business_geo=dbfunc.CheckCoordinatesUnbound(business[2],connection, cursor)
                services = []
                
                for service in business_services:
                    service_name = service[1]  # Extract 'Haircut' from ('Test123', 'Haircut', 300.0, 3, '300:0', 0)
                    service_price = service[2]  # Extract the price (300.0)
                    services.append({
                        'name': service_name,
                        'price': service_price
                    })
                ##print("service", service)
                businesses.append({
                    'username': business[2],
                    'name': business_name,
                    'address': address,
                    'services': services,
                    'profile_url': url_for('businessViewProfilePage', username=business[2]),
                    'lat': business_geo[0],
                    'lng': business_geo[1]
                })
                ##print("nearby", nearby_businesses)
                #print("business", businesses)
            
            session['s_nearby_businesses']=businesses
            session['s_nearby_businesses_t']=True
            cursor.close()
            connection.close()
            return render_template('home.html', name=name, nearby_businesses=businesses)
        else:
            businesses=session.get('s_nearby_businesses')
            return render_template('home.html', name=name, nearby_businesses=businesses)
        
    elif CheckRole(username)=='Business':

    # if CallBusinessInfo(CallBusinessName(username)[0]):
        
        BusinessInfo = CallBusinessInfo(CallBusinessName(username)[0])
        return render_template('bHome.html', name = BusinessInfo[0]) #Change this to the buisness home page!!!

    # Check to see if it is an employee
    elif CheckRole(username)=='Employee':
    # if CallBusinessInfo(CallBusinessName(username)[0]):
        
        BusinessInfo = CallBusinessInfo(CallBusinessName(username)[0])
        return render_template('bHome.html', name = BusinessInfo[0])
    
    # return render_template('home.html', name = "name")
    return render_template('home.html')

@app.route('/search', methods=['GET', 'POST'])

def searchPage():
    # Get user information
    username = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not username: 
        #print("Empty Username!")
        return redirect(url_for('login'))


    user_coords = dbfunc.CheckCoordinates(username)
    if not user_coords:
        return render_template('templates/search.html', error="Unable to fetch user location")

    user_lat, user_lng = user_coords
    query = ""
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if not query:
            return render_template('templates/search.html', error="Search query cannot be empty")

        #try:
            # Fetch all businesses within a 20-mile radius of the user
        nearby_businesses = session.get('s_nearby_businesses')
        ##print(nearby_businesses)
        matching_businesses = []
        ##print(nearby_businesses)
        for business in nearby_businesses:
            business_name = business['name']
            services = business['services']
            #if query.lower() in business_name.lower():
                ##print("found")
            for service in services:
                if query.lower() in service['name'].lower() or query.lower() in business['name'].lower():  # Case-insensitive search
                    #print("found")
                    matching_businesses.append({
                        'business_name': business_name,
                        'business_username': business['username'],
                        'address': business['address'],
                        'service_name': service['name'],  # Assuming service[1] is the service name
                        'service_price': service['price'],  # Assuming service[2] is the price
                        'lat': business['lat'],
                        'lng': business['lng']
                    })
        if len(matching_businesses)==0:
            return render_template('templates/search.html', error="No matching services found.", query=query)
        return render_template('templates/search.html', businesses=matching_businesses, query=query)

        #except Exception as e:
            #app.logger.error(f"Error fetching businesses for query '{query}': {str(e)}")
            #return render_template('templates/search.html', error="Error fetching businesses")

    return render_template('templates/search.html', api_key = API_KEY)


@app.route('/profile')
def profilePage():
    # Get user information
    username = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not username: 
        #print("Empty Username!")
        return redirect(url_for('login'))
    name = dbfunc.CallCustomerInfo(username)[1] + " " + dbfunc.CallCustomerInfo(username)[2]
    return render_template('templates/cEdit.html', name=name)

@app.route('/bookings')
def bookingPage():

    # Get user information
    username = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not username: 
        #print("Empty Username!")
        return redirect(url_for('login'))
    
    #print(CheckRole(username)[0])

    # TODO: Make this faster
    # Get all of the bookings for the business
    if CheckRole(username)[0] == 'Business' and 'Employee' and 'Administrator':
        name = CallBusinessName(username)[0]
        allBookings = dbfunc.getBusinessBookings(name)
        bookingData = []
        idList = []

        # #print(allBookings)
        for booking in allBookings:
            # #print(dbfunc.CallCustomerInfo(booking[2])) 
            customerName = dbfunc.CallCustomerInfo(booking[2])[1] + " " + dbfunc.CallCustomerInfo(booking[2])[2]
            tempData = [booking[0], customerName , str(booking[3])[:10], str(booking[3])[11:], str(booking[4])[11:], dbfunc.CallCustomerInfo(booking[2])[8], dbfunc.CallCustomerInfo(booking[2])[7], booking[5]]
            # print()
            bookingData.append(tempData)

            print(booking)
            print(booking[6])
            
            idList.append(booking[6])


        # #print (bookingData)
        return render_template("templates/bBookings.html", bookings = bookingData, idList=idList)

    if CheckRole(username)[0] == 'Customer':
        name = username
        allBookings = dbfunc.getUserBookings(name)
        #print(allBookings)
        bookingData = []
        bookingIdData = {}
        

        for booking in allBookings: 
            price = "$" + str(dbfunc.GetService(booking[0], booking[1])[4][0]) + "0"
            # #print(price)
            bookingData.append([booking[0], booking[1], str(booking[3])[:10],str(booking[3])[11:], str(booking[4])[11:], price, booking[6]])
            
    
        # for booking in allBookings:
            # tempData = [book,]
        return render_template('templates/bookings.html', bookings = bookingData)

    # return render_template('templates/Bbookings.html')
    return render_template("templates/bBookings.html")

@app.route('/deleteBookingFunction', methods=['POST'])
def deleteBooking():
    data = request.json
    dbfunc.DeleteBookingFromID(data.get("bookingID"))

    return jsonify(data)

@app.route('/booking/delete/<id>')
def deleteBookingID(id):

    dbfunc.DeleteBookingFromID(id)

    return redirect('/bookings')

@app.route('/employees')
def employeePage():
    # Get user information
    username = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not username: 
        #print("Empty Username!")
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
    username = session.get('username')
    #print(username)
    #print("role:", g.role)
    if g.role == "Business":
        redir = '/business/view/' + username
    else:
        employeeInfo = dbfunc.CallEmployeeInfo(username)
        ##print(employeeInfo)
        ##print(employeeInfo[3])
        businessUsername = CallBusinessInfo(employeeInfo[3])[6]
        redir = '/business/view/' + businessUsername

    return redirect(redir)

@app.route('/business/view/<username>',  methods = ['GET','POST'])
def businessViewProfilePage(username):

    # Get user information
    currentUsername = session.get('username')
    #print("Current username: " , currentUsername)
    #print("business username: ", username)
    
    # business_username = dbfunc.CallBusinessInfo(username)
    # #print("Business Username: ", business_username) 

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        #print("Empty Username!")
        return redirect(url_for('login'))

    # debuig this - there might be an error!!!

    # General Business Information
    #businessInfo = dbfunc.CallBusinessInfo(username)
    ##print("businessInfo")
    ##print(businessInfo)
    ##print(dbfunc.CallBusinessInfo(username))
    ##print(dbfunc.CallBusinessName(username))
    if dbfunc.CallBusinessInfo(username) != None: 
        businessInfo = dbfunc.CallBusinessInfo(username)
    else:
        businessInfo = dbfunc.CallBusinessInfo(username)
    #print(CallBusinessName(username))
    #print(CallBusinessInfo(username))
    businessInfo = CallBusinessInfo(CallBusinessName(username)[0])
    businessName = businessInfo[0]
    businessAddress = businessInfo[3] + ", " + businessInfo[2]
    businessUsername = businessInfo[6]


    # stars = "4"

    # Get array for services

    arrServices = GetBusinessServices(businessName)
    
    # get descriptions
    

    # Time Table

    # Map
    bcoords = dbfunc.CheckCoordinates(businessUsername)
    if bcoords is not None: 
        b_lat, b_lng = bcoords
        #print(b_lat, b_lng)
    else: 
        b_lat, b_lng = 0, 0
    fullAddress = businessInfo[5] + " " + businessInfo[4] + " " + businessInfo[3] + ", " + businessInfo[2]
    #print(fullAddress)
    #If we want to do direction maps??
    user_coords = dbfunc.CheckCoordinates(currentUsername)
    #user   _lat, user_lng = user_coords
    
    # Reviews
    
    profilePath = "static/images/uploads/" + businessUsername + "/profile_picture.png"
    file_exists = os.path.isfile(profilePath)


    profilePath1 = "static/images/uploads/" + businessUsername + "/cover_photo.png"
    background_exists = os.path.isfile(profilePath1)
    #print(background_exists) 
    #print(businessUsername) 

    #Service hours

 
    return render_template('templates/bProfile.html', businessName = businessName, businessAddress=businessAddress, title='View Buisness', businessUsername=businessUsername, arrServices=arrServices, api_key=API_KEY, b_lat=b_lat, b_lng=b_lng, fullAddress=fullAddress, file_exists=file_exists, background_exists=background_exists)


@app.route('/business/edit')
def businessEditProfilePage():
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        #print("Empty Username!")
        return redirect(url_for('login'))
    
    
    businessUsername = currentUsername
    profilePath = "static/images/uploads/" + businessUsername + "/profile_picture.png"
    file_exists = os.path.isfile(profilePath)


    profilePath1 = "static/images/uploads/" + businessUsername + "/cover_photo.png"
    background_exists = os.path.isfile(profilePath1)
    #print(profilePath1) 
    #print(background_exists) 
    #print(businessUsername) 

    return render_template('templates/bEdit.html', title="Edit Profile", username=currentUsername, businessName=CallBusinessName(currentUsername)[0], file_exists=file_exists, background_exists=background_exists)


def save_file(file, field_name):
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        # Create a unique filename based on the field name
        filename = f"{field_name}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return filename
    return None


@app.route('/upload', methods=['get', 'POST'])
def upload_file():
    # Get user information
    currentUsername = session.get('username')


    uploadFolder = "static/images/uploads/" + currentUsername
    
    # Create the directory if it doesn't exist
    if not os.path.exists(uploadFolder):
        os.makedirs(uploadFolder)


    profile_picture = request.files.get('profilePicture')
    cover_photo = request.files.get('bannerFile')

    if profile_picture:
        #print("here")
        extension = ".png" # os.path.splitext(profile_picture.filename)[1]
        # Generate the custom filename
        filename = f"profile_picture{extension}"
        profile_picture_filename = "profile_picture" + extension
        profile_picture.save(os.path.join(uploadFolder,profile_picture_filename))
        #print("here")
    if cover_photo:
        extension = ".png" # os.path.splitext(cover_photo.filename)[1]
        # Generate the custom filename
        filename = f"cover_photo{extension}"
        cover_photo_filename = "cover_photo" + extension
        cover_photo.save(os.path.join(uploadFolder,cover_photo_filename))
        #print("here")

     
    #print(request.form.get("bname"))
    if request.form.get("bname") != "":
        dbfunc.UpdateService()


    return redirect('/business/edit')

    
    

@app.route('/profile/view')
def customerViewProfilePage():
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        #print("Empty Username!")
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
        #print("Empty Username!")
        return redirect(url_for('login'))

    # return render_template('templates/cEdit.html')
    return render_template('templates/bEdit.html')

@app.route('/services')
def servicePage():
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        #print("Empty Username!")
        return redirect(url_for('login'))
    ##print("currentUsername:", currentUsername)
    employeeInfo = dbfunc.CallEmployeeInfo(currentUsername)
    # #print("employee info:", employeeInfo)
    # #print("business_name: ", employeeInfo[3])
    # #print(CallBusinessName(currentUsername))
    # #print(CallBusinessInfo(CallBusinessName(currentUsername)))
    # #print(GetBusinessServices(CallBusinessName(currentUsername)[0]))
    # if business
    if g.role == "Business":
        return render_template('templates/servicePage.html', service=[[row[1], "$" + str(row[2]) + "0", row[3], str(row[4]) + "0"]for row in GetBusinessServices(CallBusinessName(currentUsername)[0])], nextLink=[CallBusinessName(currentUsername)])
    else:
        return render_template('templates/servicePage.html', service=[[row[1], "$" + str(row[2]) + "0", row[3], str(row[4]) + "0"]for row in GetBusinessServices(employeeInfo[3])], nextLink=[employeeInfo[3]])
    # return render_template('templates/servicePage.html', service=GetBusinessServices(CallBusinessName(currentUsername)[0]))

@app.route('/add-service', methods = ['GET','POST'])
def addService():
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        #print("Empty Username!")
        return redirect(url_for('login'))

    if request.method == "POST":
       print("Hello there")

    return render_template('templates/addService.html')

def checkLogin():
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        #print("Empty Username!")
        return redirect('/login')

@app.route('/submit-form', methods=['POST', 'GET'])
def addServiceFunction():
    # Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        #print("Empty Username!")
        return redirect('/login')
    #print(request.form)
    name = request.form.get('name')
    price = request.form.get('price')
    slots = request.form.get('slots')
    time = request.form.get('time')

    bName = CallBusinessName(currentUsername)[0]

    # #print(name + " " + price + " " + bName + " " + slots)

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
        # #print(request.form.get(startLabel))
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
        #print("Empty Username!")
        return redirect('/login')

    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    breakStart = request.form.get("break-start")
    breakEnd = request.form.get("break-end")

    for i in days:
        startLabel = i + '-start'    
        endLabel = i + '-end'    
        
        #print(request.form.get(startLabel))
        #print(request.form.get(endLabel))

        # UpdateAvailability('Pozie Jewelry', 'thingy4', i, startLabel, endLabel, breakStart, breakEnd)

    return redirect(url_for('servicePage'))

def getDBconnection():
    if not hasattr(g, 'connection'):
        g.connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
        g.cursor=g.connection.cursor(scrollable=True)


@app.route('/booking/edit/<bookingId>',  methods = ['GET','POST'])
def reBook(bookingId=None):
    currentUsername = session.get('username')
    
    bookingInfo = dbfunc.getBookingFromId(bookingId)
    
    customerName = "Editing: " + dbfunc.CallCustomerInfo(dbfunc.getBookingFromId(bookingId)[0][2])[1] + " " + dbfunc.CallCustomerInfo(dbfunc.getBookingFromId(bookingId)[0][2])[2]
    customerUser = dbfunc.getBookingFromId(bookingId)[0][2]
    print(customerUser)

    print(bookingInfo)
    currentDiscount = bookingInfo[0][5]    

    return render_template("templates/sView.html", bookingId=bookingId, businessName=bookingInfo[0][1], serviceName=bookingInfo[0][0], customerName=customerName, customerUser=customerUser, currentDiscount=currentDiscount)
    # `return render_template("templates/sView.html", businessName=businessname, serviceName=serviceName, hours=hours, reviews = formatted_reviews, username=businessUsername, background_exists=background_exists, file_exists=file_exists)

@app.route('/<businessname>/service/<serviceName>')
def singleServicePage(businessname, serviceName):
    
    #getDBconnection()

    # Get user information
    currentUsername = session.get('username')
    
    businessUsername = dbfunc.CallBusinessInfo(businessname)[6]
    # #print(bUsername)
    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        #print("Empty Username!")
        return redirect('/login')

    # Get avalible service times 
    hours = GetHours(serviceName, businessname)

    #gets inital reviews
    #reviews = dbfunc.getReviewScrollStart(10,businessname,serviceName,g.cursor,g.connection)

    reviews = dbfunc.getReviews(businessname, serviceName)
    
    #only capturing first 10
    reviews = reviews[:10]
    ##print("reviews")
    ##print(reviews)
    
    formatted_reviews = [{
        'id': r[0],
        'username': r[1],
        'fname': r[2],
        'lname': r[3],
        'header': r[4],
        'body': r[5],
        'rating': r[6],
        'businessname': r[7],
        'servicename': r[8]
    } for r in reviews]

    #if leave page do the following
    #cursor.close()
    #connection.close()
    

    profilePath = "static/images/uploads/" + businessUsername + "/profile_picture.png"
    file_exists = os.path.isfile(profilePath)


    profilePath1 = "static/images/uploads/" + businessUsername + "/cover_photo.png"
    background_exists = os.path.isfile(profilePath1)
    #print(background_exists) 
    #print(businessUsername) 

    return render_template("templates/sView.html", businessName=businessname, serviceName=serviceName, hours=hours, reviews = formatted_reviews, username=businessUsername, background_exists=background_exists, file_exists=file_exists, userType="customer")

@app.route('/exitingServicePage', methods = ['post'])
def exitingServicePage():
    #print("hi there")
    
    dbfunc.closeConnections()

    return

@app.route('/<businessname>/service/edit/<serviceName>', methods=['GET', 'POST'])
def singleServiceEditPage(businessname, serviceName):
# Get user information
    currentUsername = session.get('username')

    # If they are not logged in, redirect them to the login page
    if not currentUsername: 
        #print("Empty Username!")
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
    #print(information)
    dbfunc.UpdateService(information['service'], information['name'], information["price"], information['slots'], information['time'], "0")

    for i in request.form:
        
        if request.form.get(i) != "":
            # new data
            information[i] = request.form.get(i)

    # update the service:
    #print(information)
    #print(information['service'])

    dbfunc.UpdateService(information['service'], information['name'], information["price"], information['slots'], information['time'], "0")

    #print('hello thereß')

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
        #print("Empty Username!")
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
    if not username:
        return redirect(url_for('login'))

    lat = request.args.get('lat')
    lng = request.args.get('lng')
    name = request.args.get('name')
    address = request.args.get('address')

    if not lat or not lng or not name or not address:
        return "Invalid parameters", 400

    return render_template('maps.html', api_key=API_KEY, lat=lat, lng=lng, name=name, address=address)


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
    # get the avalible times
    data = request.get_json()
    buser = dbfunc.CallBusinessInfo(data["bInfo"])[6]
    timeSlot = data["dateInfo"]
    #print(timeSlot)
    #print(timeSlot[:10])
    serviceName = data["sname"]
    serviceInfo = dbfunc.GetService(serviceName, data['bInfo'])
    #print("serviceInfo")
    #print(serviceInfo)
    slots = serviceInfo[3][0]
    #print(slots)
    # avalibleSlots = dbfunc.GetService()
    
    
    bookingInfo = dbfunc.getBusinessBookingsOnDate(data['bInfo'], timeSlot[:10])
    #print(bookingInfo)

    avalibleTimes = []
    timeSlotLength = 30
    #print(datetime.strptime(timeSlot[:10], "%Y-%m-%d").strftime("%A"))
    date_obj = datetime.strptime(timeSlot[:10], "%Y-%m-%d") 
    weekday = datetime.strptime(timeSlot[:10], "%Y-%m-%d").strftime("%A")
    hours = dbfunc.GetHoursDay(serviceInfo[1][0], serviceInfo[0][0], weekday) #TODO: Make this dynamic

    hours = [[None, None, None, hours[0][3], hours[0][4], hours[0][5], hours[0][6]]] #maybe delete this

    time_format = "%H:%M"  # Time format
    # startHours = datetime.strptime(hours[0][3], time_format)
    # # startHours = datetime.(hours[0][3], time_format)
    # endHours = datetime.strptime(hours[0][4], time_format)
    # breakStart = datetime.strptime(hours[0][5], time_format)
    # breakEnd = datetime.strptime(hours[0][6], time_format)

    startHours = datetime.combine(date_obj, datetime.strptime(hours[0][3], time_format).time())
    endHours = datetime.combine(date_obj, datetime.strptime(hours[0][4], time_format).time())
    breakStart = datetime.combine(date_obj, datetime.strptime(hours[0][5], time_format).time())
    breakEnd = datetime.combine(date_obj, datetime.strptime(hours[0][6], time_format).time())


    deltaTime = timedelta(minutes=serviceInfo[4][0])

    #print("type(hours[0][3]")
    #print(type(hours[0][3]))

    timeslots = []
    bookings = []

    while startHours < endHours: 
        startHours_est = est.localize(startHours)
        #print(startHours)

        # #print(dbfunc.getBusinessBookingsOnDateAndTime(buser, startHours))
        # #print()

        numBook = dbfunc.getBusinessBookingsOnDateAndTime(serviceInfo[0][0], startHours)[0][0]
        #print(numBook)

        if numBook < slots:
            #print("dbfunc.getBusinessBookingsOnDateAndTime(buser, startHours)[0][0]: ")
            #print(numBook)
            bookings.append(numBook)
            timeslots.append(startHours_est)
            #print(bookings)

        startHours += deltaTime

    #print(hours)
    #print(timeslots)


    return jsonify(result=timeslots, bookingsNum=bookings)


@app.route('/dataNeeded', methods=['post'])
def data():
    dailyBookingsInfo = {}
    
    chart_data = {
        'x': [],
        'y': []
    }

    current_date = datetime.now().date()
    startDate = current_date - timedelta(days = 7)

    while(startDate != current_date): #TODO: turn this into a do while loop
        #print(startDate)
        dailyBookingsInfo[startDate.strftime("%A")] = dbfunc.getBusinessBookingsOnDate('TestB', startDate)[0][0]
        startDate += timedelta(days = 1) 

    for i in dailyBookingsInfo:
        chart_data['x'].append(i)
        chart_data['y'].append(dailyBookingsInfo[i])

    layout = {
        # 'title': 'Sample Bar Chart',
        'xaxis': {'title': 'Weekdays'},
        'yaxis': {'title': 'Amount of Bookings'}
    }

    return jsonify({"data": chart_data, "layout": layout})

@app.route('/analytics')
def analyticsPage():

    username = session.get('username')
    
    # Get the data that goes on the chart    
    
    chart_data = {
        'x': ['a', 'b', 'c', 'd'],
        'y': [10, 15, 13, 117]
    }
    
    # current_date = datetime.now().date()
    # for i in range (7):
    #     #print(current_date - timedelta(days=i))
    #     #print(current_date.strftime("%A"))
    #     thing = current_date - timedelta(days=i)
    #     #print(dbfunc.getBusinessBookingsOnDate('TestB', thing))
    #     #print(len(dbfunc.getBusinessBookingsOnDate('TestB', thing)))
    #     dailyBookingsInfo[current_date - timedelta(days=i)] = (current_date - timedelta(days=i)).strftime("%A")

    #     # get the count for the days and then put them into the graph

    return render_template('templates/analytics.html')


@app.route('/load_more_reviews',methods=['POST'])
def load_more_reviews():
    
    data = request.get_json()
    businessname = data.get('businessName')
    servicename = data.get('serviceName')
    start = data.get('start')
    
    #print(businessname)
    #print(servicename)
    
    reviews = dbfunc.getReviews(businessname,servicename)
        
    if (len(reviews[start:]) >= 2 ):
        reviews = reviews[start:start+2]
    else:
        reviews = reviews[start:]

    #print("reviews")
    #print(reviews)

    formatted_reviews = [{
        'id': r[0],
        'username': r[1],
        'fname': r[2],
        'lname': r[3],
        'header': r[4],
        'body': r[5],
        'rating': r[6],
        'businessname': r[7],
        'servicename': r[8]
    } for r in reviews]

    # return render_template('sView.html', reviews=reviews)
    return jsonify({'reviews': formatted_reviews})



@app.route('/run_python_function', methods=['POST'])
def run_python_function():
    data = request.json  # Get JSON data sent from JavaScript
    button_id = data.get('buttonId')  # Extract button id from the data

    username = session.get('username')
    
    print(data.get('bookingID'))
    print(data.get('customer'))
    print("data.get('customerUser')")
    print(data.get('customerUser'))

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
        #print("TOMATO")
        #print(date_time_str)
        # date_time_str2 = f"{day} {month} {year} {time2}"
        date_time_str2 = f"{month} {day} {year} {new_time_str}"
        #print(date_time_str2)
        # #print(date_time_str2)
        
        # Parse the combined string into a datetime object
        date_time_obj = datetime.strptime(date_time_str, '%b %d %Y %H:%M')
        # date_time_obj2 = datetime.strptime(date_time_str2, '%d %b %Y %H:%M:%S')
        
    
    date_time_obj2 = date_time_obj + timedelta(minutes = 20)
    # #print(date_time_obj2)
    # #print(date_time_str2)

    #print("========")
    test_detail = test_detail.replace("%20", " ")
    #print(test_detail)
    service = service.replace("%20", " ")
    #print(service)
    # username = "otest"
    #print(username)
    #print("========")

    
    #THISSSS
    if g.role == "Business":
        # Customerusername = data.get('customer')[9:]
        # print(Customerusername)
        # cuser = dbfunc.CallCustomerInfoByName(Customerusername)
        # print(cuser)
        print(data.get('bookingId')[14:])
        print()
        print(dbfunc.getBookingFromId(data.get('bookingId')[14:]))
        service = dbfunc.getBookingFromId(data.get('bookingId')[14:])[0][0]
        businessName = dbfunc.getBookingFromId(data.get('bookingId')[14:])[0][1]
        print(test_detail)
        print("service")
        print(service)
        print( data.get('customerUser'))

        discount = 0

        # Delete old booking 
        dbfunc.DeleteBookingFromID(data.get('bookingId')[14:])

        dbfunc.CreateBooking(service, businessName, data.get('customerUser'), date_time_str, date_time_str2, discount)

        # return redirect('/home')
    elif g.role == "Customer":
        dbfunc.CreateBooking(test_detail, service, username, date_time_str, date_time_str2, "null")

    # result = my_python_function(button_id)

    #print(dbfunc.getUserBookings("ctest"))
    result="hi there"
    return jsonify(result=result)


@app.route('/apply_discount', methods=['POST'])
def applyDiscount():
    data = request.json
    print(data['discountAmount'])
    print(data.get('bookingId')[14:])

    dbfunc.ApplyDiscount(data['discountAmount'], data.get('bookingId')[14:])

    return jsonify()

if __name__ == '__main__':
    app.run(debug=True)