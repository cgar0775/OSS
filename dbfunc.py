#this file contains functions for database calls for various functions
import os
import oracledb
import hashlib
from database import OracleConfig
from dotenv import load_dotenv
import math
from haversine import haversine,Unit
load_dotenv()
#setup the database connection
database= OracleConfig()

# Login and Signup Functions

def hashPass(passw):
    #hashing the password
    encoded_pass=passw.encode()
    hash_object=hashlib.sha384(encoded_pass)
    hashed_passw=hash_object.hexdigest()
    return hashed_passw

def CheckRole(username):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"SELECT type FROM userlogin WHERE username='{username}'"
    cursor.execute(query)
    connection.commit()
    role=cursor.fetchone()
    cursor.close()
    connection.close()
    return role

def loginCheck(user,passw):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    #hash the password
    hashed_passw=hashPass(passw)
    #define the query for checking login
    query= f"SELECT COUNT(*) FROM userlogin where username='{user}' AND password='{hashed_passw}'"
    #check
    cursor.execute(query)
    connection.commit()
    check=cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return bool(check) 

def CreateCustomerAcc(username,password,firstname,lastname,country,state,city,address,email,phone):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    hashed_passw=hashPass(password)
    #fill the two tables needed
    query=f"INSERT INTO userlogin VALUES('{username}','{hashed_passw}','Customer')"
    query2=f"INSERT INTO CUSTOMERINFO VALUES('{username}','{firstname}','{lastname}','{country}','{state}','{city}','{address}','{email}','{phone}')"
    #execute the database calls
    print(query)
    cursor.execute(query)
    cursor.execute(query2)
    connection.commit()
    #close db connection for space
    cursor.close()
    connection.close()
    #end func
    #testing purposes erase later
    print("done")
    return

def CreateBusinessAcc(username,password,name,country,state,city,address,email,phone):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    hashed_passw=hashPass(password)
    #fill the two tables needed
    query=f"INSERT INTO userlogin VALUES('{username}','{hashed_passw}','Business')"
    query2=f"INSERT INTO BUSINESSINFO VALUES('{name}','{email}','{country}','{state}','{city}','{address}','{username}','{phone}')"
    #execute the database calls
    cursor.execute(query)
    cursor.execute(query2)
    connection.commit()
    #close db connection for space
    cursor.close()
    connection.close()
    #end func
    #testing purposes erase later
    print("done")
    return

#returns an array/tuple
def CallBusinessInfo(name):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    #calls a specific business' info from the database
    query=f"SELECT * FROM BUSINESSINFO WHERE name='{name}'"
    cursor.execute(query)
    connection.commit()
    #store result so we can close db connection
    val=cursor.fetchone()
    cursor.close()
    connection.close()
    #returns the first (and expectedly only) row
    return val

def CallBusinessInfoUnbound(name,connection,cursor):
    #calls a specific business' info from the database
    query=f"SELECT * FROM BUSINESSINFO WHERE name='{name}'"
    cursor.execute(query)
    connection.commit()
    #store result so we can close db connection
    val=cursor.fetchone()
    #returns the first (and expectedly only) row
    return val

def CallBusinessName(username):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    #calls a specific business' info from the database
    query=f"SELECT * FROM BUSINESSINFO WHERE username='{username}'"
    cursor.execute(query)
    connection.commit()
    #store result so we can close db connection
    val=cursor.fetchone()
    cursor.close()
    connection.close()
    #returns the first (and expectedly only) row
    return val

def CheckBusinessName(name):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    #calls a specific business' info from the database
    query=f"SELECT Count(*) FROM BUSINESSINFO WHERE name='{name}'"
    cursor.execute(query)
    connection.commit()
    #store result so we can close db connection
    val=cursor.fetchone()[0]
    cursor.close()
    connection.close()
    #returns the first (and expectedly only) row
    return val

def CallCustomerInfo(name):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    #calls a specific business' info from the database
    query=f"SELECT * FROM CUSTOMERINFO WHERE username='{name}'"
    cursor.execute(query)
    connection.commit()
    #store result so we can close db connection
    val=cursor.fetchone()
    cursor.close()
    connection.close()
    #returns the first (and expectedly only) row
    return val

