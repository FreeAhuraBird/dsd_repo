from flask import Flask, render_template, request, redirect, url_for, session
#from Flask_session import Session
from flaskext.mysql import MySQL
from datetime import datetime, timedelta
import os, uuid, pprint, random, datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure MySQL
app.config['MYSQL_DATABASE_USER'] = 'art@%'
app.config['MYSQL_DATABASE_PASSWORD'] = 'superbra'
app.config['MYSQL_DATABASE_DB'] = 'art_database'
app.config['MYSQL_DATABASE_HOST'] = '85.230.109.96'

app.config['UPLOAD_PATH'] = 'static/img'

mysql = MySQL(app)

# functions
def get_userID_from_email(email):
    conn = mysql.connect()
    cursor = conn.cursor()

    query = "SELECT UserID FROM Users WHERE Email = %s"
    cursor.execute(query, (email,))
    return cursor.fetchall()

def get_logged_in_user_id():
    return session.get('user_id', None)

def get_user_data(email):
    conn = mysql.connect()
    cursor = conn.cursor()

    query = "SELECT * FROM Users WHERE email = %s"
    cursor.execute(query, (email,))
    user_data = cursor.fetchall()
    return user_data

def get_user_list(userid):
    conn = mysql.connect()
    cursor = conn.cursor()

    query = "SELECT ListID FROM Lists WHERE UserID = %s"
    cursor.execute(query, (userid,))
    list_data = cursor.fetchall()
    return list_data[0][0]

def get_list_data(listid):
    conn = mysql.connect()
    cursor = conn.cursor()

    query = "SELECT Title FROM Lists WHERE ListID = %s"
    cursor.execute(query, (listid,))
    list_data = cursor.fetchall()
    return list_data

def get_new_listid():
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(ListID) FROM Lists")
    max_listid = cursor.fetchone()[0]
    new_listid = max_listid + 1
    print("newlistID:", new_listid)
    return new_listid

def get_new_userid():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(UserID) FROM Users")
    max_listitemID = cursor.fetchall()[-1]
    return max_listitemID + 1

def get_new_ListItemID():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(ListItemID) FROM ListItem")
    list_itemid_data = cursor.fetchall()[0][0]
    print(list_itemid_data)
    max_listitemID = list_itemid_data + 1
    print("Max listitemID:", max_listitemID)
    return max_listitemID

def get_column_data(column_name, table):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute(f"SELECT {column_name} FROM {table}")
    return cursor.fetchall()

def reserve_item_for_user(item_id, user_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        # Check if the item is available
        cursor.execute("SELECT * FROM Items WHERE ItemID = %s AND ReservedUntil IS NULL", (item_id,))
        item_data = cursor.fetchone()

        if item_data:
            # Update the item to be reserved for the user
            reserved_until = datetime.now() + timedelta(minutes=10)
            cursor.execute("UPDATE Items SET ReservedBy = %s, ReservedUntil = %s WHERE ItemID = %s",
                           (user_id, reserved_until, item_id))
            conn.commit()
            return True
        else:
            return False

    except Exception as e:
        print(str(e))
        return False
    finally:
        cursor.close()
        conn.close()

# routes
@app.route('/')
def index():
    if 'email' in session:
        return redirect(url_for("home"))
    
    if request.method == 'POST':
        username = request.form['signup-username']
        password = request.form['signup-password']
        email = request.form['signup-email']
        color = request.form.get('color', 'beige')
        print(username, password, email, color)

    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['signup-username']
        password = request.form['signup-password']
        email = request.form['signup-email']
        color = request.form.get('color', 'beige')
        file = request.files['profile-picture']
        print(username, password, email, color)
        all_emails = get_column_data("Email", "Users")
        print(all_emails)

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        else:
            filename = 'cat_placeholder.jpg'
            
        for emails in all_emails:
            for email_ in emails:
                print(email_)
                if email_ == email:
                    print(f"{email_} exists")
                    return render_template('index.html', existing_email=True)
        
        # what is this? vvv
        userid = get_new_listid()
        print(userid)
        # Store user data in MySQL database
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            # Insert user into Users table
            cursor.execute("INSERT INTO Users (UserID, Username, Password, Email, Profile_Picture) VALUES (%s, %s, %s, %s, %s)",
                           (userid, username, password, email, filename))

            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for("login"))
        
        except Exception as e:
            return str(e)

