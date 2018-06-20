# import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
# from flask import Flask
# from flask import render_template, request, redirect
# from flask_sqlalchemy import SQLAlchemy

# project_dir = os.path.dirname(os.path.abspath(__file__))
# database_file = "sqlite:///{}".format(os.path.join(project_dir, "foodDB.db"))

class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/hello"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output ++ "<html><body>Hello!</body></html>"
				self.wfile.write(output)
				print output
				return

		except IOError:
			self.send_error(404, "File Not Found %s" % self.path)


def main():
	try:
		port = 8080
		server = HTTPServer(('',port), webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()


	except KeyboardInterrupt:
		print "^C entered, stopping web server..."
		server.socket.close()

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = database_file

# db = SQLAlchemy(app)
# class Food(db.Model):
# 	item = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
	
# 	def __repr__(self):
# 		return"<Food: {}>".format(self.item)
		

# @app.route('/', methods=["GET", "POST"])
# def home():
# 	foods = None
# 	if request.form:
# 		try:
# 			food = Food(item=request.form.get("item"))
# 			db.session.add(food)
# 			db.session.commit()
# 		except Exception as e:
# 			print("Failed to add food item.")
# 			print(e)
# 	foods = Food.query.all()
# 	return render_template("CRUD-App.html", foods=foods)


# @app.route("/update", methods=["POST"])
# def update():
# 	try:
# 		newitem = request.form.get("newitem")
# 		olditem = request.form.get("olditem")
# 		food = Food.query.filter_by(item=olditem).first()
# 		food.item = newitem
# 		db.session.commit()
# 	except Exception as e:
# 		print("Couldn't update food item.")
# 		print(e)
# 	return redirect("/")


# @app.route("/delete", methods=["POST"])
# def delete():
#     item = request.form.get("item")
#     food = Food.query.filter_by(item=item).first()
#     db.session.delete(item)
#     db.session.commit()
#     return redirect("/")


if __name__ == "__main__":
	main()
	# app.run(host='0.0.0.0', port=5000, debug=True)