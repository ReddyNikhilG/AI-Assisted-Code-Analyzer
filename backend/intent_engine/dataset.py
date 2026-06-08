dataset = [
    # API Communication
    {"code": "requests.get(url, headers=headers)", "intent": "API Communication"},
    {"code": "requests.post(endpoint, json=payload)", "intent": "API Communication"},
    {"code": "response = requests.put(api_url, data=data)", "intent": "API Communication"},
    {"code": "httpx.get('https://api.github.com')", "intent": "API Communication"},
    {"code": "urllib.request.urlopen(req)", "intent": "API Communication"},
    {"code": "async with aiohttp.ClientSession() as session:", "intent": "API Communication"},

    # Database Operation
    {"code": "SELECT * FROM users WHERE email = ?", "intent": "Database Operation"},
    {"code": "cursor.execute('INSERT INTO logs (message) VALUES (?)')", "intent": "Database Operation"},
    {"code": "conn = sqlite3.connect('app.db')", "intent": "Database Operation"},
    {"code": "session.query(User).filter_by(id=user_id).first()", "intent": "Database Operation"},
    {"code": "db.commit()", "intent": "Database Operation"},
    {"code": "client = pymongo.MongoClient('mongodb://localhost:27017/')", "intent": "Database Operation"},

    # Computer Vision
    {"code": "cv2.imread(image_path)", "intent": "Computer Vision"},
    {"code": "cv2.imshow('frame', gray)", "intent": "Computer Vision"},
    {"code": "image = Image.open('photo.jpg')", "intent": "Computer Vision"},
    {"code": "cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)", "intent": "Computer Vision"},
    {"code": "faces = face_cascade.detectMultiScale(gray, 1.1, 4)", "intent": "Computer Vision"},

    # Machine Learning
    {"code": "model.fit(X_train, y_train, epochs=10)", "intent": "Machine Learning"},
    {"code": "predictions = clf.predict(X_test)", "intent": "Machine Learning"},
    {"code": "X_train, X_test, y_train, y_test = train_test_split(X, y)", "intent": "Machine Learning"},
    {"code": "model = tf.keras.Sequential([keras.layers.Dense(10)])", "intent": "Machine Learning"},
    {"code": "loss = criterion(outputs, labels)", "intent": "Machine Learning"},
    {"code": "scaler = StandardScaler().fit(X)", "intent": "Machine Learning"},

    # Networking
    {"code": "s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)", "intent": "Networking"},
    {"code": "s.connect(('127.0.0.1', 8080))", "intent": "Networking"},
    {"code": "s.bind((host, port))", "intent": "Networking"},
    {"code": "s.listen(5)", "intent": "Networking"},
    {"code": "ssh = paramiko.SSHClient()", "intent": "Networking"},

    # File Handling
    {"code": "with open('report.txt', 'w') as f: f.write(content)", "intent": "File Handling"},
    {"code": "data = open('config.json').read()", "intent": "File Handling"},
    {"code": "if os.path.exists(file_path): os.remove(file_path)", "intent": "File Handling"},
    {"code": "shutil.copyfile(src, dst)", "intent": "File Handling"},
    {"code": "content = pathlib.Path('docs.md').read_text()", "intent": "File Handling"},

    # Authentication
    {"code": "hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())", "intent": "Authentication"},
    {"code": "token = jwt.encode({'user_id': 123}, secret, algorithm='HS256')", "intent": "Authentication"},
    {"code": "login(username, password)", "intent": "Authentication"},
    {"code": "m = hashlib.sha256(password.encode()).hexdigest()", "intent": "Authentication"},
    {"code": "verify_password(plain_password, hashed_password)", "intent": "Authentication"},

    # Web Server / API Framework
    {"code": "app = FastAPI()", "intent": "Web Server / API Framework"},
    {"code": "app = Flask(__name__)", "intent": "Web Server / API Framework"},
    {"code": "@app.get('/api/v1/status')", "intent": "Web Server / API Framework"},
    {"code": "@app.route('/login', methods=['POST'])", "intent": "Web Server / API Framework"},
    {"code": "uvicorn.run('main:app', host='0.0.0.0', port=8000)", "intent": "Web Server / API Framework"},

    # General Utility / Scripting
    {"code": "import math\nresult = math.sqrt(25)", "intent": "General Utility / Scripting"},
    {"code": "now = datetime.datetime.now()", "intent": "General Utility / Scripting"},
    {"code": "data = json.loads(json_string)", "intent": "General Utility / Scripting"},
    {"code": "import random\nnum = random.randint(1, 100)", "intent": "General Utility / Scripting"},
    {"code": "parser = argparse.ArgumentParser(description='CLI script')", "intent": "General Utility / Scripting"}
]