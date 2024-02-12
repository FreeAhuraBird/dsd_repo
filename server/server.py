from flask import Flask, jsonify, request
import bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

'''
I den här filen har jag bara skapat en snabb liten app med flask som de rekommenderade att vi skulle göra
på canvas. Den här appen ska vi koppla med vår mariaDB databas sen i framtiden. Änsålänge använder den bara
"mock users" alltså låtsas användare.

Den första delen här nere som använder "JWT" det är JSON Web Tokens, den används för att säkert
överföra information mellan klienten och servern som ett JSON-objekt. Denna information kan valideras 
och verifieras eftersom den är digitalt signerad. Vad innebär det? Jo alltså, den hemliga nyckeln används
för att skapa (signera) en token. När token sedan skickas tillbaka till servern för validering, så kollar servern den hemliga
nyckeln återigen för att kontrollera tokenens signatur. Om signaturen är giltig och matchar, så anses den vara autentisk.

Vad händer om vi inte använder JWT? Vem som helst kan då få tag på användar data och annan känslig information.
'''

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Vi ska ändra detta till en random secret key.
jwt = JWTManager(app)

# Just nu bara mock users, för att testa. Lägg sedan till mariaDB
users = {}

# Här krypteras lösenordet med ett populärt hashningsalgoritm som jag hitta på nätet,
# det ser jobbigt ut men det är ganska enkelt faktiskt. 
# finns mer info här: https://www.geeksforgeeks.org/hashing-passwords-in-python-with-bcrypt/

def hash_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(stored_password, provided_password):
    stored_password_bytes = stored_password.encode('utf-8')
    provided_password_bytes = provided_password.encode('utf-8')
    return bcrypt.checkpw(provided_password_bytes, stored_password_bytes)



# Okej här kommer vi in till vår inlognings sida. Här kollar koden om url slutar på "/register" vilket den borde göra
# i vår register sida på nätet. Då skickar den data som vår användare har skrivit. username, email osv.
#
# Den gör samma sak på "/login" och skickar ett bekräftelse meddelande om användaren lyckats logga in.

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    email = data['email']
    plain_password = data['password']
    
    if username in users:
        return jsonify({"success": False, "message": "Username already exists"}), 409
    
    hashed_password = hash_password(plain_password)
    users[username] = {'email': email, 'password': hashed_password}
    
    return jsonify({"success": True, "message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    submitted_password = data.get('password')
    
    user = users.get(username)
    
    if user and verify_password(user['password'], submitted_password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

# Det här är en skyddad route, man får bara tillgång till den med en giltig JSON Web Token.
# Den returnerar då information om den inloggade användaren. Det kan vara användbart när användaren kollar sin egna profil t.ex.
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

if __name__ == '__main__':
    app.run(debug=True)
