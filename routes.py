from flask import render_template, redirect, url_for, flash ,request,current_app,session,make_response
from market import db, app, photos,search
from market.model import Item, User, Brand, Category,Item,CustomerOrder
from market.forms import RegisterForm, LoginForm, SellItemForm,Addproduct
import secrets, os
from flask_login import login_user, logout_user, login_required, current_user
import os
import stripe
publishable_key='pk_test_51LrkN1FmofwIkEuxYGiim62qX2RTMzqPPr0pemDgprVCJk0YjUPurFFgXG1AwvPdHP0daREbLQIE3SULYgS7XOSc000AhexQof'
                 
stripe.api_key='sk_test_51LrkN1FmofwIkEux3ZKCrwfmSjT4jQjU9qkWmXdr0F5IWoNnodvPOg5AIyl4TJq2wZ7loE9FnSXU9vEIDy9JAZgu00s9OQKXFt'
                


@app.route('/payment', methods=['GET','POST'])
@login_required
def payment():
    invoice = request.form.get('invoice')
    amount = request.form.get('amount')
    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken'],
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        description=Item.description,
        amount=amount,
        currency='usd',
    )
    orders = CustomerOrder.query.filter_by(customer_id=current_user.id,charge=charge,invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status='Paid'
    db.session.commit()
    return redirect(url_for('thank'))


@app.route('/thanks')
def thanks():
    return render_template('thank.html')


@ app.route ('/')
@ app.route('/home')
def home_page ():
    return render_template ('home.html')
@ app.route('/index')
def main_page():
    page = request.args.get('page',1,type=int)
    item = Item.query.filter(Item.stock > 0).order_by(Item.id.desc()).paginate(page=page, per_page=8)
    brands = Brand.query.join(Item,(Brand.id==Item.brand_id)).all()
    categories = Category.query.join(Item,(Category.id==Item.category_id)).all()
    return render_template('index.html', item=item, brands=brands, categories=categories)


@app.route('/product/<int:id>')
def single_page(id):
    product=Item.query.get_or_404(id)
    brands = Brand.query.join(Item,(Brand.id==Item.brand_id)).all()
    categories = Category.query.join(Item,(Category.id==Item.category_id)).all()
    return render_template('single_page.html', product=product, brands=brands, categories=categories)





@app.route('/brand/<int:id>')
def get_brand(id):
    get_b = Brand.query.filter_by(id=id).first_or_404()
    page = request.args.get('page',1, type=int)
    brand = Item.query.filter_by(brand=get_b).paginate(page=page, per_page=6)
    brands = Brand.query.join(Item,(Brand.id==Item.brand_id)).all()
    categories = Category.query.join(Item,(Category.id==Item.category_id)).all()
    return render_template('index.html', brand=brand, brands=brands, categories=categories,get_b=get_b)

@app.route('/categories/<int:id>')
def get_category(id):
    page = request.args.get('page',1,type=int)
    get_cat=Category.query.filter_by(id=id).first_or_404()
    get_cat_prod = Item.query.filter_by(category=get_cat).paginate(page=page, per_page=4)
    brands = Brand.query.join(Item,(Brand.id==Item.brand_id)).all()
    categories = Category.query.join(Item,(Category.id==Item.category_id)).all()
    return render_template('index.html',get_cat_prod=get_cat_prod,brands=brands,categories=categories,get_cat=get_cat)




@ app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    brands = Brand.query.join(Item,(Brand.id==Item.brand_id)).all()
    categories = Category.query.join(Item,(Category.id==Item.category_id)).all()
    selling_form = SellItemForm()
    if request.method == "POST":
        # purchasing item
        purchased_item = request.form.get("purchased_item")
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Thank You for purchased this item {p_item_object.name} for {p_item_object.price}₹", category='success')
        # selling item
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"Congratulations! You sold {s_item_object.name} back to market!", category='success')
        return redirect(url_for('market_page'))

    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, owned_items=owned_items, selling_form=selling_form, brands=brands,categories=categories)




