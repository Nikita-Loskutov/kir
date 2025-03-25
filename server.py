from flask import Flask, request, jsonify, redirect, render_template, flash
from sqlalchemy.orm import Session
from models import User
from database import engine, SessionLocal, Base
import bcrypt
from flask_mail import Mail, Message
import random
import string

app = Flask(__name__)
app.secret_key = 'supersecretkey'



# Конфигурация Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.yandex.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'lnikitaloskutov@yandex.ru'
app.config['MAIL_PASSWORD'] = 'fejsotogoqcawyzx'
app.config['MAIL_DEFAULT_SENDER'] = 'lnikitaloskutov@yandex.ru'

mail = Mail(app)


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
        email = request.form["email"]
        password = request.form["password"]
        
        if db.query(User).filter(User.username == username).first():
            flash("Данный ник занят попробуйте другой.", "error")
            return render_template("register.html")
        
        if db.query(User).filter(User.email == email).first():
            flash("Данный email уже зарегистрирован.", "error")
            return render_template("register.html")
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        new_user = User(username=username, email=email, hashed_password=hashed_password.decode('utf-8'))
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
            return render_template("index.html")
        else:
            flash("Неправильный логин или пороль!", "error")
            return render_template("login.html")
    return render_template("login.html")

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        db: Session = next(get_db())
        email = request.form["email"]
        
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))  # Генерация случайного пароля из 8 символов
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            user.hashed_password = hashed_password.decode('utf-8')
            db.commit()
            
            # Отправка email с новым паролем
            msg = Message('Восстановление пароля', recipients=[email])
            msg.body = f"Ваш новый пароль: {new_password}"
            mail.send(msg)
            
            flash("Новый пароль отправлен на ваш email.", "success")
            return redirect("/login")
        else:
            flash("Email не найден.", "error")
            return render_template("reset_password.html")
    return render_template("reset_password.html")

if __name__ == "__main__":
    app.run(debug=True)