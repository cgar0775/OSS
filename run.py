#imports
from flask import Flask, render_template, request, redirect, url_for
import oracledb
from database import OracleConfig
from dotenv import load_dotenv
#start flask
app = Flask(__name__)

#loading the env file
load_dotenv()

#global variable setup
# database= OracleConfig()



@app.route("/")
def hello_world():
    return render_template('splash.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':

        #handling login logic
        username = request.form['username']
        password = request.form['password']

        print("hi there")
        #This wont work... it will fail on the following line below
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/Bsignup', methods = ['GET','POST'])
def Bsignup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        businessname = request.form['business name']
        address = request.form['address']
        services = request.form['service offerings']
        return redirect(url_for('login'))
    
    return render_template('Bsignup.html')


@app.route('/Csignup', methods = ['GET','POST'])
def Csignup():
    if request.method == 'POST':
         username = request.form['username']
         password = request.form['password']
         address = request.form['address']
         return redirect(url_for('login'))
    
    return render_template('Csignup.html')

@app.route('/home')
def homePage():
    name = "Olivia"
    return render_template('home.html', name = name)

@app.route('/profile')
def profilePage():

    return render_template('Components/profile.html')

@app.route('/business/view')
def businessViewProfilePage():
    
    businessName = "Publix"
    businessAddress = "123 Happy Street"

    stars = "4"


    return render_template('templates/bProfile.html', businessName = businessName, businessAddress=businessAddress, stars=stars)

@app.route('/customer/view')
def customerViewProfilePage():

    return render_template('templates/cProfile.html')

if __name__ == '__main__':
    app.run(debug=True)