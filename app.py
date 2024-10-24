from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    users = [
        {"manager": "Oren Nahzabi", "name": "Sebastien Atemnkeng", "title": "Senior DevOps Engineer"},
        {"manager": "Oren Nahzabi", "name": "John Doe", "title": "DevOps Engineer"},
        {"manager": "Oren Nahzabi", "name": "Jane Smith", "title": "Junior DevOps Engineer"},
        {"manager": "Oren Nahzabi", "name": "Priscille", "title": "Senior Account Executive"},
        {"manager": "Oren Nahzabi", "name": "Motopamba", "title": "Senior Java Developer"}
    ]
    return render_template('users.html', users=users)

# Do not include the following block when using Waitress
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8000)
