from flask import *
import pymysql
import ctypes

UPLOAD_FOLDER = r'C:\Users\hp india\PycharmProjects\SE_Project\Uploads'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024

def databaseConnect():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='root',
                                 db='btp',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    return connection




class dpstate:
    def __init__(self, taxino, curloc, curtime, users_in_taxi):
        self.taxino = taxino
        self.curloc = curloc
        self.curtime = curtime
        self.users_in_taxi = users_in_taxi

    def __hash__(self):
        val = 0
        for i in self.users_in_taxi:
            val += i * i;
        return hash((self.taxino, self.curloc, self.curtime)) + val

    def __eq__(self, other):
        return (self.taxino, self.curloc, self.curtime, self.users_in_taxi) == (other.taxino, other.curloc, other.curtime, other.users_in_taxi)

    def to_string(self):
        return self.taxino + " " + self.curloc + " " + self.curtime + " " + self.users_in_taxi

class User:
    def __init__(self, name, id, destination):
        self.name = name
        self.id = id
        self.destination = destination

    def to_string(self):
        return self.name + " " + self.id + " " + self.destination


class TriggerRequest:
    def __init__(self, user_id, destination_id, timestamp):
        self.user_id = user_id
        self.destination_id = destination_id
        self.timestamp = timestamp

    def to_string(self):
        return self.user_id + " " + self.destination_id + " " + self.timestamp


time_matrix = [[0 for i in range(8)] for j in range(8)]

time_matrix[0][1] = time_matrix[1][0] = 22
time_matrix[0][2] = time_matrix[2][0] = 31
time_matrix[0][3] = time_matrix[3][0] = 53
time_matrix[0][4] = time_matrix[4][0] = 47
time_matrix[0][5] = time_matrix[5][0] = 80
time_matrix[0][6] = time_matrix[6][0] = 85
time_matrix[0][7] = time_matrix[7][0] = 90

time_matrix[1][2] = time_matrix[2][1] = 13
time_matrix[1][3] = time_matrix[3][1] = 34
time_matrix[1][4] = time_matrix[4][1] = 38
time_matrix[1][5] = time_matrix[5][1] = 46
time_matrix[1][6] = time_matrix[6][1] = 54
time_matrix[1][7] = time_matrix[7][1] = 58

time_matrix[2][3] = time_matrix[3][2] = 27
time_matrix[2][4] = time_matrix[4][2] = 31
time_matrix[2][5] = time_matrix[5][2] = 44
time_matrix[2][6] = time_matrix[6][2] = 48
time_matrix[2][7] = time_matrix[7][2] = 54

time_matrix[3][4] = time_matrix[4][3] = 11
time_matrix[3][5] = time_matrix[5][3] = 17
time_matrix[3][6] = time_matrix[6][3] = 25
time_matrix[3][7] = time_matrix[7][3] = 29

time_matrix[4][5] = time_matrix[5][4] = 18
time_matrix[4][6] = time_matrix[6][4] = 21
time_matrix[4][7] = time_matrix[7][4] = 25

time_matrix[0][1] = time_matrix[1][0] = 14
time_matrix[0][1] = time_matrix[1][0] = 18

time_matrix[0][1] = time_matrix[1][0] = 8

n = 7

cache = dict()
users = list()

users.append(User('Shubham', 0, 1))
users.append(User('Shivam', 1, 2))
users.append(User('Sweta', 2, 3))
users.append(User('Ujjawal', 3, 4))
users.append(User('Narain', 4, 5))
users.append(User('Rick', 5, 6))
users.append(User('Morty', 6, 7))

answer = 1e9


def solve(taxino, curloc, curtime, users_in_taxi, cost, best_config):

    global answer
    if users_in_taxi.count(0) + users_in_taxi.count(1) == 0:
        #print(users_in_taxi)
        if cost < answer:
            best_config.clear()
            for i in users_in_taxi:
                best_config.append(i)
            answer = cost
        return 0
    if dpstate(taxino, curloc, curtime, users_in_taxi) in cache:
       return cache[dpstate(taxino, curloc, curtime, users_in_taxi)]

    #print(users_in_taxi)

    res = 1e9

    # Move on to new taxi if all passengers have reached their destination
    if curloc != 0 and users_in_taxi.count(1) == 0:
        return solve(taxino + 1, 0, 0, users_in_taxi, cost, best_config)

    # Try picking up passengers if there is space and we are at source and calculate best result
    picked_up = users_in_taxi.count(1);
    for i in range(0, n):

        if picked_up < 4 and users_in_taxi[i] == 0 and curloc == 0:
            users_in_taxi[i] = 1
            res = min(res, solve(taxino, curloc, curtime, users_in_taxi, cost, best_config))
            users_in_taxi[i] = 0

    # Try dropping off passengers and see if it yields best result
    for i in range(0, n) :

        if users_in_taxi[i] == 1:
            users_in_taxi[i] = taxino
            res = min(res, time_matrix[curloc][users[i].destination] + solve(taxino, users[i].destination, curtime + time_matrix[curloc][users[i].destination], users_in_taxi, cost + time_matrix[curloc][users[i].destination], best_config))
            users_in_taxi[i] = 1;

    cache[dpstate(taxino, curloc, curtime, users_in_taxi)] = res
    return res


def print_group_pattern(users_in_taxi) :
    users_done = 0
    for i in range (2, 1000):
        if users_done >= n:
            return
        print("Taxi #" + str(i - 1) + ": ")
        for j in range(0, n):
            if users_in_taxi[j] == i:
                print(users[j].name + " ")
                users_done += 1
        print("")