@app.route('/login', methods=['GET','POST'])
def login():
    if 'email' in session:
        user_email = session.get('email')
        user_data = get_user_data(user_email)
        profile_pic = user_data[0][5]
        print(profile_pic)
        #user_id = get_logged_in_user_id()
        return redirect(url_for("profile"))
    
    if request.method == 'POST':
        email = request.form['login-email']
        password = request.form['login-password']
        print(email, password)
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            # Check if the provided credentials are valid
            cursor.execute("SELECT * FROM Users WHERE Email = %s AND Password = %s", (email, password))
            user_data = cursor.fetchone()
            print(user_data)
            print(user_data)
            if user_data != None:
                session['email'] = email
                return redirect(url_for('home'))
            else:
                return render_template('login.html', invalid_password=True)

        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            conn.close()

    else:  # For GET requests
        return render_template('login.html')
    
@app.route('/upload_profilepic', methods=['POST'])
def upload_profilepic():
    file = request.files['file']

    if file:
        if 'email' in session:
            user_email = session.get('email')

            filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1] #get new filename
            conn = mysql.connect()
            cursor = conn.cursor()

            sql = "UPDATE Users SET Profile_Picture = %s WHERE email = %s"
            cursor.execute(sql, (filename, user_email)) # store only the filename in the database

            conn.commit()
            cursor.close()
            conn.close()

            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), app.config['UPLOAD_PATH'], filename)
            file.save(file_path) # upload new file
        
    return redirect(url_for('profile'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'email' not in session:
        return redirect(url_for('index'))
    user_email = session.get('email')
    user_id = get_userID_from_email(user_email)
    user_data = get_user_data(user_email)
    description = user_data[0][-1]
    user_name = user_data[0][1]
    profile_pic = user_data[0][5]
    if user_data[0][4] is not None:
        description = user_data[0][4]
    print(profile_pic)
    pprint.pprint(user_data)

    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Lists WHERE UserID = %s", (user_id))
        lists_data = [dict((cursor.description[i][0], value) 
                      for i, value in enumerate(row)) for row in cursor.fetchall()]
        pprint.pprint(lists_data)
        

    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()

    return render_template('profile.html', description=description, user_name=user_name, profile_pic=profile_pic, lists_data=lists_data)

@app.route('/settings')
def settings():
    if 'email' not in session:
        return redirect(url_for('index'))
    user_email = session.get('email')
    user_id = get_userID_from_email(user_email)
    user_data = get_user_data(user_email)
    description = user_data[0][-1]
    user_name = user_data[0][1]
    profile_pic = user_data[0][5]
    if user_data[0][4] is not None:
        description = user_data[0][4]
    print(profile_pic)
    pprint.pprint(user_data)

    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        # Fetch some sample data for illustration purposes
        cursor.execute("SELECT * FROM Lists WHERE UserID = %s", (user_id))
        lists_data = [dict((cursor.description[i][0], value) 
                      for i, value in enumerate(row)) for row in cursor.fetchall()]
        pprint.pprint(lists_data)
        

    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()

    #must add description to sent variables
    return render_template('settings.html', description=description, user_name=user_name, profile_pic=profile_pic, lists_data=lists_data)

@app.route('/change_username', methods=['POST'])
def change_username():
    new_username = request.form['new_username']

    if new_username:
        if 'email' in session:
            user_email = session.get('email')

            try:
                conn = mysql.connect()
                cursor = conn.cursor()

                sql = "UPDATE Users SET Username = %s WHERE email = %s"
                cursor.execute(sql, (new_username, user_email))

                conn.commit()

            except Exception as e:
                return str(e)
            finally:
                cursor.close()
                conn.close()

    return redirect(url_for('settings'))
            
@app.route('/change_password', methods=['POST'])
def change_password():
    new_password = request.form['new_password']

    if new_password:
        if 'email' in session:
            user_email = session.get('email')

            try:
                conn = mysql.connect()
                cursor = conn.cursor()

                sql = "UPDATE Users SET Password = %s WHERE email = %s"
                cursor.execute(sql, (new_password, user_email))

                conn.commit()

            except Exception as e:
                return str(e)
            finally:
                cursor.close()
                conn.close()
        
    return redirect(url_for('settings'))

@app.route('/change_description', methods=['POST'])
def change_description():
    new_description = request.form['new_description']

    if new_description:
        if 'email' in session:
            user_email = session.get('email')

            try:
                conn = mysql.connect()
                cursor = conn.cursor()

                sql = "UPDATE Users SET Description = %s WHERE email = %s"
                cursor.execute(sql, (new_description, user_email))

                conn.commit()

            except Exception as e:
                return str(e)
            finally:
                cursor.close()
                conn.close()

    return redirect(url_for('settings'))

@app.route('/create_board', methods=['GET', 'POST'])
def board():
    if request.method == 'POST':
        title = request.form['board-title']
        description = request.form['board-descrption']
        print(title, description)
        user_email = session.get('email')
        user_id = get_userID_from_email(user_email)
        new_listid = get_new_listid()
        current_time = datetime.datetime.now()
        creationdate = f"{current_time.year}-{current_time.month}-{current_time.day}"
        print(creationdate)
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO Lists (ListID, UserID, Title, Description, CreationDate) VALUES (%s, %s, %s, %s, %s)",
                    (new_listid, user_id, title, description, creationdate))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("profile"))
    else:
        user_email = session.get('email')
        user_id = get_userID_from_email(user_email)
        user_data = get_user_data(user_email)
        description = user_data[0][-1]
        user_name = user_data[0][1]
        profile_pic = user_data[0][5]
        print(profile_pic)

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            # Fetch some sample data for illustration purposes
            cursor.execute("SELECT * FROM Lists WHERE UserID = %s", (user_id))
            lists_data = [dict((cursor.description[i][0], value) 
                        for i, value in enumerate(row)) for row in cursor.fetchall()]
            pprint.pprint(lists_data)

        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            conn.close()

        return render_template('create_board.html', description=description, user_name=user_name, profile_pic=profile_pic, lists_data=lists_data)

