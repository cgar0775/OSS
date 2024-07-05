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


if __name__ == '__main__':
    app.run(debug=True)