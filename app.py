from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response
import jwt
import datetime
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
users = {
    "testuser": "testpassword"
}

def generate_jwt(user_id):
    token = jwt.encode(
        {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        },
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    return token

def verify_jwt(token):
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return data['user_id']
    except:
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username] == password:
            token = generate_jwt(username)
            response = make_response(redirect(url_for('dashboard')))
            response.set_cookie('jwt_token', token)
            return response
        else:
            return 'Invalid Credentials', 401
    
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def dashboard():
    token = request.cookies.get('jwt_token')
    
    files = request.files.get('file')
    if not token:
        return 'Token is missing!', 403

    user_id = verify_jwt(token)
    if user_id:
        # return f'Welcome {user_id} to the dashboard!'
        if request.method == 'POST':
            file = request.files.get('file')

            if file:
                filename = file.filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                return f'File {filename} uploaded successfully to {filepath}'
        # else:
        return render_template('upload.html')    
    else:
        return 'Invalid or expired token!', 403

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('jwt_token')
    return response


if __name__ == '__main__':
    app.run(debug=True)