@app.route('/upload_art', methods=['POST'])
def upload_art():
    pass

@app.route('/remove_board', methods=['POST'])
def remove_board():
    list_id = request.args.get('list_id')
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        sql = "DELETE FROM Lists WHERE ListID = %s"
        cursor.execute(sql, (list_id,))

        conn.commit()

    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('profile'))

@app.route('/add_item', methods = ['GET', 'POST'])
def add_item():
    # Issue with this code: You cannot choose which list you want to put
    # the item in. This should be handeled in frontend
    if 'email' not in session:
        return redirect(url_for('index'))
    user_email = session.get('email')
    user_id = get_userID_from_email(user_email)
    item_id = request.args.get('item_id')
    redirection = request.args.get('page')
    print("itemID:", item_id)
    list_id = get_user_list(user_id)
    
    # skaffa en lista från användarens 
    listitem_id = get_new_ListItemID()
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        print(listitem_id, item_id, item_id)
        # Fetch some sample data for illustration purposes
        cursor.execute("INSERT INTO ListItem (ListItemID, ItemID, ListID) VALUES (%s, %s, %s)",
                    (listitem_id, item_id, list_id)) 
        conn.commit()     

    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()

    return redirect(redirection)

@app.route('/show_list', methods = ['GET', 'POST'])
def show_list():
    if 'email' not in session:
        return redirect(url_for('index'))
    user_email = session.get('email')
    user_id = get_userID_from_email(user_email)
    user_data = get_user_data(user_email)
    profile_pic = user_data[0][5]
    list_id = request.args.get('list_id')
    list_data = get_list_data(list_id)
    list_name = list_data[0][0]

    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        # Fetch some sample data for illustration purposes
        query = "SELECT ItemID FROM ListItem WHERE ListID = %s"
        cursor.execute(query, (list_id,))
        all_items = cursor.fetchall()
        print("all items: ", all_items)
        if len(all_items) == 0:
            return render_template('show_list.html', profile_pic=profile_pic, empty_message="Empty List")
        list_items = list()
        for item in all_items:
            list_items.append(item[0])
        print(list_items)

        # issue: Work only if lsit is not empty.
        cursor.execute("SELECT * FROM Items WHERE ItemID")
        query = "SELECT * FROM Items WHERE ItemID IN %s"
        cursor.execute(query, (list_items,))
        items_data = [dict((cursor.description[i][0], value) 
                      for i, value in enumerate(row)) for row in cursor.fetchall()]
        print("items_data:", items_data)
        # if items_data is None:
        #     return render_template('show_list.html', profile_pic=profile_pic, empty_message="Empty List")

    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()

    return render_template('show_list.html', profile_pic=profile_pic, items_data=items_data, list_name=list_name, list_id=list_id)

@app.route('/create')
def create():

    if 'email' not in session:
        return redirect(url_for('index'))
    user_email = session.get('email')
    user_id = get_userID_from_email(user_email)
    user_data = get_user_data(user_email)
    description = user_data[0][-1]
    user_name = user_data[0][1]
    profile_pic = user_data[0][5]
    print(profile_pic)

    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        # Fetch some sample data for illustration purposes
        cursor.execute("SELECT * FROM Lists WHERE UserID = %s", (user_id))
        lists_data = [dict((cursor.description[i][0], value) 
                    for i, value in enumerate(row)) for row in cursor.fetchall()]
        pprint.pprint(lists_data)

    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()

    return render_template('create_post.html', description=description, user_name=user_name, profile_pic=profile_pic, lists_data=lists_data)

