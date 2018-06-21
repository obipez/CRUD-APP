from flask import Flask
from flask import render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, FoodItem

app = Flask(__name__)

engine = create_engine('sqlite:///foodlists.db')
# Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# db = SQLAlchemy(app)
# class Food(db.Model):
# 	item = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
	
# 	def __repr__(self):
# 		return"<Foods: {}>".format(self.item)
		
# contents = session.query(FoodItem).all()
# session.delete(contents)
# session.commit()

@app.route('/')
@app.route('/home/')
def home():
	foods = session.query(FoodItem).all()
	return render_template("CRUD-App.html", foods=foods)


@app.route('/add', methods=["GET", "POST"])
def add():
	foods = None
	if request.form:
		try:
			food = FoodItem(
				name=request.form.get("title"), 
				calories=request.form.get("calories"), 
				fat_cals=request.form.get("fat_cals"), 
				total_fat=request.form.get("total_fat"),
				saturated_fat=request.form.get("saturated_fat"),
				trans_fat=request.form.get("trans_fat"),
				cholesterol=request.form.get("cholesterol"),
				sodium=request.form.get("sodium"),
				carbohydrates=request.form.get("carbohydrates"),
				dietary_fiber=request.form.get("dietary_fiber"),
				sugars=request.form.get("sugars"),
				protein=request.form.get("protein"),
				vitamin_a=request.form.get("vitamin_a"),
				vitamin_c=request.form.get("vitamin_c"),
				calcium=request.form.get("calcium"),
				iron=request.form.get("iron"))
			session.add(food)
			session.commit()
		except Exception as e:
			print("Failed to add food item.")
			print(e)
	return home()


@app.route('/update', methods=["POST"])
def update():
	try:
		newitem = request.form.get("newitem")
		olditem = request.form.get("olditem")
		food = session.query(FoodItem).filter_by(name=olditem).first()
		food.name = newitem
		session.commit()
	except Exception as e:
		print("Couldn't update food item.")
		print(e)
	return home()


@app.route('/delete', methods=["POST"])
def delete():
    name = request.form.get("item")
    food = session.query(FoodItem).filter_by(name=name).first()
    session.delete(food)
    session.commit()
    return home()


@app.route('/food_info/<id>', methods=["GET"])
def moreInfo(id):
	item = session.query(FoodItem).filter_by(id=id).first()
	return render_template('moreInfo.html', item=item)


@app.route('/addnew')
def addNew():
	return render_template('addNew.html')


if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000, debug=True)