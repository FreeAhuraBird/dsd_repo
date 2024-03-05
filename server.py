from flask import Flask, render_template, request, redirect, url_for, session
#from Flask_session import Session
from flaskext.mysql import MySQL
from datetime import datetime, timedelta
import os, uuid, pprint, random
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure MySQL
app.config['MYSQL_DATABASE_USER'] = 'art@%'
app.config['MYSQL_DATABASE_PASSWORD'] = 'superbra'
app.config['MYSQL_DATABASE_DB'] = 'art_database'
app.config['MYSQL_DATABASE_HOST'] = '188.148.152.167'

app.config['UPLOAD_PATH'] = 'static/img'

mysql = MySQL(app)

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

# Behövde ändra den här för jag fick error att det var duplicate UserID
# Det här sättet kollar istället "vad är max userid" och kör +1 så att de inte
# blir några duplicate.
def get_new_listid():
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(UserID) FROM Users")
    max_userid = cursor.fetchone()[0]
    new_listid = max_userid + 1 if max_userid else 1
    return new_listid

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

# Define routes
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
    if 'email' in session:
        user_email = session.get('email')
        user_id = get_userID_from_email(user_email)
        user_data = get_user_data(user_email)
        description = user_data[0][-1]
        user_name = user_data[0][1]
        profile_pic = user_data[0][5]
        print(profile_pic)

        return render_template('profile.html', description=description, user_name=user_name, profile_pic=profile_pic)

    else:
        return redirect(url_for("login"))
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
        cursor.execute("SELECT * FROM Items")
        items_data = [dict((cursor.description[i][0], value) 
                      for i, value in enumerate(row)) for row in cursor.fetchall()]
        pprint.pprint(items_data)
        random.shuffle(items_data)

    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()

    return render_template('home.html', profile_pic=profile_pic, items_data=items_data)

@app.route('/movies')
def movies():
    if 'email' in session:
        user_email = session.get('email')
        user_data = get_user_data(user_email)
        profile_pic = user_data[0][5]
        print(profile_pic)
    #user_id = get_logged_in_user_id()
    return render_template('movies.html', profile_pic=profile_pic)
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

@app.route('/art')
def art():
    # if 'email' in session:
    #     user_email = session.get('email')
    #     user_data = get_user_data(user_email)
    #     profile_pic = user_data[0][5]
    #     print(profile_pic)
    # #user_id = get_logged_in_user_id()

    # return render_template('art.html', profile_pic=profile_pic)
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

    # user_id = get_logged_in_user_id()

    # if user_id:
    #     try:
    #         conn = mysql.connect()
    #         cursor = conn.cursor()

    #         # Fetch some sample data for illustration purposes
    #         cursor.execute("SELECT * FROM Items WHERE Category = 'Music' LIMIT 8")
    #         music_data = cursor.fetchall()

    #         return render_template('music.html', items_data=music_data)

    #     except Exception as e:
    #         return str(e)
    #     finally:
    #         cursor.close()
    #         conn.close()
    # else:
    #     return redirect(url_for('index'))

@app.route('/people')
def people():
    # if 'email' in session:
    #     user_email = session.get('email')
    #     user_data = get_user_data(user_email)
    #     profile_pic = user_data[0][5]
    #     print(profile_pic)
    # #user_id = get_logged_in_user_id()
    # return render_template('people.html', profile_pic=profile_pic)

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


if __name__ == '__main__':
    app.run(debug=True)