@app.route('/create_item')
def create_item():
    pass

@app.route('/home')
def home():
    if 'email' not in session:
        return redirect(url_for('index'))

    user_email = session.get('email')
    user_data = get_user_data(user_email)
    profile_pic = user_data[0][5]
    #print(profile_pic)

    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        # Fetch some sample data for illustration purposes
        cursor.execute("SELECT * FROM Items")
        items_data = [dict((cursor.description[i][0], value) 
                      for i, value in enumerate(row)) for row in cursor.fetchall()]
        #pprint.pprint(items_data)
        random.shuffle(items_data)

    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()

    return render_template('home.html', profile_pic=profile_pic, items_data=items_data)

@app.route('/movies')
def movies():
    if 'email' not in session:
        return redirect(url_for('index'))

    user_email = session.get('email')
    user_data = get_user_data(user_email)
    profile_pic = user_data[0][5]
    print(profile_pic)

    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        # Fetch some sample data for illustration purposes
        query = "SELECT * FROM Items WHERE Category = %s"
        cursor.execute(query, ("Movie",))
        movie_data = [dict((cursor.description[i][0], value) 
                      for i, value in enumerate(row)) for row in cursor.fetchall()]
        pprint.pprint(movie_data)
        random.shuffle(movie_data)

    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()

    return render_template('movies.html', profile_pic=profile_pic, movie_data=movie_data)

@app.route('/art')
def art():
    if 'email' not in session:
        return redirect(url_for('index'))

    user_email = session.get('email')
    user_data = get_user_data(user_email)
    profile_pic = user_data[0][5]
    print(profile_pic)

    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        # Fetch some sample data for illustration purposes
        query = "SELECT * FROM Items WHERE Category = %s"
        cursor.execute(query, ("Art",))
        art_data = [dict((cursor.description[i][0], value) 
                      for i, value in enumerate(row)) for row in cursor.fetchall()]
        pprint.pprint(art_data)
        random.shuffle(art_data)

    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()

    return render_template('art.html', profile_pic=profile_pic, art_data=art_data)

    # user_id = get_logged_in_user_id()

    # if user_id:
    #     try:
    #         conn = mysql.connect()
    #         cursor = conn.cursor()

    #         # Fetch some sample data for illustration purposes
    #         cursor.execute("SELECT * FROM Items WHERE Category = 'Art' LIMIT 8")
    #         art_data = cursor.fetchall()

    #         return render_template('art.html', items_data=art_data)

    #     except Exception as e:
    #         return str(e)
    #     finally:
    #         cursor.close()
    #         conn.close()
    # else:
    #     return redirect(url_for('index'))

@app.route('/buy_art')
def buy_art():
    pass

@app.route('/music')
def music():
    if 'email' not in session:
        return redirect(url_for('index'))

    user_email = session.get('email')
    user_data = get_user_data(user_email)
    profile_pic = user_data[0][5]
    print(profile_pic)

    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        # Fetch some sample data for illustration purposes
        query = "SELECT * FROM Items WHERE Category = %s"
        cursor.execute(query, ("Music",))
        music_data = [dict((cursor.description[i][0], value) 
                      for i, value in enumerate(row)) for row in cursor.fetchall()]
        pprint.pprint(music_data)
        random.shuffle(music_data)

    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()

    return render_template('music.html', profile_pic=profile_pic, music_data=music_data)

@app.route('/people')
def people():
    if 'email' not in session:
            return redirect(url_for('index'))

    user_email = session.get('email')
    user_data = get_user_data(user_email)
    profile_pic = user_data[0][5]
    print(profile_pic)

    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        # Fetch some sample data for illustration purposes
        cursor.execute("SELECT * FROM Users")
        user_data = [dict((cursor.description[i][0], value) 
                      for i, value in enumerate(row)) for row in cursor.fetchall()]
        pprint.pprint(user_data)
        random.shuffle(user_data)

    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()

    return render_template('people.html', profile_pic=profile_pic, user_data=user_data)

@app.route('/about')
def about():
    if 'email' in session:
        user_email = session.get('email')
        user_data = get_user_data(user_email)
        profile_pic = user_data[0][5]
    return render_template("/about.html", profile_pic=profile_pic)

if __name__ == '__main__':
    app.run(debug=True)
