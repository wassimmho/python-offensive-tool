from flask import Flask, Response, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Needed for session management

# Simple in-memory "database"
users = {}

@app.route("/")
def home():
    if 'user' in session:
        return f"""
        <html>
            <head><title>Welcome</title></head>
            <body style="font-family: Arial; background: #f0f0f0; text-align:center; padding-top: 100px;">
                <h1>Welcome, {session['user']}!</h1>
                <p><a href='/logout'>Logout</a></p>
            </body>
        </html>
        """
    return redirect(url_for('signin'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    message = ""
    color = "red"

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email in users:
            message = "Account already exists!"
        else:
            hashed_password = generate_password_hash(password)
            users[email] = hashed_password
            message = "Account created successfully!"
            color = "green"

    return f"""
    <html>
        <head><title>Sign Up</title></head>
        <body style="font-family: Arial; background: #f0f0f0; display: flex; justify-content: center; align-items: center; height: 100vh;">
            <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); width: 300px;">
                <h2 style="text-align: center;">Sign Up</h2>
                <form method="POST">
                    <input type="email" name="email" placeholder="Email" required style="width:100%;padding:8px;margin:8px 0;border-radius:5px;border:1px solid #ccc;"><br>
                    <input type="password" name="password" placeholder="Password" required style="width:100%;padding:8px;margin:8px 0;border-radius:5px;border:1px solid #ccc;"><br>
                    <button type="submit" style="width:100%;padding:10px;background:#28a745;color:white;border:none;border-radius:5px;">Create Account</button>
                </form>
                <p style="text-align:center; color:{color};">{message}</p>
                <p style="text-align:center;">Already have an account? <a href="/signin">Sign In</a></p>
            </div>
        </body>
    </html>
    """

@app.route("/signin", methods=["GET", "POST"])
def signin():
    message = ""
    color = "red"

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email in users and check_password_hash(users[email], password):
            session['user'] = email
            return redirect(url_for('home'))
        else:
            message = "Invalid credentials, please try again."

    return f"""
    <html>
        <head><title>Sign In</title></head>
        <body style="font-family: Arial; background: #f0f0f0; display: flex; justify-content: center; align-items: center; height: 100vh;">
            <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); width: 300px;">
                <h2 style="text-align: center;">Sign In</h2>
                <form method="POST">
                    <input type="email" name="email" placeholder="Email" required style="width:100%;padding:8px;margin:8px 0;border-radius:5px;border:1px solid #ccc;"><br>
                    <input type="password" name="password" placeholder="Password" required style="width:100%;padding:8px;margin:8px 0;border-radius:5px;border:1px solid #ccc;"><br>
                    <button type="submit" style="width:100%;padding:10px;background:#007bff;color:white;border:none;border-radius:5px;">Sign In</button>
                </form>
                <p style="text-align:center; color:{color};">{message}</p>
                <p style="text-align:center;">Don't have an account? <a href="/signup">Sign Up</a></p>
            </div>
        </body>
    </html>
    """

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('signin'))

if __name__ == "__main__":
    app.run(debug=True)