#check username is already in db
def CheckUsername(name):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query= f"SELECT COUNT(*) FROM userlogin where username='{name}'"
    #check
    cursor.execute(query)
    connection.commit()
    check=cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return bool(check) 

#creates a service for a business
#inputs: business name (bname), service name (sname), price (float with 2 decimals), number of available slots (0 for unlimited)(for example only 4 hair stylists may be booked at the same time)
#time: time in hours and minutes that each service will take in the form of a float 1.40=1 hour 40 minutes in implementation CHECK THAT THE USER HASN't INPUTTED 60 MINUTES, this function doesn't check
#if someone inputs 1.60 into this function it will just send it 
def CreateService(bname,sname,price,slots,time,discount):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"INSERT INTO services VALUES('{bname}','{sname}',{price},{slots},{time},{discount})"  
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return

#create/update availability time for services
#inputs: business name (bname), service name (sname), the weekday that is being edited ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'), the opening/closing times
#in 24 hours time (09:00 for example)
def UpdateAvailability(bname,sname,weekday,opentime,closetime,breakstart,breakend):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    #check if this row already exists
    query1=f"SELECT COUNT(*) FROM servicehours WHERE bname='{bname}' AND sname='{sname}' AND weekday='{weekday}'"
    cursor.execute(query1)
    connection.commit()
    if bool(cursor.fetchone()[0]):
        #if the row exists merely update it otherwise insert new row
        query2=f"""UPDATE servicehours 
            SET opentime={opentime}, closetime={closetime}, breakstart={breakstart},breakend={breakend} 
            WHERE bname='{bname}' AND sname='{sname}' AND weekday='{weekday}'"""
    else:
        query2=f"""INSERT INTO servicehours VALUES('{sname}','{bname}','{weekday}',{opentime},{closetime},{breakstart},{breakend})"""
    cursor.close()
    cursor2=connection.cursor()
    cursor2.execute(query2)
    connection.commit()
    return

#returns a (presumed) 2D list of all services by a business
def GetBusinessServices(bname):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    #returns all services by x business
    query=f"SELECT * FROM services WHERE bname='{bname}'"
    cursor.execute(query)
    connection.commit()
    services=cursor.fetchall()
    cursor.close()
    connection.close()
    newservice=[]
    for tup in services:
        temp_list= list(tup)
        # temp_list[2] += "$"
        temp_list[4]=str(temp_list[2]).replace('.',':')
        new_tup=tuple(temp_list)
        newservice.append(new_tup)
    return newservice

#same as before except doesn't open its own connection
def GetBusinessServicesUnbound(bname,connection,cursor):
    #returns all services by x business
    query=f"SELECT * FROM services WHERE bname='{bname}'"
    cursor.execute(query)
    connection.commit()
    services=cursor.fetchall()
    newservice=[]
    for tup in services:
        temp_list= list(tup)
        # temp_list[2] += "$"
        temp_list[4]=str(temp_list[2]).replace('.',':')
        new_tup=tuple(temp_list)
        newservice.append(new_tup)
    return newservice

#gets the info of a specific service
def GetService(sname,bname):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"SELECT * FROM services WHERE bname='{bname}' AND sname='{sname}'"
    cursor.execute(query)
    connection.commit()
    #fetch the service
    service=cursor.fetchone()
    cursor.close()
    connection.close()
    newservice=[]
    for tup in service:
        if isinstance(tup, (list, tuple)):  # Check if tup is an iterable
            temp_list = list(tup)
            if len(temp_list) > 2:  # Ensure there are enough elements to modify
                temp_list[2] = str(temp_list[2]) + "$"
            if len(temp_list) > 4:  # Ensure there are enough elements to modify
                temp_list[4] = str(temp_list[4]).replace('.', ':')
            new_tup = tuple(temp_list)
            newservice.append(new_tup)
        else:
            # Handle the non-iterable case
            # print(f"Processing non-iterable item: {tup}")
            # You can decide how to handle this - here we'll convert it to a tuple with a single element
            newservice.append((tup,))
    return newservice

