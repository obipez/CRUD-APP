from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, FoodItem

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
	open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Calorie Application"


engine = create_engine('sqlite:///foodlists.db', connect_args={'check_same_thread': False}, echo=True)

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
					for x in xrange(32))
	login_session['state'] = state
	return render_template('CRUDAlogin.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code
	code = request.data

	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(
			json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
		   % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
			json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is valid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's client ID does not match app's."), 401)
		print "Token's client ID does not match app's."
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_access_token = login_session.get('access_token')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'),
								 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use.
	login_session['access_token'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	print "done!"
	return output


@app.route('/gdisconnect')
def gdisconnect():
	access_token = login_session.get('access_token')
	if access_token is None:
		print 'Access Token is None'
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	print 'In gdisconnect access token is %s', access_token
	print 'User name is: '
	print login_session['username']
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	print 'result is '
	print result
	if result['status'] == '200':
		del login_session['access_token']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		response = make_response(json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response


@app.route('/')
@app.route('/home')
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


@app.route('/update/<id>', methods=["POST"])
def update(id):
	try:
		food = session.query(FoodItem).filter_by(id=id).first()
		if(request.form["title"]):
			food.name = request.form["title"]
		if(request.form["calories"]):
			food.calories = request.form["calories"]
		if(request.form["fat_cals"]):
			food.fat_cals = request.form["fat_cals"]
		if(request.form["total_fat"]):
			food.total_fat = request.form["total_fat"]
		if(request.form["saturated_fat"]):
			food.saturated_fat = request.form["saturated_fat"]
		if(request.form["trans_fat"]):
			food.trans_fat = request.form["trans_fat"]
		if(request.form["cholesterol"]):
			food.cholesterol = request.form["cholesterol"]
		if(request.form["sodium"]):
			food.sodium = request.form["sodium"]
		if(request.form["carbohydrates"]):
			food.carbohydrates = request.form["carbohydrates"]
		if(request.form["dietary_fiber"]):
			food.dietary_fiber = request.form["dietary_fiber"]
		if(request.form["sugars"]):
			food.sugars = request.form["sugars"]
		if(request.form["protein"]):
			food.protein = request.form["protein"]
		if(request.form["vitamin_a"]):
			food.vitamin_a = request.form["vitamin_a"]
		if(request.form["vitamin_c"]):
			food.vitamin_c = request.form["vitamin_c"]
		if(request.form["calcium"]):
			food.calcium = request.form["calcium"]
		if(request.form["iron"]):
			food.iron = request.form["iron"]
		session.add(food)
		session.commit()
	except Exception as e:
		print("Couldn't update food item.")
		print(e)
	return moreInfo(id)


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


# trackapi.nutritionix.com/v2

@app.route('/search', methods=["POST"])
def search():
	search = request.form['search']
	r = request.get(trackapi.nutritionix.com/v2/search)
	return search



if __name__ == "__main__":
  app.secret_key = 'super_secret_key'
  app.run(host='0.0.0.0', port=5000, debug=True)