#this file contains functions for database calls for various functions
import os
import oracledb
import hashlib
from database import OracleConfig

#setup the database connection
database=OracleConfig

def hashPass(passw):
    #establish db connection
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    #hashing the password
    encoded_pass=passw.encode()
    hash_object=hashlib.Sha384(encoded_pass)
    hashed_passw=hash_object.hexdigest()
    return hashed_passw

def loginCheck(user,passw):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    #hash the password
    hashed_passw=hashPass(passw)
    #define the query for checking login
    query= f"SELECT COUNT(*) FROM userlogin where username='{user}' AND password='{hashed_passw}';"
    #check
    cursor.execute(query)
    cursor.commit()
    check=cursor.fetchone()[0]
    cursor.close()
    return bool(check) 

def CreateCustomerAcc(username,password,firstname,lastname,country,state,city,address,email):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    hashed_passw=hashPass(password)
    #fill the two tables needed
    query=f"INSERT INTO userlogin VALUES('{username}','{hashed_passw})"
    query2=f"INSERT INTO CUSTOMERINFO VALUES('{username}','{firstname}','{lastname}','{country}','{state}','{city}','{address}','{email}')"
    #execute the database calls
    cursor.execute(query)
    cursor.execute(query2)
    cursor.commit()
    #close db connection for space
    cursor.close()
    #end func
    #testing purposes erase later
    print("done")
    return

def CreateBusinessAcc(username,password,name,country,state,city,address,email):
    connection=oracledb.connect(user=database.username, password=database.password, dsn=database.connection_string)
    cursor=connection.cursor()
    hashed_passw=hashPass(password)
    #fill the two tables needed
    query=f"INSERT INTO userlogin VALUES('{username}','{hashed_passw})"
    query2=f"INSERT INTO BUSINESSINFO VALUES('{name}','{country}','{state}','{city}','{address}','{email}','{username}')"
    #execute the database calls
    cursor.execute(query)
    cursor.execute(query2)
    cursor.commit()
    #close db connection for space
    cursor.close()
    #end func
    #testing purposes erase later
    print("done")
    return