#update services
def UpdateService(sname,bname,price,slots, time, discount):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"""UPDATE services 
    SET sname='{sname}', bname='{bname}', price={price}, slots={slots}, discount={discount}
    WHERE sname='{sname}' AND bname='{bname}'"""
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return

def DeleteService(sname,bname):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"""DELETE FROM services WHERE sname='{sname}' AND bname='{bname}'"""
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return 

#get the hours table for any service
def GetHours(sname,bname):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"""SELECT * FROM servicehours WHERE sname='{sname}' AND bname='{bname}'"""
    cursor.execute(query)
    connection.commit()
    hours=cursor.fetchall()
    cursor.close()
    connection.close()
    newhours=[]
    for tup in hours:
        temp_list= list(tup)
        temp_list[2]=str(temp_list[2]).replace('.',':')
        temp_list[3]=str(temp_list[3]).replace('.',':')
        temp_list[4]=str(temp_list[4]).replace('.',':')
        temp_list[5]=str(temp_list[5]).replace('.',':')
        temp_list[6]=str(temp_list[6]).replace('.',':')
        new_tup=tuple(temp_list)
        newhours.append(new_tup)
    return newhours


#get the hours table for any service
def GetHoursDay(sname,bname,day):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"""SELECT * FROM servicehours WHERE sname='{sname}' AND bname='{bname}' AND weekday='{day}'"""
    cursor.execute(query)
    connection.commit()
    hours=cursor.fetchall()
    cursor.close()
    connection.close()
    newhours=[]
    for tup in hours:
        temp_list= list(tup)
        temp_list[2]=str(temp_list[2]).replace('.',':')
        temp_list[3]=str(temp_list[3]).replace('.',':')
        temp_list[4]=str(temp_list[4]).replace('.',':')
        temp_list[5]=str(temp_list[5]).replace('.',':')
        temp_list[6]=str(temp_list[6]).replace('.',':')
        new_tup=tuple(temp_list)
        newhours.append(new_tup)
    return newhours

def maxBookingId():
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"""SELECT MAX(id)
            FROM bookings"""
    cursor.execute(query)
    maxID = cursor.fetchone()
    connection.commit()
    cursor.close()
    connection.close()
    return maxID

#create booking
#inputs service name (sname), businessname (bname), username of the customer, timeslot_start the time and date of the start of the service, timeslot_end the ending time and date of the service
#both are in the format of MON-DD-YYYY HH:MM that being MON=3 letter shortening of the year Jan Feb etc, DD day 01,25 etc, YYYY the full year 2024 etc, HH:MM the time in 24 hour standard 09:30 for 9:30 AM
def CreateBooking(sname,bname,username,timeslot_start,timeslot_end,discount):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    naxtID = maxBookingId()[0] + 1
    query=f"INSERT INTO bookings VALUES('{sname}','{bname}','{username}',TO_DATE('{timeslot_start}', 'MON-DD-YYYY HH24:MI'),TO_DATE('{timeslot_end}', 'MON-DD-YYYY HH24:MI'), NULL, {naxtID})"
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return

#return a specific customer's bookings
def getUserBookings(username):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"SELECT * FROM bookings WHERE username='{username}'"
    cursor.execute(query)
    connection.commit()
    bookings=cursor.fetchall()
    cursor.close()
    connection.close()
    return bookings

#return a business' bookings
def getBusinessBookings(name):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"SELECT * FROM bookings WHERE bname='{name}'"
    cursor.execute(query)
    connection.commit()
    bookings=cursor.fetchall()
    cursor.close()
    connection.close()
    return bookings

#return a business' bookings
def getBusinessBookingsOnDate(name, date):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"SELECT * FROM bookings WHERE bname='{name}' AND timeslot_start = TO_DATE('{date}',  'DD-MON-YY HH24:MI:SS')"
    cursor.execute(query)
    connection.commit()
    bookings=cursor.fetchall()
    cursor.close()
    connection.close()
    return bookings

