from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from item_catalog_set_up import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from flask import Flask, render_template,\
    request, redirect, jsonify, url_for, flash

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"


engine = create_engine('sqlite:///items_catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    request.get_data()
    code = request.data.decode('utf-8')

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
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

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
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
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
    output += """
    style = "width: 300px;
             height: 300px;
             border-radius: 150px;
             -webkit-border-radius: 150px;
             -moz-border-radius: 150px;">
            """
    flash("you are now logged in as %s" % login_session['username'])
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
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


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
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
        response = make_response(
            json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/category')
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Items Information
# route to jsonify categories.
@app.route('/category/JSON')
def categoriesJSON():
    """
        Show list of categories in JSON format
        takes no arguments
        returns a list of JSONFIED ctegories
    """
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# route to jsonify item.
@app.route('/category/<int:category_id>/items/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    """
        Show item detail of specific category in JSON format
        takes as argument: category_id and item_id
        returns the specified JSONFIED item
    """
    item = session.query(Item).filter_by(
        id=item_id, category_id=category_id).one()
    return jsonify(item=item.serialize)


# route to jsonify list of items.
@app.route('/category/<int:category_id>/items/JSON')
def itemsJSON(category_id):
    """
        Show list of items of specific category in JSON format
        takes as argument: category_id
        returns the specified JSONFIED list of items
    """
    items = session.query(Item).filter_by(
        category_id=category_id).all()
    return jsonify(items=[i.serialize for i in items])


# route to jsonify all catalog data.
@app.route('/catalog/JSON')
def catalogJSON():
    """
        Show list of categories with its list of items in JSON format
        takes no arguments
        returns JSONFIED list of categories and its items.
    """
    categories = session.query(Category).all()
    categoryJSON = [c.serialize for c in categories]
    for c in range(len(categoryJSON)):
        items = [i.serialize for i in session.query(Item).filter_by(
            category_id=categoryJSON[c]["id"]).all()]
        if items:
            categoryJSON[c]["i"] = items
    return jsonify(Category=categoryJSON)


# route to list all categories
@app.route('/')
@app.route('/category/')
def showCategories():
    """
        Show list of categories in the home page
        takes no arguments
        returns:
            user not logged in?
            public home page shows up with the list of categories.
            user logged in?
            home page with addition option shows up
            with the list of categories.
    """
    user = True
    if 'username' not in login_session:
        user = False
    categories = session.query(Category).all()
    items_limited = session.query(Item).order_by(Item.id.desc()).limit(8)
    items = items_limited[::1]
    return render_template('home.html',
                               categories=categories, items=items,user=user)


# route to list specific category items
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/items/')
def showItems(category_id):
    """
        Show items list of specific category
        takes category_id as argument
        returns:
            user logged in?
            show home page with the specified list of items.
    """
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template(
        'home.html',
        items=items,
        categories=categories,
        selected_category=category)


# route to show item details
@app.route('/category/<int:category_id>/items/<int:item_id>')
def showItem(category_id, item_id):
    """
        Show item details data
        takes category_id and item_id as arguments
        returns:
            user logged in? the owner of this item?
            shows item detail with the ability to modify it
            user logged in? not the owner of this item?
            shows item detail without the ability to modify it
    """
    user = True
    creator = True
    if 'username' not in login_session:
        user = False
        creator = False
    item = session.query(Item).filter_by(
            category_id=category_id,
            id=item_id).one()
    if item.user_id != login_session['user_id']:
        creator = False
    return render_template('item.html', item=item,user=user,creator=creator)


# route to create a new item
@app.route('/category/new/', methods=['GET', 'POST'])
def newItem():
    """
        creates new item
        takes no arguments
        returns:
            GET : returns form for adding new item.
            POST: reads form data and add it to the DB.
    """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        category = session.query(Category).filter_by(
            name=request.form['category']).one()
        newItem = Item(
                    name=request.form['name'],
                    description=request.form['description'],
                    category=category,
                    user_id=login_session['user_id'])
        session.add(newItem)
        flash('New Item %s Successfully Created' % newItem.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        categories = session.query(Category).all()
        return render_template('newItem.html', categories=categories)


# route to edit an item
@app.route('/category/<int:category_id>/items/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(item_id, category_id):
    """
        idits an item
        takes item_id and its category_id as argument
        returns:
            GET : returns form for editin the item.
            POST: reads form data and update the DB.
    """
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(
                category_id=category_id,
                id=item_id).one()

    if request.method == 'POST':
        if (request.form['name'] and
                request.form['description'] and
                request.form['category']):
            category = session.query(Category).filter_by(
                name=request.form['category']).one()
            editedItem.name = request.form['name']
            editedItem.description = request.form['description']
            editedItem.category = category
            session.add(editedItem)
            flash('Category Successfully Edited %s' % editedItem.name)
            session.commit()
            return redirect(url_for('showCategories'))
    else:
        if editedItem.user_id != login_session['user_id']:
            return redirect(url_for('showCategories'))
        categories = session.query(Category).all()
        return render_template('editItem.html',
                               item=editedItem,
                               categories=categories)


# route to delete an item
@app.route('/category/<int:category_id>/items/<int:item_id>/delete/',
           methods=['POST'])
def deleteItem(item_id, category_id):
    """
        delete an item
        takes item_id and its category_id as argument
        returns:
            POST: takes the item id and delete it from DB.
    """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        itemtToDelete = session.query(Item).filter_by(id=item_id).one()
        if itemtToDelete.user_id != login_session['user_id']:
            return redirect(url_for('showCategories'))
        session.delete(itemtToDelete)
        flash('%s Successfully Deleted' % itemtToDelete.name)
        session.commit()
        return redirect(url_for('showCategories', item_id=item_id))


if __name__ == '__main__':
    app.secret_key = '_0Envh5BXSTjIk5QNDzDM8WQ'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
