from flask import Flask, render_template, request, url_for
from flask import redirect, flash, jsonify

app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Restaurant, MenuItem, User
from flask import session as login_session
import random, string, requests

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
from flask import make_response

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME="Restaurant Menu Application"


engine = create_engine('sqlite:///restaurantmenuwith.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#####################################################
#              Routes for auth                      #
#####################################################
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():

    # Validate state token
    if request.args.get('state') != login_session['state']:
        print "request.args.get('state') = %s" % request.args.get('state')
        print "login_session['state'] = %s" % login_session['state']
        response = make_response(json.dumps('Invalidz state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        print result.get('error')
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if the user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connectd.'), 200)
        response.headers['Content-Type'] = 'application.json'
    
    # Store the access token in the session for later use
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json'}

    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id 

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    return output
    
@app.route('/gdisconnect/')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response('Current user not connected.', 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return reponse


#####################################################
#              Routes for restaurants               #
#####################################################
@app.route('/')
@app.route('/restaurants/')
def viewRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/restaurant/new/', methods=['GET', 'POST'])
def addRestaurant():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newRestaurant = Restaurant(name=request.form['restaurant_name'], user_id=login_session['user_id'])
        session.add(newRestaurant)
        session.commit()
        flash('Restaurant created successufully')
        return redirect(url_for('viewRestaurants'))
    return render_template('newrestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        restaurant.name = request.form['restaurant_name']
        session.add(restaurant)
        session.commit()
        flash('Restaurant edited successufully')
        return redirect(url_for('viewRestaurants'))
    return render_template('editrestaurant.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
   
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        itemsToDelete = session.query(MenuItem).filter_by(
            restaurant_id=restaurant.id)
        # Delete all menu itmes associated with this restaurant
        for i in itemsToDelete:
            item = session.query(MenuItem).filter_by(id=i.id).one()
            session.delete(item)
        # Delete the restaurant
        session.delete(restaurant)
        session.commit()
        flash('Restaurant and its menu items deleted successufully')
        return redirect(url_for('viewRestaurants'))
    return render_template('deleterestaurant.html', restaurant=restaurant)


#####################################################
#              Routes for menu items                #
#####################################################
@app.route('/restaurant/<int:restaurant_id>/menu/')
def viewMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menuItems = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    if restaurant.user_id != login_session['user_id']:
        return render_template('publicmenu.html', restaurant=restaurant, menuItems=menuItems)
    return render_template('menu.html', restaurant=restaurant, menuItems=menuItems)


@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def addMenuItem(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        item_name = request.form['menu_item_name']
        item_price = request.form['menu_item_price']
        item_description = request.form['menu_item_desc']
        newmenuitem = MenuItem(name=item_name, price=item_price,
                               description=item_description,
                               restaurant_id=restaurant_id,
                               user_id=login_session['user_id'])
        session.add(newmenuitem)
        session.commit()
        flash('Menu item created successufully')
        return redirect(url_for('viewMenu', restaurant_id=restaurant_id))
    return render_template('newMenuItem.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        menuItem.name = request.form['menu_item_name']
        menuItem.price = request.form['menu_item_price']
        menuItem.description = request.form['menu_item_desc']
        session.add(menuItem)
        session.commit()
        flash('Menu item edited successufully')
        return redirect(url_for('viewMenu', restaurant_id=restaurant_id))
    return render_template('editMenuItem.html', item=menuItem)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(menuItem)
        flash('Menu item deleted successufully')
        return redirect(url_for('viewMenu', restaurant_id=restaurant_id))

    return render_template('deleteMenuItem.html', item=menuItem)


#####################################################
#              Routes for JSON endpoints            #
#####################################################
@app.route('/restaurants/JSON/')
def viewRestaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurant=[r.serialize for r in restaurants])


@app.route('/restaurant/<int:restaurant_id>/menu/JSON/')
def viewMenuJSON(restaurant_id):
    menuItems = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItem=[i.serialize for i in menuItems])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def viewMenuItemJSON(restaurant_id, menu_id):
    menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=menuItem.serialize)


def createUser(login_session):
    newUser = User(name = login_session['username'],
                   email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = 'SECRETKEY'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
