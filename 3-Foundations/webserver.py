from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from database_setup import Restaurant, MenuItem, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>Hello!</body></html>"
                output += """<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message'
                type='text'><input type='submit' value='Submit'></form>"""
                output += "</body></html>"

                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>&#161Hola!</h1>"
                output += """<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message'
                type='text'><input type='submit' value='Submit'></form>"""
                output += "</body></html>"

                self.wfile.write(output)
                print output
                return
            
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                restaurants = session.query(Restaurant).all()

                output = ""
                output += "<html><body>"
                output += '<a href="/restaurants/new">Add Restaurant</a><br>'
                for restaurant in restaurants:
                    output += '<br>%s<br>' % restaurant.name
                    output += '<a href="/restaurants/%s/edit">Edit</a><br>' % restaurant.id
                    output += '<a href="/restaurants/%s/delete">Delete</a></br>' % restaurant.id
                
                output += "</body></html>"

                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += """
                <form method='POST' enctype='multipart/form-data' action='/restaurants/new'>
                <input name='restaurant_name' type='text'><input type='submit' value='Create'></form>"""
                
                output += "</body></html>"

                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/edit"):
                restaurant_id = self.path.split("/")[2]
                restaurantName = session.query(Restaurant).filter_by(id=restaurant_id).one()
                if restaurantName != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    output = ""
                    output += "<html><body>"
                    output += "<h1>Rename <em>%s</em><h1>" % restaurantName.name
                    output += """
                    <form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>
                    <input name='restaurant_rename' type='text'><input type='submit' value='Create'></form>""" % restaurantName.id
                    
                    output += "</body></html>"

                    self.wfile.write(output)
                    print output
                    return

            if self.path.endswith("/delete"):
                restaurant_id = self.path.split("/")[2]
                restaurantName = session.query(Restaurant).filter_by(id=restaurant_id).one()
                if restaurantName != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    output = ""
                    output += "<html><body>"
                    output += "<h1>Delete: <em>%s</em>?<h1>" % restaurantName.name
                    output += """
                    <form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>
                    <input type='submit' value='Delete'></form>""" % restaurantName.id
                    
                    output += "</body></html>"

                    self.wfile.write(output)
                    print output
                    return


        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            '''
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields=cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')

            output = ""
            output += "<html><body>"
            output += "<h2> Okay, how about this: </h2>"
            output += "<h1> %s </h1>" % messagecontent[0]

            output += """<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message'
                type='text'><input type='submit' value='Submit'></form>"""
            output += "</body></html>"
            self.wfile.write(output)
            print output
            '''

            if self.path.endswith("/restaurants/new"):
                
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype =='multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('restaurant_name')

                newRestaurant = Restaurant(name = messagecontent[0])
                session.add(newRestaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/edit"):
                restaurant_id = self.path.split("/")[2]


                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype =='multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('restaurant_rename')
                
                restaurantRename = session.query(Restaurant).filter_by(id=restaurant_id).one()
                restaurantRename.name = messagecontent[0]
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()


            if self.path.endswith("/delete"):
                restaurant_id = self.path.split("/")[2]
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                restaurantRename = session.query(Restaurant).filter_by(id=restaurant_id).one()

                if restaurantRename != []:
                    session.delete(restaurantRename)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

        except:
            pass

        

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print('Web server running on port %s' % port)
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C entered, stopping web server...')
        server.socket.close()


if __name__ == '__main__':
    main()
