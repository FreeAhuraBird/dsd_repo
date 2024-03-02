from flask import Flask, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure MySQL
app.config['MYSQL_DATABASE_USER'] = 'art@%'
app.config['MYSQL_DATABASE_PASSWORD'] = 'superbra'
app.config['MYSQL_DATABASE_DB'] = 'art_database'
app.config['MYSQL_DATABASE_HOST'] = '188.148.152.167'

mysql = MySQL(app)

def get_logged_in_user_id():
    return session.get('user_id', None)

def get_user_data():
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Users")
        user_data = cursor.fetchall()
        return user_data

def get_new_listid():
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Lists")
        list_data = cursor.fetchall()
        new_listid = list_data[0][0] + 1 #get new listid
        return new_listid

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

# Define routes
@app.route('/')
def index():
    if request.method == 'POST':
        username = request.form['signup-username']
        password = request.form['signup-password']
        email = request.form['signup-email']
        color = request.form.get('color', 'beige')
        print(username, password, email, color)
        print("!!!!!!")
        # Check if password contains a capital letter
    # if not any(char.isupper() for char in password):
    #     return 'Password must contain at least one capital letter.'
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['signup-username']
        password = request.form['signup-password']
        email = request.form['signup-email']
        color = request.form.get('color', 'beige')
        print(username, password, email, color)
        print("something")

        userid = get_new_listid()
        # Store user data in MySQL database
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            # Insert user into Users table
            cursor.execute("INSERT INTO Users (UserID, Username, Password, Email, Profile_Picture) VALUES (%s, %s, %s, %s)",
                           (userid, username, password, email, 'images/cat_placeholder.jpg'))

            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for("home"))
        
        except Exception as e:
            return str(e)

        #     return 'Signup successful!'
        # Check if password contains a capital letter
        # if not any(char.isupper() for char in password):
        #     return 'Password must contain at least one capital letter.'

        # Store user data in MySQL database


        #     return 'Signup successful!'
        # except Exception as e:
        #     return str(e)
        # finally:
        #     cursor.close()
        #     conn.close()

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['login-email']
        password = request.form['login-password']
        print(email, password)
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            # Check if the provided credentials are valid
            cursor.execute("SELECT * FROM Users WHERE Username = %s AND Password = %s", (email, password))
            user_data = cursor.fetchone()

            if user_data != None:
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

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    user_id = get_logged_in_user_id()
    user_data = get_user_data()
    description = user_data[0][-1]
    user_name = user_data[0][1]

    # conn = mysql.connect()
    # cursor = conn.cursor()

    # cursor.execute("SELECT * FROM Lists WHERE UserID = %s", (user_id,))
    # user_playlists = cursor.fetchall()
    return render_template('profile.html', description=description, user_name=user_name)

    # if user_id:
    #     try:
    #         conn = mysql.connect()
    #         cursor = conn.cursor()

    #         # Fetch user data
    #         cursor.execute("SELECT * FROM Users WHERE UserID = %s", (user_id,))
    #         user_data = cursor.fetchone()
    #         # Fetch playlists created by the user
    #         cursor.execute("SELECT * FROM Lists WHERE UserID = %s", (user_id,))
    #         user_playlists = cursor.fetchall()

    #         # Fetch playlists followed by the user
    #         cursor.execute("""
    #             SELECT L.ListID, L.Title, L.Description
    #             FROM Lists L
    #             INNER JOIN UserLists UL ON L.ListID = UL.ListID
    #             WHERE UL.UserID = %s
    #         """, (user_id,))
    #         followed_playlists = cursor.fetchall()

    #         return render_template('profile.html', user_data=user_data, user_playlists=user_playlists,
    #                                followed_playlists=followed_playlists)
    #     except Exception as e:
    #         return str(e)
    #     finally:
    #         cursor.close()
    #         conn.close()
    # else:
    #     return render_template('profile.html')

# @app.route('/create_board')
# def board():
#     # take userid
#     # create new board : insert userid, create listid, get title, descrption
#     new_listid = get_new_listid()
#     conn = mysql.connect()
#     cursor = conn.cursor()

#     # cursor.execute("INSERT INTO Users (UserID, Username, Password, Email, Profile_Picture) VALUES (%s, %s, %s, %s)",
#     #                    (userid, username, password, email, 'images/cat_placeholder.jpg'))


#     # Insert user into Users table
#     cursor.execute("INSERT INTO Lists (ListID, UserID, Title, Description, CreationDate) VALUES (%s, %s, %s, %s, %s)",
#                    (new_listid, 'userid', 'title', 'description', 'creationdate'))
    

@app.route('/home')
def home():
    user_id = get_logged_in_user_id()
    return render_template('home_user.html')

    if user_id:
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            # Fetch some sample data for illustration purposes
            cursor.execute("SELECT * FROM Items LIMIT 3")
            items_data = cursor.fetchall()

            return render_template('home_user.html', items_data=items_data)

        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            conn.close()
    else:
        return redirect(url_for('index'))

@app.route('/movies')
def movies():
    #user_id = get_logged_in_user_id()
    return render_template('movies.html')
    # if user_id:
    #     try:
    #         conn = mysql.connect()
    #         cursor = conn.cursor()

    #         # Fetch some sample data for illustration purposes
    #         cursor.execute("SELECT * FROM Items WHERE Category = 'Movies' LIMIT 8")
    #         movies_data = cursor.fetchall()

    #         return render_template('movies.html', items_data=movies_data)

    #     except Exception as e:
    #         return str(e)
    #     finally:
    #         cursor.close()
    #         conn.close()
    # else:
    #     return redirect(url_for('index'))

@app.route('/buy_movie/<int:item_id>')
def buy_movie(item_id):
    user_id = get_logged_in_user_id()

    if user_id:
        if reserve_item_for_user(item_id, user_id):
            return f'Movie with ItemID {item_id} reserved for purchase. Please complete the transaction within 10 minutes.'
        else:
            return f'Movie with ItemID {item_id} is not available for purchase.'
    else:
        return redirect(url_for('index'))

@app.route('/art')
def art():
    user_id = get_logged_in_user_id()

    if user_id:
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            # Fetch some sample data for illustration purposes
            cursor.execute("SELECT * FROM Items WHERE Category = 'Art' LIMIT 8")
            art_data = cursor.fetchall()

            return render_template('art.html', items_data=art_data)

        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            conn.close()
    else:
        return redirect(url_for('index'))

@app.route('/buy_art/<int:item_id>')
def buy_art(item_id):
    user_id = get_logged_in_user_id()

    if user_id:
        if reserve_item_for_user(item_id, user_id):
            return f'Art with ItemID {item_id} reserved for purchase. Please complete the transaction within 10 minutes.'
        else:
            return f'Art with ItemID {item_id} is not available for purchase.'
    else:
        return redirect(url_for('index'))

@app.route('/music')
def music():
    user_id = get_logged_in_user_id()

    if user_id:
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            # Fetch some sample data for illustration purposes
            cursor.execute("SELECT * FROM Items WHERE Category = 'Music' LIMIT 8")
            music_data = cursor.fetchall()

            return render_template('music.html', items_data=music_data)

        except Exception as e:
            return str(e)
        finally:
            cursor.close()
            conn.close()
    else:
        return redirect(url_for('index'))

@app.route('/buy_music/<int:item_id>')
def buy_music(item_id):
    user_id = get_logged_in_user_id()

    if user_id:
        if reserve_item_for_user(item_id, user_id):
            return f'Music with ItemID {item_id} reserved for purchase. Please complete the transaction within 10 minutes.'
        else:
            return f'Music with ItemID {item_id} is not available for purchase.'
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
