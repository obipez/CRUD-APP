from flask import Flask
from flask import render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, FoodItem, FoodInfo

app = Flask(__name__)

engine = create_engine('sqlite:///foodlist.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

db = SQLAlchemy(app)
class Food(db.Model):
	item = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
	
	def __repr__(self):
		return"<Food: {}>".format(self.item)
		

@app.route('/', methods=["GET", "POST"])
def home():
	foods = None
	if request.form:
		try:
			food = Food(item=request.form.get("item"))
			db.session.add(food)
			db.session.commit()
		except Exception as e:
			print("Failed to add food item.")
			print(e)
	foods = Food.query.all()
	return render_template("CRUD-App.html", foods=foods)


@app.route("/update", methods=["POST"])
def update():
	try:
		newitem = request.form.get("newitem")
		olditem = request.form.get("olditem")
		food = Food.query.filter_by(item=olditem).first()
		food.item = newitem
		db.session.commit()
	except Exception as e:
		print("Couldn't update food item.")
		print(e)
	return redirect("/")


@app.route("/delete", methods=["POST"])
def delete():
    item = request.form.get("item")
    food = Food.query.filter_by(item=item).first()
    db.session.delete(item)
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000, debug=True)
