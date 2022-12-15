from email.mime import image
from email.policy import default
from enum import unique
from market import db, login_manager
from market import bcrypt
from datetime import datetime
from flask_login import UserMixin
import json

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=1000)
    items = db.relationship('Item', backref='owned_user', lazy=True)

    @property
    def password(self):
        return self.password
    # some oop here
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def can_purchase(self, item_obj):
        return self.budget >= item_obj.price

    def can_sell(self, item_obj):
        return item_obj in self.items

class Item(db.Model):
    __searchable_ = ['name','description']
    id=db.Column(db.Integer(),primary_key=True)
    name=db.Column(db.String(length=30), nullable=False, unique=True)
    price=db.Column(db.Integer(), nullable=False)
    discount=db.Column(db.Integer(), default=0)
    stock=db.Column(db.Integer(), nullable=False)
    colors=db.Column(db.Text(), nullable=False)
    description=db.Column(db.String(length=1084), nullable=False, unique=True)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

    brand_id = db.Column(db.Integer(), db.ForeignKey('brand.id'),nullable=False)
    brand = db.relationship('Brand',backref=db.backref('brands', lazy=True))

    category_id = db.Column(db.Integer(), db.ForeignKey('category.id'),nullable=False)
    category = db.relationship('Category',backref=db.backref('posts', lazy=True))

    image_1 =db.Column(db.String(150),nullable=False, default='image.jpg')
    image_2 =db.Column(db.String(150),nullable=False, default='image.jpg')
    image_3 =db.Column(db.String(150),nullable=False, default='image.jpg')
    
    def __repr__(self):
        return f'Item{self.name}'

    def buy(self, user):
        self.owner = user.id
        user = self.price
        db.session.commit()
        
    def sell(self, user):
        self.owner = None
        user.budget = self.price
        db.session.commit()


class Brand(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)


class Category(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)

        
db.create_all()
class jsonEncodedDict(db.TypeDecorator):
    impl = db.Text()
    def process_bind_param(self,value,dialect):
        if value is None:
            return '{}'
        else:
            return json.dumps(value)
    def process_result_value(self,value,dialect):
        if value is None:
            return {}
        else:
            return json.loads(value)
class CustomerOrder(db.Model):
    id=db.Column(db.Integer(), primary_key=True)
    invoice =db.Column(db.String(20), unique=True,nullable=False)
    status =db.Column(db.String(20), default='Pending',nullable=False)
    customer_id =db.Column(db.Integer(), unique=False,nullable=False)
    date_created =db.Column(db.String(20), default=datetime.utcnow,nullable=False)
    orders =db.Column(jsonEncodedDict)
    def __repr__(self):
        return'<CustomerOrder %r>' % self.invoice
db.create_all()