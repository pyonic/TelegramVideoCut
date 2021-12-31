import sqlite3
conn = sqlite3.connect('main.db', check_same_thread=False)


def get_sponsor():
	global conn
	cur = conn.cursor()
	fetch = cur.execute("SELECT channel_id,channel_link FROM chanel WHERE id = 1").fetchall()
	return fetch
def query(queryset, commit = False):
	""" Direct queryset to DB """
	global conn
	cur = conn.cursor()
	result = cur.execute(queryset)
	if commit:
		conn.commit()
	return result.fetchall()

def user_exist(uid):
	""" Check if user alredy in DB """
	check_user = query(f'SELECT id FROM users WHERE uid = {uid}')
	if len(check_user) == 0:
		return False
	else:
		return True
def get_users_count():
	create_user = query(f'SELECT COUNT(id) FROM users')
	return create_user[0][0]
def insert_user(uid):
	""" Insert new user into DB """
	create_user = query(f'INSERT INTO users(uid) VALUES({uid})', True)
	return True
def update_lang(uid, language):
	create_user = query(f'UPDATE users SET lang = "{language}" WHERE uid={uid}', True)
	return True
def get_language(uid):
	lang = query(f'SELECT lang FROM users WHERE uid = {uid}')
	return lang
def user_ordered(uid):
	""" Function checks if user alredy made any orders or not """
	check_user = query(f'SELECT ordered FROM users WHERE uid = {uid}')
	if check_user[0][0] == "0":
		return False
	else:
		return True
def user_made_order(uid):
	check_user = query(f'UPDATE users SET ordered = 1 WHERE uid = {uid}', True)
def get_users():
	users = query('SELECT uid FROM users WHERE id > 0')
	return users
def order_completed(uid):
	query(f'UPDATE users SET ordered = 0 WHERE uid = {uid}', True)
def get_que_number():
	global conn
	cur = conn.cursor()
	fetch = cur.execute("SELECT COUNT(id) FROM orders WHERE done = 0").fetchall()
	return fetch

def new_order(author_id,target_link):
	""" Function creates new order """
	global conn
	que_number = int(get_que_number()[0][0]) + 1
	cur = conn.cursor()
	query = f'INSERT INTO orders(author_id,done,que_order,target) VALUES({author_id},0, {que_number},"{target_link}")'
	cur.execute(query)
	conn.commit()
	return True
def order_done(author_id):
	global conn
	que_number = int(get_que_number()[0][0]) + 1
	cur = conn.cursor()
	query = f'UPDATE orders SET done = 1 WHERE author_id = {author_id}'
	cur.execute(query)
	conn.commit()
	return True