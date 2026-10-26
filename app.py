import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Модели БД ---
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    starting_price = db.Column(db.Integer, nullable=False)
    current_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Активен')
    bids = db.relationship('Bid', backref='car', lazy=True)

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    bidder_name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Маршруты ---
@app.route('/')
def index():
    cars = Car.query.all()
    return render_template('index.html', cars=cars)

@app.route('/add_car', methods=['POST'])
def add_car():
    brand = request.form.get('brand')
    model = request.form.get('model')
    year = int(request.form.get('year'))
    price = int(request.form.get('price'))
    
    new_car = Car(brand=brand, model=model, year=year, starting_price=price, current_price=price)
    db.session.add(new_car)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/bid/<int:car_id>', methods=['POST'])
def make_bid(car_id):
    car = Car.query.get_or_404(car_id)
    bidder = request.form.get('bidder_name')
    amount = int(request.form.get('amount'))
    
    # Ставка должна быть больше текущей
    if amount > car.current_price:
        car.current_price = amount
        new_bid = Bid(car_id=car.id, bidder_name=bidder, amount=amount)
        db.session.add(new_bid)
        db.session.commit()
        
    return redirect(url_for('index'))

@app.route('/close_auction/<int:car_id>')
def close_auction(car_id):
    car = Car.query.get_or_404(car_id)
    car.status = 'Продан'
    db.session.commit()
    return redirect(url_for('index'))

# Инициализация БД
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)