#update an existing booking
#same inputs as creating a booking with additional new timeslots to be updated to
def UpdateBooking(sname,bname,username,timeslot_start,timeslot_end, new_timeslot_start, new_timeslot_end, discount):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"""UPDATE bookings 
    SET sname='{sname}', bname='{bname}', username='{username}',
    timeslot_start=TO_DATE('{new_timeslot_start}', 'MON-DD-YYYY HH24:MI'), 
    timeslot_end=TO_DATE('{new_timeslot_end}', 'MON-DD-YYYY HH24:MI'))
    WHERE sname='{sname}', bname='{bname}', username='{username}',
    timeslot_start=TO_DATE('{timeslot_start}', 'MON-DD-YYYY HH24:MI'), 
    timeslot_end=TO_DATE('{timeslot_end}', 'MON-DD-YYYY HH24:MI'),{discount})"""
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return

def DeleteBooking(sname,bname,username,timeslot_start,timeslot_end, new_timeslot_start, new_timeslot_end):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"""DELETE FROM bookings 
    WHERE sname='{sname}', bname='{bname}', username='{username}',
    timeslot_start=TO_DATE('{timeslot_start}', 'MON-DD-YYYY HH24:MI'), 
    timeslot_end=TO_DATE('{timeslot_end}', 'MON-DD-YYYY HH24:MI'))"""
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return

def DeleteServiceBookings(bname):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"""DELETE FROM bookings WHERE bname='{bname}'"""
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return

#employee related tasks
#role is discrete 'Employee' or 'Administrator' 
def CreateEmployee(bname,username,password,efname,elname,role):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    hashed_passw=hashPass(password)
    query=f"INSERT INTO userlogin VALUES('{username}','{hashed_passw}','{role}')"
    query2=f"INSERT INTO employees VALUES('{username}','{efname}','{elname}','{bname}','{role}')"
    cursor.execute(query)
    cursor.execute(query2)
    connection.commit()
    cursor.close()
    connection.close()
    return

def UpdateEmployee(bname,username,efname,elname,role): 
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"UPDATE employees SET efname='{efname}', elname='{elname}', role='{role}' WHERE bname='{bname}' AND username='{username}'" 
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return

#returns all of a businesses employees for display
def CallBusinessEmployees(bname):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"SELECT * FROM employees WHERE bname='{bname}'"
    cursor.execute(query)
    connection.commit()
    fetch=cursor.fetchall()
    cursor.close()
    connection.close()
    return fetch

def CallEmployeeInfo(name):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    #calls a specific business' info from the database
    query=f"SELECT * FROM employees WHERE username='{name}'"
    cursor.execute(query)
    connection.commit()
    #store result so we can close db connection
    val=cursor.fetchone()
    cursor.close()
    connection.close()
    #returns the first (and expectedly only) row
    return val

#this function is dangerous, be very careful with implementation it should only be called on a visible delete button tied into background checking systems, like a user's profile page
def DeleteAccount(username):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"DELETE FROM userlogin WHERE username='{username}'"
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return

#geocoordinate stuff

def AddCoordinates(username,lat,lng):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"INSERT INTO geocoordinates VALUES('{username}',{lat},{lng})"
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return

def CheckCoordinates(username):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"SELECT lat,lng FROM geocoordinates WHERE username='{username}'"
    cursor.execute(query)
    connection.commit()
    coords=cursor.fetchone()
    cursor.close()
    connection.close()
    return coords

def CheckCoordinatesUnbound(username,connection,cursor):
    query=f"SELECT lat,lng FROM geocoordinates WHERE username='{username}'"
    cursor.execute(query)
    connection.commit()
    coords=cursor.fetchone()
    return coords

