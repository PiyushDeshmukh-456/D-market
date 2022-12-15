from flask import render_template, redirect, url_for, flash ,request,current_app,session
from market import db, app
from market.model import Item


def MagerDicts(dict1,dict2):
    if isinstance(dict1, list)and isinstance(dict2,list):
        return dict1+dict2
    elif isinstance(dict1,dict)and isinstance(dict2,dict):
            return dict(list(dict.items()) + list(dict2.items()))
    return False



@app.route('/addcart',methods=['POST'])
def AddCart():
    try:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        colors =request.form.get('colors')
        product = Item.query.filter_by(id=product_id).first()
        if product_id and quantity and colors and request.method == "POST":
            DictItems = {product_id:{'name': product.name, 'price':product.price, 'discount':product.discount, 'color':colors, 'quantity':quantity, 'image':product.image_1}}
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    print('This product is alredy in your cart')
                else:
                    session['Shoppingcart'] = MagerDicts(session['Shoppingcart'], DictItems)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)



@app.route('/carts')
def getCart():
    if 'Shoppingcart' not in session:
        return redirect(request.referrer)
    return render_template('carts.html')