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
            item = session.query(MenuItem).filter_by(id=i.id).one()
            session.delete(item)
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
    menuItems = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return render_template('viewMenu.html', restaurant_id=restaurant_id, menuItems=menuItems)


@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def addMenuItem(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        item_name = request.form['menu_item_name']
        item_price = request.form['menu_item_price']
        item_description = request.form['menu_item_desc']
        newMenuItem = MenuItem(name=item_name, price=item_price,
                               description=item_description,
                               restaurant_id=restaurant_id)
        session.add(newMenuItem)
        session.commit()
        return redirect(url_for('viewMenu', restaurant_id=restaurant_id))
    return render_template('newMenuItem.html', restaurant=restaurant)


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
