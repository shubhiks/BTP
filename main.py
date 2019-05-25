from flask import *
import pymysql
import ctypes
import googlemaps
from itertools import permutations
import math
import time

gmaps = googlemaps.Client(key='AIzaSyBO-As_Dsy1gdaAuTPVAThEvWRNmvLWY-4')

UPLOAD_FOLDER = r'C:\Users\hp india\PycharmProjects\SE_Project\Uploads'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024


def databaseConnect():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='root',
                                 db='test',
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

    def __init__(self, id, destination):
        self.id = id
        self.destination = destination

    def to_string(self):
        return self.id + " " + self.destination


class UserAttributes:

    def __init__(self, userid, destination, distance, time, cost):
        self.userid = userid
        self.destination = destination
        self.distance = distance
        self.time = time
        self.cost = cost

    def to_string(self):
        return str(self.userid) + " " + self.destination + " " + str(self.distance) + " " + str(self.time) + " " + str(self.cost)

distance_matrix_map = dict()
time_matrix_map = dict()


def get_distance(src, dest):

    if src + dest in distance_matrix_map:
        return distance_matrix_map[src + dest]
    else :
        my_dist = gmaps.distance_matrix(src, dest)['rows'][0]['elements'][0]
        distance_matrix_map[src + dest] = my_dist['distance']['value']
        distance_matrix_map[dest + src] = my_dist['distance']['value']
        time_matrix_map[src + dest] = my_dist['duration']['value']
        time_matrix_map[dest + src] = my_dist['duration']['value']
        return distance_matrix_map[src + dest]


def get_duration(src, dest) :
    if (src + dest) in time_matrix_map:
        return time_matrix_map[src + dest]
    else :
        my_dist = gmaps.distance_matrix(src, dest)['rows'][0]['elements'][0]
        distance_matrix_map[src + dest] = my_dist['distance']['value']
        distance_matrix_map[dest + src] = my_dist['distance']['value']
        time_matrix_map[src + dest] = my_dist['duration']['value']
        time_matrix_map[dest + src] = my_dist['duration']['value']
        return time_matrix_map[src + dest]


cache = dict()
users = list()
groups = list()
n = 0
answer = 1e9
home_source = "Rajiv Chowk"

def solve(taxino, curloc, curtime, users_in_taxi, cost, best_config):

    global answer
    if users_in_taxi.count(0) + users_in_taxi.count(1) == 0:
        if cost < answer:
            best_config.clear()
            for i in users_in_taxi:
                best_config.append(i)
            answer = cost
        return 0
    if dpstate(taxino, curloc, curtime, users_in_taxi) in cache:
       return cache[dpstate(taxino, curloc, curtime, users_in_taxi)]

    res = 1e9

    # Move on to new taxi if all passengers have reached their destination
    if curloc != home_source and users_in_taxi.count(1) == 0:
        return solve(taxino + 1, home_source, 0, users_in_taxi, cost, best_config)

    # Try picking up passengers if there is space and we are at source and calculate best result
    picked_up = users_in_taxi.count(1);
    for i in range(0, n):

        if picked_up < 4 and users_in_taxi[i] == 0 and curloc == home_source:
            users_in_taxi[i] = 1
            res = min(res, solve(taxino, curloc, curtime, users_in_taxi, cost, best_config))
            users_in_taxi[i] = 0

    # Try dropping off passengers and see if it yields best result
    for i in range(0, n) :

        if users_in_taxi[i] == 1:
            users_in_taxi[i] = taxino
            res = min(res, get_distance(curloc, users[i].destination) + solve(taxino, users[i].destination, curtime + get_distance(curloc, users[i].destination), users_in_taxi, cost + get_distance(curloc, users[i].destination), best_config))
            users_in_taxi[i] = 1;

    cache[dpstate(taxino, curloc, curtime, users_in_taxi)] = res
    return res


def cost_calculator(dist, tot_dist, min_cost, tot_cost) :
    val = (1.0 * dist) / (1.0 * tot_dist)
    val *= tot_cost
    val = math.floor(val)
    val = max(val, min_cost)
    return val


def print_group_pattern(users_in_taxi) :
    users_done = 0

    for i in range(2, 1000):
        if users_done >= n:
            return

        cur_cab_users = list()
        print("Taxi #" + str(i - 1) + ": ")
        for j in range(0, n):
            if users_in_taxi[j] == i:
                print(str(users[j].id) + " ")
                users_done += 1
                cur_cab_users.append(users[j])
        print("")
        # Process current cab users to form person attribute object for each of the user sitting in this cab
        tot_users = len(cur_cab_users)
        if tot_users == 0 :
            return
        # Groups is a list which is the final object to be sent to front end and comprises of a list of "group" and each "group" is a list of "UserAttributes"
        # We are here to find current group details
        group = list()
        perm = list()
        for x in range(0, tot_users):
            perm.append(x)
        perm_list = permutations(perm)

        min_dist = 1e9
        for candidate in perm_list:
            cur_dist = get_distance(home_source, cur_cab_users[candidate[0]].destination)
            for idx in range(1, tot_users):
                cur_dist += get_distance(cur_cab_users[candidate[i - 1]].destination, cur_cab_users[candidate[i]].destination)

            if(cur_dist > min_dist):
                continue
            # Update the best group

            group.clear()
            min_dist = cur_dist
            dur_so_far = get_duration(home_source, cur_cab_users[candidate[0]].destination)
            dist_so_far = get_distance(home_source, cur_cab_users[candidate[0]].destination)
            minimum_cost = 53
            total_cost = 60 + 12 * ((1.0 * cur_dist)/ (1000.0))

            group.append(UserAttributes(cur_cab_users[candidate[0]].id, cur_cab_users[candidate[0]].destination,
                                        dist_so_far, dur_so_far, cost_calculator(dist_so_far, cur_dist, minimum_cost, total_cost)))

            for idx in range(1, tot_users):
                dur_so_far += get_duration(cur_cab_users[candidate[i - 1]].destination, cur_cab_users[candidate[i]].destination)
                dist_so_far = get_distance(cur_cab_users[candidate[i - 1]].destination, cur_cab_users[candidate[i]].destination)

                group.append(UserAttributes(cur_cab_users[candidate[i]].id, cur_cab_users[candidate[i]].destination,
                                            dist_so_far, dur_so_far,
                                            cost_calculator(dist_so_far, cur_dist, minimum_cost, total_cost)))

        groups.append(group)

def populate_user_list() :

    users = list()
    sql = "SELECT userid, destination FROM request WHERE status = 0"
    try:
        connection = databaseConnect()
        cur = connection.cursor()
        cur.execute(sql)
        numrows = cur.rowcount

        for x in range(0, numrows):
            row = cur.fetchone()
            user_id = row["userid"]
            dest = row["destination"]
            users.append(User(user_id, dest))
    finally:
        connection.close()

    return users

def _main_():

    global n
    global users
    global groups

    import time
    starttime = time.time()
    while True:
        users = populate_user_list()
        n = len(users)
        users_in_taxi = [0 for i in range(n)]
        best_config = list()
        mincost = solve(2, home_source, 0, users_in_taxi, 0, best_config)

        print(answer)
        print(best_config)
        print("")

        print_group_pattern(best_config)

        for x in groups:
            for y in x:
                print(y.to_string())
            print("")
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))


# EVERYTHING RELATED TO RENDERING PAGES ACCORDING TO LINKS
_main_()




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