#faster implementation of haversine calculating it locally rather than serverside
def CallBusinessGeo(Customerusername):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    coords=CheckCoordinates(Customerusername)
    query=f"""SELECT lat,lng,b.username, b.name
    From geocoordinates
    INNER JOIN businessinfo b ON geocoordinates.username=b.username"""
    cursor.execute(query)
    connection.commit()
    info=cursor.fetchall()
    i=0
    info2=[]
    #simple function that copies the rows produced via the query that result in distances less than 20 miles using haversine
    for entries in info:
        coords1=(info[i][0],info[i][1])
        dist=haversine(coords,coords1,unit='mi')
        if dist<20.0:
            info2.append(info[i])
        i=i+1
    cursor.close()
    connection.close()
    return info2




#used both for updating and creating descriptions for services
def UpdateDescription(sname,bname,description):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    #check if this row already exists
    query1=f"SELECT COUNT(*) FROM servicedescription WHERE bname='{bname}' AND sname='{sname}'"
    cursor.execute(query1)
    connection.commit()
    if bool(cursor.fetchone()[0]):
        #if the row exists merely update it otherwise insert new row
        query2=f"""UPDATE servicedescription 
            SET description={description} 
            WHERE bname='{bname}' AND sname='{sname}'"""
    else:
        query2=f"""INSERT INTO servicedescription VALUES('{sname}','{bname}','{description}')"""
    cursor.execute(query2)
    connection.commit()
    return

def GetDescription(sname,bname):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query1=f"SELECT description FROM servicedescription WHERE bname='{bname}' AND sname='{sname}'"
    cursor.execute(query1)
    connection.commit()
    desc=cursor.fetchone()
    cursor.close()
    connection.close()
    return desc

#reviews
#header limit of 100 chars
#body limit of 1,000 chars
#rating is from 0 to 10
def CreateReview(username,fname,lname,header,body,rating,bname,sname):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"INSERT INTO creviews (username,fname,lname,header,body,rating,bname,sname) VALUES('{username}','{fname}','{lname}','{header}','{body}',{rating},'{bname}','{sname}')"
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return

#allows editing of reviews via the unique id, should be used in tandem with getuserreviews
def editReview(id,header,body):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"UPDATE creviews SET header='{header}', body='{body}'WHERE id={id}"
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return

#returns a list of the ids of review created by a specific username
def getUserReviews(username):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"SELECT id FROM creviews WHERE username='{username}'"
    cursor.execute(query)
    connection.commit()
    rev=cursor.fetchall()
    cursor.close()
    connection.close()
    return rev

def getReviewScrollStart(amount,bname,sname,cursor,connection):
    query=f"SELECT * FROM creviews WHERE bname='{bname}' and sname='{sname}'"
    cursor.execute(query)
    connection.commit()
    rev=cursor.fetchmany(amount)
    return rev

def getReviewScrollContinue(amount,cursor,connection):
    return cursor.fetchmany(amount)

#gets a list of all reviews for a specific service
def getReviews(bname,sname):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"SELECT * FROM creviews WHERE bname='{bname}' and sname='{sname}'"
    cursor.execute(query)
    connection.commit()
    rev=cursor.fetchall()
    cursor.close()
    connection.close()
    return rev

#gets only the review ids, useful for responses
def getReviewIds(bname,sname):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"SELECT id FROM creviews WHERE bname='{bname}' and sname='{sname}'"
    cursor.execute(query)
    connection.commit()
    rev=cursor.fetchall()
    cursor.close()
    connection.close()
    return rev

#create a response to a review
#id is the id of the review being responded to, reference getreviews to get the id since it would have already been called to display the reviews
def CreateResponse(bname,id,body):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"INSERT INTO bresponse VALUES({id},{bname},'{body}')"
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return

#edits a reponse, should only be called when applicable as this doesn't check if you should be eligable to do so
def EditResponse(id,body):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"UPDATE bresponse SET body='{body}' WHERE id={id}"
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return

#gets the responses to reviews
def GetResponse(bname,sname):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"SELECT bresponse.name, bresponse.body FROM bresponse INNER JOIN creviews c ON refid=id WHERE c.bname='{bname}' AND c.sname='{sname}'"
    cursor.execute(query)
    connection.commit()
    res=cursor.fetchall()
    cursor.close()
    connection.close()
    return res