from flask import Flask, request, jsonify, redirect, render_template, flash
from sqlalchemy.orm import Session
from models import User
from database import engine, SessionLocal, Base
import bcrypt

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Create database tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.route("/", methods=["GET"])
def home():
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db: Session = next(get_db())
        username = request.form["username"]
        password = request.form["password"]
        
        if db.query(User).filter(User.username == username).first():
            flash("Данный ник занят попробуйте другой.", "error")
            return render_template("register.html")
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        new_user = User(username=username, hashed_password=hashed_password.decode('utf-8'))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db: Session = next(get_db())
        username = request.form["username"]
        password = request.form["password"]
        
        user = db.query(User).filter(User.username == username).first()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            return render_template("suc.html")
        else:
            flash("Неправильный логин или пороль!", "error")
            return render_template("login.html")
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)