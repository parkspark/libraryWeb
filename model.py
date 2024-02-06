from app import db
from sqlalchemy.orm import relationship
#mysql workbench 로 확인하자

class User(db.Model):
    
    __tablename__ = 'customer'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    
    def __init__(self, username, email, password ):
        self.username = username
        self.email = email
        self.password = password

class Book(db.Model):
    __tablename__ = 'book'

    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.Text(), nullable=False)
    publisher = db.Column(db.Text(), nullable=False)
    author = db.Column(db.String(20), nullable=False)
    publication_date = db.Column(db.Date, nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    isbn = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    link = db.Column(db.Text(), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Integer, nullable=False)

    def __init__(self, stock, rate):
        self.stock = stock
        self.rate = rate
    
class RentBook(db.Model):
    __tablename__ = 'rental_book'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    rent_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)

    def __init__(self, book_id, customer_id, rent_date):
        self.book_id = book_id
        self.customer_id = customer_id
        self.rent_date = rent_date

class CheckInBook(db.Model):
    __tablename__ = 'check_in_book'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    rent_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=False)

    def __init__(self, book_id, customer_id, rent_date, return_date):
        self.book_id = book_id
        self.customer_id = customer_id
        self.rent_date = rent_date
        self.return_date = return_date


class Comment(db.Model):

    __tablename__ = 'comment'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    content = db.Column(db.Text)
    rate = db.Column(db.Integer)     

    def __init__(self, book_id, customer_id, content, rate):
        self.book_id = book_id
        self.customer_id = customer_id
        self.content = content
        self.rate = rate