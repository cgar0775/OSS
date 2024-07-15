#this file contains functions for database calls for various functions
import os
import oracledb
import hashlib
from database import OracleConfig
from dotenv import load_dotenv

load_dotenv()
#setup the database connection
database= OracleConfig()

def hashPass(passw):
    #establish db connection
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    #hashing the password
    encoded_pass=passw.encode()
    hash_object=hashlib.sha384(encoded_pass)
    hashed_passw=hash_object.hexdigest()
    return hashed_passw

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

def CreateCustomerAcc(username,password,firstname,lastname,country,state,city,address,email):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    hashed_passw=hashPass(password)
    #fill the two tables needed
    query=f"INSERT INTO userlogin VALUES('{username}','{hashed_passw}')"
    query2=f"INSERT INTO CUSTOMERINFO VALUES('{username}','{firstname}','{lastname}','{country}','{state}','{city}','{address}','{email}')"
    #execute the database calls
    print(query)
    cursor.execute(query)
    cursor.execute(query2)
    connection.commit()
    #close db connection for space
    cursor.close()
    connection.close()
    #end func
    return

def CreateBusinessAcc(username,password,name,country,state,city,address,email):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    hashed_passw=hashPass(password)
    #fill the two tables needed
    query=f"INSERT INTO userlogin VALUES('{username}','{hashed_passw}')"
    query2=f"INSERT INTO BUSINESSINFO VALUES('{name}','{email}','{country}','{state}','{city}','{address}','{username}')"
    #execute the database calls
    cursor.execute(query)
    cursor.execute(query2)
    connection.commit()
    #close db connection for space
    cursor.close()
    connection.close()
    #end func
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
def CreateService(bname,sname,price,slots):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"INSERT INTO services VALUES('{bname}','{sname}',{price},{slots})"  
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
            SET opentime=TO_DATE('JAN-01-2002 {opentime}', 'MON-DD-YYYY HH24:MI'), 
                closetime=TO_DATE('JAN-01-2002 {closetime}', 'MON-DD-YYYY HH24:MI'),
                breakstart=TO_DATE('JAN-01-2002 {breakstart}', 'MON-DD-YYYY HH24:MI'),
                breakend=TO_DATE('JAN-01-2002 {breakend}', 'MON-DD-YYYY HH24:MI') 
            WHERE bname='{bname}' AND sname='{sname}' AND weekday='{weekday}'"""
    else:
        query2=f"""INSERT INTO servicehours 
        VALUES('{sname}','{bname}','{weekday}',
            TO_DATE('JAN-01-2002 {opentime}', 'MON-DD-YYYY HH24:MI'),
            TO_DATE('JAN-01-2002 {closetime}', 'MON-DD-YYYY HH24:MI'),
            TO_DATE('JAN-01-2002 {breakstart}', 'MON-DD-YYYY HH24:MI'),
            TO_DATE('JAN-01-2002 {breakend}', 'MON-DD-YYYY HH24:MI'))"""
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
    return services

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
    return service
#create booking
#inputs service name (sname), businessname (bname), username of the customer, timeslot_start the time and date of the start of the service, timeslot_end the ending time and date of the service
#both are in the format of MON-DD-YYYY HH:MM that being MON=3 letter shortening of the year Jan Feb etc, DD day 01,25 etc, YYYY the full year 2024 etc, HH:MM the time in 24 hour standard 09:30 for 9:30 AM
def CreateBooking(sname,bname,username,timeslot_start,timeslot_end):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"INSERT INTO bookings VALUES('{sname}','{bname}','{username}',TO_DATE('{timeslot_start}', 'MON-DD-YYYY HH24:MI'),TO_DATE('{timeslot_end}', 'MON-DD-YYYY HH24:MI'))"
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

#update an existing booking
#same inputs as creating a booking with additional new timeslots to be updated to
def UpdateBooking(sname,bname,username,timeslot_start,timeslot_end, new_timeslot_start, new_timeslot_end):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    query=f"""UPDATE bookings 
    SET sname='{sname}', bname='{bname}', username='{username}',
    timeslot_start=TO_DATE('{new_timeslot_start}', 'MON-DD-YYYY HH24:MI'), 
    timeslot_end=TO_DATE('{new_timeslot_end}', 'MON-DD-YYYY HH24:MI'))
    WHERE sname='{sname}', bname='{bname}', username='{username}',
    timeslot_start=TO_DATE('{timeslot_start}', 'MON-DD-YYYY HH24:MI'), 
    timeslot_end=TO_DATE('{timeslot_end}', 'MON-DD-YYYY HH24:MI'))"""
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    return