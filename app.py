from flask import Flask, render_template, json, request, session, flash, jsonify, redirect, url_for
from flask_mysqldb import MySQL
import pymysql
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from contextlib import closing
from form import RegisterForm, CommentForm
import bcrypt
import re
import math
from datetime import date

app = Flask(__name__)

app.secret_key = 'dev'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:akdldptmzbdpf1@@localhost:3306/book_db" 
app.config['SQLALCHEMY_POOL_SIZE'] = 1
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db = SQLAlchemy(app)
# db.init_app(app)
# migrate = Migrate(app, db)
# migrate.init_app(app, db)

db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)


from model import *

    
@app.route("/")
def main():
	form = RegisterForm()
	if 'log_in' in session:
		page = request.args.get('page', type=int, default=1)
		books_info = Book.query.paginate(page, per_page=8 ,error_out=False)

		db.session.close()
		return render_template('main.html', books_info = books_info)
	else:
		return render_template('login.html', form= form)

@app.route("/login",  methods=['POST'])
def login():

	if 'log_in' in session:
		return redirect(url_for('main'))

	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']

		password = password.encode('utf-8')
		username = User.query.filter_by(email = email).first()
		if username is None:
			flash('이메일과 비밀번호를 다시 입력해주세요.')	
			return redirect(url_for('main')) 
			
		check_password = bcrypt.checkpw(password, username.password.encode('utf-8'))

		if username is not None and check_password:
			session['log_in'] = True
			session['email'] = email
			session['username'] = username.username
			db.session.close()

			return redirect(url_for('main'))

		flash('이메일과 비밀번호를 다시 입력해주세요.')	
		return redirect(url_for('main'))

@app.route("/logout",methods=['GET']) # POST는 필요없다.
def logout():
	session.pop('log_in', None)
	return redirect(url_for('main'))

@app.route("/register", methods=['GET','POST']) # wiki 11_22_5 정규식의 문자 클래스 참고
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		username = form.data.get('username')
		email = form.data.get('email')
		password = form.data.get('password')
		repassword = form.data.get('password_2')
		usernames = '^[가-힣|a-z|A-Z]+$'
		n = re.compile(usernames)
		is_username = n.search(username)

		if is_username is None:
			flash('이름은 한글과 영문만 가능합니다.')
			return render_template('register.html', form = form)

		if len(password) < 8:
			flash('password는 8자 이상이여야합니다.')
			return render_template('register.html', form = form)

		#\d는 10진수를 찾습니다. 많은 다른 문자 집합의 10진수뿐만 아니라 표준 10진수 0-9를 포함하는 \p{Nd} 정규식 패턴과 동일합니다.
		numbers = '\d'
		m = re.compile(numbers)
		is_number = m.search(password)
	
		if is_number is None:
			
			flash('숫자가 포함되어야합니다.')
			return render_template('register.html', form = form)

		#\W는 비단어 문자를 찾습니다. \W 언어 요소는 다음 문자 클래스에 해당합니다.
		#[^\p{Ll}\p{Lu}\p{Lt}\p{Lo}\p{Nd}\p{Pc}\p{Lm}]
		specials = '\W'
		w = re.compile(specials)
		is_special = w.search(password)


		if is_special is None:

			flash('비밀번호에 특수문자가 포함되어야합니다.')
			return render_template('register.html', form = form)
		
  
		if password != repassword:
			flash('비밀번호가 일치하지 않습니다.')
			return render_template('register.html', form = form)


		user = User.query.filter_by(email=email).first()
		if user:
			flash('이미 존재하는 유저입니다.')
			return render_template('register.html', form = form)
		
  
		password = (bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())).decode('utf-8')
		query = User(username, email, password)
		
		
		db.session.add(query)
		db.session.commit()
		db.session.close()
  
		flash('첫 방문을 환영합니다!')  
		return render_template('login.html', form = form)
	
	return 	render_template('register.html', form = form)



@app.route("/book-info/<int:bookId>", methods=['GET','POST'])
def detail(bookId):
	logform = RegisterForm()
	if 'log_in' in session:
		form = CommentForm()
		books_info = Book.query.filter(Book.id == bookId).all()
		total_comment = Comment.query.filter_by(book_id = bookId).order_by(Comment.id.desc()).all()
		customer= User.query.filter_by(email = session['email']).first()

		review = []

		for i in total_comment:
			customer = User.query.filter_by(id = i.customer_id).first()
			review.append([customer.username, i.content, i.rate])

		db.session.close()
		return render_template('book_info.html', books_info=books_info, form=form, comments = review)
	else:
		return render_template('login.html', form=logform)


