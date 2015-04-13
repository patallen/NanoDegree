from flask import Flask, render_template, request, url_for
from flask import redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


#Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


#Fake Menu Items
items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}


#####################################################
#              Routes for restaurants               #
#####################################################
@app.route('/')
@app.route('/restaurants/')
def viewRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('viewrestaurants.html', restaurants=restaurants)


@app.route('/restaurant/new/', methods=['GET', 'POST'])
def addRestaurant():
    if request.method=='POST':
        newRestaurant = Restaurant(name=request.form['restaurant_name'])
        session.add(newRestaurant)
        session.commit()
        return redirect(url_for('viewRestaurants'))
    return render_template('newrestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method=='POST':
        restaurant.name=request.form['restaurant_name']
        session.add(restaurant)
        session.commit()
        return redirect(url_for('viewRestaurants'))
    return render_template('editrestaurant.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method=='POST':
        itemsToDelete = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
        # Delete all menu itmes associated with this restaurant
        for i in itemsToDelete:
            session.delete(i)
        # Delete the restaurant
        session.delete(restaurant)
        session.commit()
        return redirect(url_for('viewRestaurants'))
    return render_template('deleterestaurant.html', restaurant=restaurant)


#####################################################
#              Routes for menu items                #
#####################################################
@app.route('/restaurant/<int:restaurant_id>/menu/')
def viewMenu(restaurant_id):
    return render_template('viewMenu.html', menuItems=items)


@app.route('/restaurant/<int:restaurant_id>/menu/new/')
def addMenuItem(restaurant_id):
    return render_template('newmenuitem.html', restaurant=restaurants[restaurant_id])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/')
def editMenuItem(restaurant_id, menu_id):
    return render_template('editmenuitem.html', item=item)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/')
def deleteMenuItem(restaurant_id, menu_id):
    return render_template('deletemenuitem.html', item=item)

if __name__ == '__main__':
    app.secret_key = 'SECRETKEY'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)