def _main_():

    print(time_matrix)
    print("")

    users_in_taxi = [0 for i in range(7)]
    best_config = list()
    mincost = solve(2, 0, 0, users_in_taxi, 0, best_config)

    print(answer)
    print(best_config)
    print("")

    print_group_pattern(best_config)

# EVERYTHING RELATED TO RENDERING PAGES ACCORDING TO LINKS

@app.route('/')
def main():
    return render_template('index.html')


@app.route('/login.html')
def login():
    return render_template('login.html')


@app.route('/register.html')
def register():
    return render_template('register.html')


@app.route('/index-3.html')
def services():
    return render_template('index-3.html')


@app.route('/index-4.html')
def contact_us():
    return render_template('index-4.html')


@app.route('/index.html')
def return_to_home():
    return render_template('index.html')

# EVERYTHING RELATED TO GETTING INPUT FROM FORMS

""""
#1 Login form on the homepage
@app.route('/booking/booking.php', methods=['POST'])
def login_form():

    # read the posted values from the UI
    _name = request.form['Name']
    _email = request.form['ID']
    _password = request.form['Password']

    # validate the received values=
    if _name and _email and _password:
        print(_name)
        print(_email)
        print(_password)
        return json.dumps({'html': '<span>All fields good !!</span>'})
    else:
        return json.dumps({'html': '<span>Enter the required fields</span>'})


#2 Booking form on the homepage
@app.route('/booking/booking.php', methods=['POST'])
def booking_form():

    # read the posted values from the UI
    _name = request.form['Name']
    _from = request.form['From']
    _email = request.form['Email']
    _to = request.form['To']
    _time = request.form['Time']
    _date = request.form['Date']
    _message = request.form['Message']

    # validate the received values=
    if _name and _email:
        print(_name)
        print(_email)
        return json.dumps({'html': '<span>All fields good !!</span>'})
    else:
        return json.dumps({'html': '<span>Enter the required fields</span>'})

@app.route('/booking/booking.php', methods=['POST'])
def registration_form():

    # read the posted values from the UI
    _name = request.form['Name']
    _email = request.form['ID']
    _password = request.form['Password']

    # validate the received values=
    if _name and _email and _password:
        print(_name)
        print(_email)
        print(_password)
        return json.dumps({'html': '<span>All fields good !!</span>'})
    else:
        return json.dumps({'html': '<span>Enter the required fields</span>'})


@app.route('/booking/booking.php', methods=['POST'])
def query_form():

    # read the posted values from the UI
    _name = request.form['Name']
    _email = request.form['ID']
    _password = request.form['Password']

    # validate the received values=
    if _name and _email and _password:
        print(_name)
        print(_email)
        print(_password)
        return json.dumps({'html': '<span>All fields good !!</span>'})
    else:
        return json.dumps({'html': '<span>Enter the required fields</span>'})

"""

@app.route('/savedetails', methods=['POST', 'GET'])
def savedetails():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        dob = request.form['dob']
        sql = "insert into user(username, email, password, phone, dob) values(%s,%s,%s,%s,%s)"
        try:
            connection = databaseConnect()
            cur = connection.cursor()
            cur.execute(sql,(username,email,password,phone, dob))
            connection.commit()
            print(" User added successfully!")
        finally:
            connection.close()
    return redirect(url_for('login'))


@app.route('/setcookie', methods=['POST', 'GET'])
def setcookie():
    if request.method == 'POST':
        email = request.form['email']
        passw = request.form['password']
        sql = "select password from user where email = %s"
        try:
            connection = databaseConnect()
            cur = connection.cursor()
            cur.execute(sql, email)
            if (cur.rowcount):
                actualPass = cur.fetchone()['password']
                if(passw == actualPass):
                    print(" password matched succesfully")
                    sql2 = "select id from user where email = %s"
                    cur.execute(sql2, email)
                    id1 = cur.fetchone()['id']
                    print(id1)
                    resp = make_response(render_template('index.html'))
                    resp.set_cookie('userID', value=str(id1))
                    print("userID cookie set")
                else:
                    print("password does not match")
                    resp = make_response(render_template('/login.html'))
                    ctypes.windll.user32.MessageBoxW(0, "password does not match", "Error", 0)
            else:
                print("username does not exist")
                resp = make_response(render_template('/login.html'))
                ctypes.windll.user32.MessageBoxW(0, "username does not exists", "Error", 0)
        finally:
            connection.close()
    else:
        resp = make_response(render_template('/login.html'))
    print("going")
    return resp

@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        sql = "insert into contactUs(name, email, phone, message) values(%s,%s,%s,%s)"
        try:
            connection = databaseConnect()
            cur = connection.cursor()
            cur.execute(sql,(name,email,phone, message))
            connection.commit()
            print(" Message added successfully!")
        finally:
            connection.close()
            resp = make_response(render_template('/index.html'))
            ctypes.windll.user32.MessageBoxW(0, "Thank you for contacting us. \n We will contact you shortly ", "Message Added", 0)
    return resp

@app.route('/addRequest', methods=['POST', 'GET'])
def addRequest():
    if request.method == 'POST':
        destination = request.form['destination']
        userID = request.cookies.get('userID')
        sql = "insert into request(destination, time, date, userid) values(%s,%s,%s,%s)"
        try:
            connection = databaseConnect()
            cur = connection.cursor()
            cur.execute("select CURTIME() as time")
            time = cur.fetchone()['time']
            cur.execute("select CURDATE() as date")
            date = cur.fetchone()['date']
            cur.execute(sql,(destination,time,date,userID))
            connection.commit()
            print(" Request added successfully!")
      # function call
        finally:
            connection.close()
    # TO DO : change redirect url
    return redirect(url_for('login'))



# RUN THE APPLICATION
if __name__ == "__main__":
    app.run(debug=True)