@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('main_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)



@ app.route("/addbrand", methods=['GET','POST'])
def addbrand():
    if request.method=="POST":
        getbrand = request.form.get('brand')
        brand = Brand(name=getbrand)
        db.session.add(brand)
        flash(f'The Brand {getbrand} was added to your database','success')
        db.session.commit()
        return redirect(url_for('addbrand'))
    return render_template('addbrand.html',brands='brands')


@ app.route("/addcat", methods=['GET','POST'])
def addcat():
    if request.method=="POST":
        getbrand = request.form.get('category')
        cat = Category(name=getbrand)
        db.session.add(cat)
        flash(f'The Category {getbrand} was added to your database','success')
        db.session.commit()
        return redirect(url_for('addbrand'))
    return render_template('addbrand.html',)

@app.route('/updatecat/<int:id>',methods=['GET','POST'])
def updatecat(id):
    updatecat = Category.query.get_or_404(id)
    category = request.form.get('category')  
    if request.method =="POST":
        updatecat.name = category
        flash(f'The category {updatecat.name} was changed to {category}','success')
        db.session.commit()
        return redirect(url_for('categories'))
    category = updatecat.name
    return render_template('updatebrand.html', title='Update cat',updatecat=updatecat)


    



@app.route('/deletecategory/<int:id>', methods=['POST'])
def deletecategory(id):
    category = Category.query.get_or_404(id)
    if request.method=="POST":
        db.session.delete(category)
        db.session.commit()
        flash(f"The category {category.name} was deleted from your database","success")
        return redirect(url_for('market_page'))
    flash(f"The brand {category.name} can't be  deleted from your database","warning")
    return redirect(url_for('market_page'))



@ app.route('/addproduct',methods=['POST','GET'])
def addproduct():
    brands = Brand.query.all()
    categories = Category.query.all()
    form = Addproduct(request.form)
    if request.method=="POST":
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        colors = form.colors.data
        description = form.description.data
        brand = request.form.get('brand')
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        addproduct = Item(name=name,price=price,discount=discount,stock=stock,colors=colors,description=description,category_id=category,brand_id=brand,image_1=image_1,image_2=image_2,image_3=image_3)
        db.session.add(addproduct)
        flash(f'The product {name} was added in database','success')
        db.session.commit()
        return redirect(url_for('main_page'))
    return render_template('addproduct.html', title="Add Product Page", form=form, brands=brands, categories=categories)

@app.route('/updatebrand/<int:id>',methods=['GET','POST'])
def updatebrand(id):
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method =="POST":
        updatebrand.name = brand
        flash(f'The brand {updatebrand.name} was changed to {brand}','success')
        db.session.commit()
        return redirect(url_for('brands'))
    brand = updatebrand.name
    return render_template('updatebrand.html', title='Update brand',brands='brands',updatebrand=updatebrand)


@app.route('/deletebrand/<int:id>', methods=['POST'])
def deletebrand(id):
    brand = Brand.query.get_or_404(id)
    if request.method=="POST":
        db.session.delete(brand)
        db.session.commit()
        flash(f"The brand {brand.name} was deleted from your database","success")
        return redirect(url_for('market_page'))
    flash(f"The brand {brand.name} can't be  deleted from your database","warning")
    return redirect(url_for('main_page'))



@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        #if the user is exist
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You Are Logged In: {attempted_user.username}', category='success')
            return redirect(url_for('main_page'))
        else:
            flash('Username And Password are not match! Please Try Again', category='danger')

    return render_template('login.html', form=form)


@app.route('/brands/<int:id>')
def brands(id):
    brands = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('brands.html', title='brands',brands=brands)




@app.route('/categories')
def categories():
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('brands.html', title='categories',categories=categories)


@ app.route('/logout')
def logout_page():
    logout_user()
    flash("You Have Been Logged out!", category='info')
    return redirect(url_for("home_page"))

def updateshoppingcart():
    for _key, product in session['Shoppingcart'].items():
        session.modified =True
        del product['image']
        del product['colors']
    return updateshoppingcart()

@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        try:
            order =CustomerOrder(invoice=invoice,customer_id=customer_id,orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash(f'Your order has been sent','success')
            return redirect(url_for('orders',invoice=invoice))
        except Exception as e:
            print(e)
            flash(f'something went wrong while get order', 'danger')
            return redirect(url_for('getCart'))

@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandTotal=0
        subTotal=0
        customer_id = current_user.id
        customer = User.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id,invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (product['discount']/100) * float(product['price'])
            subTotal += float(product['price']) * int(product['quantity'])
            subTotal -= discount
            tax = ("%.2f" % (.06 * float(subTotal)))
            grandTotal = ("%.2f" % (1.06 * float(subTotal)))
    else:
        return redirect(url_for('login_page'))
    return render_template('order.html',invoice=invoice,tax=tax,subTotal=subTotal,grandTotal=grandTotal,custome=customer,orders=orders)





@app.route('/updateproduct/<int:id>', methods=['GET','POST'])
def updateproduct(id):
    brands = Brand.query.all()
    categories = Category.query.all()
    product = Item.query.get_or_404(id)
    brand =request.form.get('brand')
    category = request.form.get('category')
    form = Addproduct(request.form)
    if request.method == 'POST':
        product.name = form.name.data 
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data 
        product.colors = form.colors.data
        product.description = form.description.data
        product.category_id=category
        product.brand_id = brand
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        db.session.commit()
        flash(f'your product is updated','success')
        return redirect(url_for("market_page"))
    form.name.data = product.name
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.description.data = product.description
    form.colors.data = product.colors



    
    return render_template('updateproduct.html', form=form, product=product, brands=brands,categories=categories)


@ app.route('/deleteitem/<int:id>',methods=['POST'])
def deleteitem(id) :
    product=Addproduct.query.get_or_404(id)
    if request.method == "POST":
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
            except Exception as e:
                print(e)

        db.session.delete(product)
        db.session.commit()
        flash(f'The product {product.name} was delete form your record','success')
        return redirect(url_for('market_page'))
    flash(f'Cant delete the product','danger')
    return redirect(url_for('market_page'))



