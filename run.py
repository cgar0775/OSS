from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route('/login', methods = ['GET','POST'])

def login():
    if request.method == 'POST':

        #handling login logic
        username = request.form['username']
        password = request.form['password']
        #not sure what this exactly does coppied from chatgpt
        return redirect(url_for('index'))
    
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)