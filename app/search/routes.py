import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

from app.apiauthhelper import token_required
from .forms import IceCreamSearchForm
from app.models import Icecream, User, db
from .YelpAPI import API_KEY

search = Blueprint('search', __name__, template_folder='searchtemplates')

ENDPOINT = "https://api.yelp.com/v3/businesses/search"
API_AUTH = {'Authorization': 'bearer %s' % API_KEY}

@search.route('/search', methods=["GET", "POST"])
def searchIceCream():
    form = IceCreamSearchForm()
    my_dict = {}
    saved = False
    if request.method == "POST":
        print('Post request made.')
        if form.validate():
            location = form.location.data

            # Define the parameters
            PARAMETERS = {
                'location': location,
                'categories': 'icecream,gelato, All',
                'radius': 10000,
                'open_now': True,
                'sort_by': 'best_match'
            }
            res = requests.get(url = ENDPOINT, params=PARAMETERS, headers=API_AUTH)
            if res.ok:
                yelp_data = res.json()
                for each in yelp_data['businesses']:
                    my_dict = {
                        'name': each['name'],
                        'rating': each['rating'],
                        'address': each['location']['address1'],
                        'img_url': each['image_url'],
                        'website': each['url']
                    }
                try:
                    shops = Icecream.query.filter_by(name=my_dict['name']).first()
                    if not shops:
                        shops = Icecream(my_dict['name'], my_dict['rating'], my_dict['address'], my_dict['img_url'], my_dict['website'])
                        shops.save()
                    if current_user.shop.filter_by(name=shops.name).first():
                        saved = True
                except KeyError:
                    flash("Sorry, we couldn't find anything for this location!", 'danger')
            else:
                flash("Sorry, we couldn't find anything for this location!", 'danger')
    return render_template('icecreamsearch.html', form=form, shops=my_dict, saved=saved)


@search.route('/saved', methods=["GET","POST"])
def savedShops():
    shops = current_user.shop.all()
    return render_template('savedshops.html', shops=shops)

# save ice cream shops
@search.route('/save/<string:icecream_name>')
def saveIceCream(icecream_name):
    current_user
    shops = Icecream.query.filter_by(name=icecream_name).first()
    current_user.shop.append(shops)
    db.session.commit()
    return redirect(url_for('search.savedShops'))

# remove
@search.route('/remove/<string:icecream_name>')
def removeIceCream(icecream_name):
    shops = Icecream.query.filter_by(name=icecream_name).first()
    current_user.shop.remove(shops)
    db.session.commit()
    return redirect(url_for('search.savedShops'))


######### API ##########
@search.route('/api/search', methods=["POST"])
def apiSearch():
    form = IceCreamSearchForm()
    my_dict = {}
    saved = False
    if request.method == "POST":
        print('Post request made.')
        if form.validate():
            location = form.location.data

            # Define the parameters
            PARAMETERS = {
                'location': location,
                'categories': 'icecream',
                'limit': 50,
                'radius': 10000
            }
            res = requests.get(url = ENDPOINT, params=PARAMETERS, headers=API_AUTH)
            if res.ok:
                yelp_data = res.json()
                for each in yelp_data['businesses']:
                    my_dict = {
                        'name': each['name'],
                        'rating': each['rating'],
                        'address': each['location']['address1'],
                        'img_url': each['image_url'],
                        'website': each['url']
                    }
                shops = Icecream.query.filter_by(name=my_dict['name']).first()
                if not shops:
                    shops = Icecream(my_dict['name'], my_dict['rating'], my_dict['address'], my_dict['img_url'], my_dict['website'])
                    shops.save()
                if current_user.shop.filter_by(name=shops.name).first():
                    saved = True
    return {
        'status': 'ok',
        'message': 'search completed!'
    }

@search.route('/api/shops', methods=["POST"])
@token_required
def getShops(user):
    return {
        'status': 'ok',
        'shop': [p.to_dict() for p in user.getShops()]
    }

@search.route('/api/shops/save', methods=["POST"])
@token_required
def saveShop(user):
    data = request.json

    icecream_id = data['icecreamId']
    icecream = Icecream.query.get(icecream_id)

    user.saveShops(icecream)
    return {
        'status': 'ok',
        'message': 'Saved shop!'
    }

@search.route('/api/shops/remove', methods=["POST"])
@token_required
def removeShop(user):
    data = request.json
    icecream_id = data['icecreamId']
    icecream = Icecream.query.get(icecream_id)

    user.removeShops(icecream)
    return {
        'status': 'ok',
        'message': 'Shop removed!'
    }