from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

# import CRUD Operations from database_setup.py
from database_setup import Base, FoodItem, FoodInfo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create session and connect to DB
engine = create_engine('sqlite:///foodlist.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            #Creating new food item page
            if self.path.endswith("/food_items/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Add a New Item</h1>"
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/food_items/new'>"
                output += "<input name = 'newFoodItem' type = 'text' placeholder = 'New Food Item' > "
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/food_items"):
                food_items = session.query(FoodItem).all()
                output = ""
                #link to create new item
                output += "<a href = '/food_items/new' > Add a New Item Here </a></br></br>"

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output += "<html><body>"
                for food_item in food_items:
                    output += food_item.name
                    output += "</br>"
                    #code to EDIT and DELETE links
                    output += "<a href ='#' >Edit </a> "
                    output += "</br>"
                    output += "<a href =' #'> Delete </a>"
                    output += "</br></br></br>"

                output += "</body></html>"
                self.wfile.write(output)
                return
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


    #POST method
    def do_POST(self):
        try:
            if self.path.endswith("/food_items/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newFoodItem')

                    # Create new Restaurant Object
                    newFoodItem = FoodItem(name=messagecontent[0])
                    session.add(newFoodItem)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/food_items')
                    self.end_headers()

        except:
            pass



def main():
    try:
        server = HTTPServer(('', 8080), webServerHandler)
        print 'Web server running...open localhost:8080/food_items in your browser'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()