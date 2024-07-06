from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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
        #not sure what this exactly does coppied from chatgpt
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/Bsignup', methods = ['GET','POST'])
def Bsignup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        address = request.form['address']
        return redirect(url_for('index'))
    
    return render_template('Bsignup.html')


@app.route('/Csignup', methods = ['GET','POST'])
def Csignup():
    if request.method == 'POST':
         username = request.form['username']
         password = request.form['password']
         businessname = request.form['business name']
         address = request.form['address']
         services = request.form['service offerings']
         return redirect(url_for('index'))
    
    return render_template('Csignup.html')

@app.route('/home')
def homePage():
    name = "Olivia"
    return render_template('Components/home.html', name = name)

@app.route('/profile')
def profilePage():

    return render_template('Components/profile.html')

@app.route('/business/view')
def businessViewProfilePage():
    businessName = "Publix"
    businessAddress = "123 Happy Street"


    return render_template('Components/bViewProfile.html', businessName = businessName, businessAddress=businessAddress)


if __name__ == '__main__':
    app.run(debug=True)