@app.route("/rent-book/<int:bookId>") 
def rent(bookId):
	logform = RegisterForm()
	if 'log_in' in session:
		customer= User.query.filter_by(email = session['email']).first()
		query = RentBook(bookId, customer.id, date.today().isoformat())
		book_query = Book.query.filter_by(id = bookId).first()
		check_duplicattion = RentBook.query.filter(customer.id == RentBook.customer_id, RentBook.book_id == bookId).all()

		if book_query.stock > 0:
			if not check_duplicattion:
				book_query.stock -= 1

				db.session.add(query)
				db.session.add(book_query)
				db.session.commit()
				db.session.close()
			else:

				flash('이미 대여중입니다.')
				return redirect(url_for('main') + f'?page={math.ceil(bookId / 8)}')
		else:
			flash('재고가 없습니다.')
			return redirect(url_for('main') + f'?page={math.ceil(bookId / 8)}')

		return redirect(url_for('main') + f'?page={math.ceil(bookId / 8)}')

	else:
		return render_template('login.html', form=logform)


@app.route("/rent-log")
def rent_log():
	logform = RegisterForm()
	if 'log_in' in session:
		customer= User.query.filter_by(email = session['email']).first()
		rent_log = CheckInBook.query.filter(customer.id == CheckInBook.customer_id).all()
		rented_book = []
		date = []
		img = []
		
		for i in rent_log:
			rented_book.append(Book.query.filter(Book.id == i.book_id).all())
			date.append([i.rent_date, i.return_date])

		rented_book = sum(rented_book, [])

		for i in rented_book:
			img.append(i.id)

		db.session.close()
		return render_template('rental_log.html', books_info = rented_book, date=date, img=img)
	else:
		return render_template('login.html', form=logform)


@app.route("/checkin")
def checkin():
	logform = RegisterForm()
	if 'log_in' in session:
		customer= User.query.filter_by(email = session['email']).first()
		rent_log = RentBook.query.filter(customer.id == RentBook.customer_id).all()
		rented_book = []
		date = []
		img = []

		for i in rent_log:
			rented_book.append(Book.query.filter(Book.id == i.book_id).all())
			date.append([i.rent_date, i.return_date])

		rented_book = sum(rented_book, [])

		for i in rented_book:
			img.append(i.id)
	
		db.session.close()
		return render_template('checkin.html', books_info = rented_book, date=date, img=img)
	
	else:
		return render_template('login.html', form=logform)


@app.route("/checkin-book/<int:bookId>")
def checkin_book(bookId):
	customer= User.query.filter_by(email = session['email']).first()
	return_book = RentBook.query.filter(RentBook.customer_id == customer.id, RentBook.book_id == bookId).order_by(RentBook.id.desc()).first()
	left_log = CheckInBook(bookId, customer.id, return_book.rent_date, date.today().isoformat())

	db.session.add(left_log)
	db.session.delete(return_book)
	db.session.commit()
	db.session.close()

	book_query = Book.query.filter_by(id = bookId).first()
	book_query.stock += 1

	db.session.add(book_query)
	db.session.commit()
	db.session.close()

	return redirect(url_for('checkin'))


@app.route("/comment/<int:bookId>",  methods=['POST'])
def comment(bookId):
	form = CommentForm()
	customer= User.query.filter_by(email = session['email']).first()
	books_info = Book.query.filter(Book.id == bookId).all()
	total_comment = Comment.query.filter_by(book_id = bookId)
	book_rate = books_info[0]
	writed = Comment.query.filter_by(customer_id = customer.id, book_id = bookId).first()

	if request.method == 'POST':
		cc = form.data.get('content')
		rate = request.form['total']

		if writed:
			flash('댓글은 1개만 입력 가능합니다.')
			return redirect(url_for('detail', bookId=bookId))

		if len(cc) > 0 and rate != '' and writed == None:
			review = Comment(bookId, customer.id, cc, int(rate))
			db.session.add(review)

			total_rate = 0
			for i in total_comment:
				total_rate += int(i.rate)

			rate_avg = int(total_rate / len(total_comment.all()))
			book_rate.rate = rate_avg

			db.session.add(book_rate)
			db.session.commit()
			db.session.close()
		else:
			flash('점수를 평가해 주세요')
			return redirect(url_for('detail', bookId=bookId))
	
	return redirect(url_for('detail', bookId=bookId))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)