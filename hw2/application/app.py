# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import settings
import sys,os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
import pymysql as db
import random
import datetime

def connection():
    ''' Use this function to create your connections '''
    con = db.connect(
        settings.mysql_host, 
        settings.mysql_user, 
        settings.mysql_passwd, 
        settings.mysql_schema)
    
    return con

####################### Q1 - findTrips #######################
 
def f_trips_tp_info(x, a, b, cur):
    """
    This function finds the trip package info of the given branch within the date window.

    Args:
        x: branch id
        a: first date
        b: second date
        cur: Database cursor.

    Returns:
        The list [(<trip_package_id1>, <cost_per_person1>, <max_num_participants1>, <reservation_count1>, <empty_seats1>, <trip_start1>, <trip_end1>), ...]
    """

    tp_info_query = """ SELECT tp.trip_package_id, tp.cost_per_person, tp.max_num_participants, count(DISTINCT r.Reservation_id), tp.max_num_participants - count(DISTINCT r.Reservation_id), tp.trip_start, tp.trip_end
                        FROM travel_agency_branch tab, trip_package tp, reservation r, offer o
                        WHERE 	r.offer_id  = o.offer_id AND 
                                r.travel_agency_branch_id = tab.travel_agency_branch_id AND 
                                tp.trip_package_id = o.trip_package_id AND
                                datediff(tp.trip_start, '{0}') >= 0 AND
                                datediff(tp.trip_start, '{1}' ) <= 0 AND
                                tab.travel_agency_branch_id = {2}
                        GROUP BY tp.cost_per_person, tp.max_num_participants,tp.trip_start, tp.trip_end, tp.trip_package_id
                        ORDER BY tp.trip_package_id ASC
          """.format(a, b, x)

    result = []

    # try to execute sql query
    try:
        cur.execute(tp_info_query)
    except (db.Error, db.Warning) as e:
        print(str(e))
        return None
    # get query result
    try:
        res = cur.fetchall()

        for re in res:
            l = [re[0], re[1], re[2], re[3], re[4], re[5], re[6]]
            result.append(l)

        return result
    
    except TypeError as e:
        print(str(e))
        return None


def f_trips_name_info(x, a, b, cur):
    """
    This function finds the names of the guides of the given branch within the date window.

    Args:
        x: branch id
        a: first date
        b: second date
        cur: Database cursor.

    Returns:
        The list [(<trip_package_id1>, <name1>, <surname1>), ...]
    """

    name_info_query = """   SELECT distinct tp.trip_package_id, e.name, e.surname
                            FROM travel_agency_branch tab, trip_package tp, reservation r, offer o, employees e, guided_tour gt
                            WHERE   r.offer_id  = o.offer_id AND
                                    r.travel_agency_branch_id = tab.travel_agency_branch_id AND
                                    tp.trip_package_id = o.trip_package_id AND
                                    datediff(tp.trip_start, '{0}') >= 0 AND
                                    datediff(tp.trip_start, '{1}' ) <= 0 AND
                                    tab.travel_agency_branch_id = {2} AND 
                                    gt.trip_package_id = tp.trip_package_id AND
                                    gt.travel_guide_employee_AM = e.employees_AM;
                            """.format(a, b, x)
    
    result = []

    # try to execute sql query
    try:
        cur.execute(name_info_query)
    except (db.Error, db.Warning) as e:
        print(str(e))
        return None
    # get query result
    try:
        res = cur.fetchall()

        for re in res:
            tup = [re[0], re[1], re[2]]
            result.append(tup)

        return result
    
    except TypeError as e:
        print(str(e))
        return None

def find_id_list(li, id):
    """
    This function returns the list with the given id in a list of lists.

    Args:
        li: list of format [[<id1>, ...], [<id2>, ...], ...]
        id: id to search

    Returns:
        The list [<id>, ...]
    """
    
    result = list(filter(lambda l: l[0] == id, li))
    
    # no list was found with that id
    if len(result) == 0:
        return None
    
    return result

def l_to_str(l):
    """
    This function returns a string given a list with tuples (name, surname).

    Args:
        l: list

    Returns:
        The string "(name_1, surname_1), (name_2, surname_2), ..."
    """

    s = ""
    
    for tup in l:
        s += str(tup[0])
        s += " "
        s += str(tup[1])
        s += ", " 

    # pop last 2 characters
    s = s[:-2]

    return s

def findTrips(x,a,b):
    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    cur=con.cursor()

    result = [("cost_per_person", "max_num_participants", "reservations_count", "empty_seats", "start_date", "end_date", "guide_names_list")]

    info_r = f_trips_tp_info(x, a, b, cur)

    if info_r == None:
        return None

    names_r = f_trips_name_info(x, a, b, cur)

    if names_r == None:
        return None

    # list of lists 
    # inner list format (id, (name, surrname))
    temp_l = []

    # constuct temp list which contains lists of all guides for each trip package
    for l in names_r:
        l_res = find_id_list(temp_l, l[0])
        
        # id hasnt been added yet
        if l_res == None:
            temp_l.append([l[0], (l[1], l[2])])
        else:
            l_res[0].append((l[1], l[2]))

    # construct result
    for l in info_r:
        l_res = find_id_list(temp_l, l[0])

        
        # no guides were found we just add -
        if l_res == None:
            l.append("No guide")

        # guides were foun we add them to the list
        else:
            to_append = l_res[0]

            # pop id
            to_append.pop(0)
            
            l.append(l_to_str(to_append))

        # pop id
        l.pop(0)
        result.append(tuple(l))


    con.close()

    return result


####################### Q2 - findRevenue #######################

def find_employee_info(cur, id):
    """
    This function returns the number of employees in each branch and the total salary.

    Args:
        cur: Database cursor.
        id: The id of the client.

    Returns:
        The list ["<attraction1>, <attraction2>, .."].
    """ 
    sql = """SELECT br.travel_agency_branch_id, count(distinct employees_AM), sum(e.salary)
              FROM travel_agency_branch br, employees e
              WHERE e.travel_agency_branch_travel_agency_branch_id = br.travel_agency_branch_id
              GROUP BY br.travel_agency_branch_id"""    
    try:
        cur.execute(sql)
    except (db.Error, db.Warning) as e:
        return [(str(e), ""),]
    try:
        employee_info = cur.fetchall()

        # convert the list of tupples into a list
        employees_info = list()
        for employee in employee_info: employees_info.append((employee[0],employee[1],employee[2]))
        return employees_info

    except TypeError as e:
        print(str(e))
        return None

def findRevenue(x):
    # Create a new connection
    con=connection()
    
    # Create a cursor on the connection
    cur=con.cursor()

    sql1 = """SELECT br.travel_agency_branch_id, count(distinct Reservation_id), sum(o.cost) as total_cost
              FROM reservation r, offer o, travel_agency_branch br
              WHERE r.offer_id = o.offer_id AND 
	                r.travel_agency_branch_id = br.travel_agency_branch_id 
              GROUP BY br.travel_agency_branch_id
              ORDER BY sum(o.cost) {0}""".format(x)
    result = [("travel_agency_branch_id", "total_num_reservations", "total_income","num_of_employees","total_salary")]

    # close connection to database
    try:
        # try to execute sql query
        try:
            cur.execute(sql1)
        except (db.Error, db.Warning) as e:
            return [(str(e), ""),]

        # get query result
        try:
            revenue = cur.fetchall()

            for branch in revenue:
               
                id, total_res, total_income = branch
                
                employees_info = find_employee_info(cur, id)

                # combine all the info
                for empl in employees_info:
                    if id == empl[0]:
                        result.append((id, total_res, total_income, empl[1], empl[2]))

            return result
        
        except TypeError as e:
            return [(str(e), ""),]
        
    # close connection to database
    finally:
        con.close()



####################### Q3 - bestClient #######################

def get_attractions(cur, id):
    """
    This function returns the attractions visited by the client in an alphabetical order.

    Args:
        cur: Database cursor.
        id: The id of the client.

    Returns:
        The list ["<attraction1>, <attraction2>, ..."].
    """
    
    sql = """
        SELECT DISTINCT ta.name
        FROM reservation res, tourist_attraction ta, guided_tour gt
        WHERE res.Customer_id = {0} AND res.offer_trip_package_id = gt.trip_package_id AND ta.tourist_attraction_id = gt.tourist_attraction_id
        ORDER BY ta.name;
        """.format(id)

    try:
        cur.execute(sql)
    except (db.Error, db.Warning) as e:
        return [(str(e), ""),]
    try:
        # convert the list of tupples into a list
        return list(cur.fetchall())

    except TypeError as e:
        print(str(e))
        return None

def get_num_of_visited(cur, id):
    """
    This function returns the tuple number of countries and number of cities visited by the client.

    Args:
        cur: Database cursor.
        id: The id of the client.

    Returns:
        The tuple (<number of countries>, <number of cities>).
    """
    
    sql = """
        SELECT count(DISTINCT d.name), count(DISTINCT d.country)
        FROM destination d, reservation res, offer o, trip_package_has_destination tphd
        WHERE res.Customer_id = {0} AND res.offer_id = o.offer_id
            AND o.trip_package_id = tphd.trip_package_trip_package_id AND tphd.destination_destination_id = d.destination_id;
        """.format(id)

    try:
        cur.execute(sql)
    except (db.Error, db.Warning) as e:
        return [(str(e), ""),]
    try:
        num_visited = cur.fetchall()
        return (num_visited[0][1], num_visited[0][0])
    except TypeError as e:
        print(str(e))
        return None
    
def get_best_clients(cur):
    """
    This function returns the credentials of the best client(s).

    Args:
        cur: Database cursor.

    Returns:
        The tuple (<(name1, surname1)>, <(name2, surname2)>, ...).
    """
    
    sql = """
        SELECT tr.traveler_id, tr.name, tr.surname
        FROM traveler AS tr
        WHERE 
        (
            SELECT SUM(o.cost)
            FROM reservation res, offer o
            WHERE tr.traveler_id = res.Customer_id AND res.offer_id = o.offer_id
            GROUP BY res.Customer_id
        )
        =
        (
            SELECT MAX(money_spent)
            FROM (
                SELECT res.Customer_id, SUM(o.cost) AS money_spent
                FROM reservation res, offer o
                WHERE res.offer_id = o.offer_id
                GROUP BY res.Customer_id
            ) AS max_money
        )
        ORDER BY tr.name;
        """

    try:
        cur.execute(sql)
    except (db.Error, db.Warning) as e:
        return [(str(e), ""),]
    try:
        return cur.fetchall()
    except TypeError as e:
        print(str(e))
        return None

def bestClient(x):
    # create a new connection
    con=connection()

    cur=con.cursor()

    client_list = [("first_name", "last_name", "total_countries_visited", "total_cities_visited", "list_of_attractions")]

    try:
        best_clients = get_best_clients(cur)

        for client in best_clients:
            # get the credentials of the client
            id, name, surname = client
            
            # get the number of countries and cities visited (using the id)
            num_of_countries, num_of_cities = get_num_of_visited(cur, id)

            # get the attractions visited (using the id)
            attraction_list = get_attractions(cur, id)

            # combine all the info about the client
            client_list.append((name, surname, num_of_countries, num_of_cities, attraction_list))

        return client_list

    # close connection to database
    finally:
        con.close()


####################### Q4 - giveAway #######################

class client_packages:
    def __init__(self, id, packages, discount, gender, name, surname):
        self.name      = name
        self.id        = id
        self.packages = packages
        self.discount  = discount
        self.gender    = gender
        self.name      = name
        self.surname   = surname

class winning_package:
    def __init__(self, id, name , surname, gender, location, discount):
        self.idd      = id
        self.name     = name
        self.surname  = surname
        self.gender   = gender
        self.location = location
        self.discount = discount

class winning_offer:
    def __init__(self, gender, name, surname, offer_desc, date, price, offer_id, loc_name, discount, package_id):
        self.gender     = gender
        self.name       = name
        self.surname    = surname
        self.date       = date
        self.offer_desc = offer_desc
        self.price      = price
        self.offer_id   = offer_id
        self.loc_name   = loc_name
        self.discount   = discount
        self.package_id = package_id

def get_packages(cur, id):
    """
    This function returns the packages the client has not been into.

    Args:
        cur: Database cursor.
        id: The id of the client.

    Returns:
        The list [(<package_id, location1>, <package_id, location2>, ..].
    """
    
    sql = """
        SELECT tr.trip_package_id, d.name
        FROM trip_package tr, destination d, trip_package_has_destination tphd
        WHERE tphd.trip_package_trip_package_id = tr.trip_package_id AND tphd.destination_destination_id = d.destination_id AND NOT EXISTS (
            SELECT *
            FROM reservation res
            WHERE res.Customer_id = {0} AND tr.trip_package_id = res.offer_trip_package_id 
        );
        """.format(id)

    try:
        cur.execute(sql)
    except (db.Error, db.Warning) as e:
        return [(str(e), ""),]
    try:
        packages = cur.fetchall()

        # convert the list of tupples into a list
        package_list = list()
        for p in packages: package_list.append((p[0], p[1]))
        return package_list
    
    except TypeError as e:
        print(str(e))
        return None

def get_offer(cur, id):
    """
    This function returns an offer with the package id.

    Args:
        cur: Database cursor.
        id: The id of the locaiton.

    Returns:
        An offer id.
    """
    
    sql = """
        SELECT o.offer_id, o.description, o.cost, o.offer_end, o.trip_package_id
        FROM offer o
        WHERE {0} = o.trip_package_id;
        """.format(id)

    try:
        cur.execute(sql)
    except (db.Error, db.Warning) as e:
        return [(str(e), ""),]
    try:
        offers = cur.fetchall()

        # return a random offer for the specific package
        return random.choice(offers)
    except TypeError as e:
        print(str(e))
        return None

def find_next_id(cur):
    """
    This function finds the next id.

    Args:
        cur: Database cursor.

    Returns:
        An id.
    """

    sql = """
        SELECT MAX(offer_id) + 1 from offer;
        """
    
    try:
        cur.execute(sql)
    except (db.Error, db.Warning) as e:
        return [(str(e), ""),]

    # get query result
    try:
        return int(cur.fetchall()[0][0])
    except TypeError as e:
        print(str(e))
        return None

def get_clients(cur):
    """
    This function finds the clients.

    Args:
        cur: Database cursor.

    Returns:
        A list containing the winners.
    """

    # get customer info & 1 if he has more than 1 reservations - 0 if not
    sql = """
        SELECT traveler_id, tr.name, tr.surname, tr.gender, count(tr.traveler_id) > 1
        FROM traveler tr, reservation res
        WHERE tr.traveler_id = res.Customer_id
        GROUP BY tr.traveler_id;
        """
    try:
        cur.execute(sql)
    except (db.Error, db.Warning) as e:
        return [(str(e), ""),]
    # get query result
    try:
        return list(cur.fetchall())
    except TypeError as e:
        print(str(e))
        return None

def get_winners(cur, N, clients):
    """
    This function finds the winners of giveaway.

    Args:
        clients: The clients.
        N: The number of the winners.

    Returns:
        A list containing the winners.
    """

    # get customer info & 1 if he has more than 1 reservations - 0 if not
    number_of_clients = len(clients)
    winning_clients = list()
    for i in range(N):
        winning_client = clients.pop(random.randint(0, number_of_clients-i-1))
        winning_clients.append(client_packages(winning_client[0], get_packages(cur, winning_client[0]), winning_client[4], winning_client[3], winning_client[1], winning_client[2]))

    return (winning_clients, clients)

def insert_customer(cur, con, id, start_date, end_date, price, o, category):
    """
    This function inserts a customer in the database.

    Args:
        cur: Database cursor.
        con: Database connection.
        start_date: The start date of the offer.
        end_date: The end date of the offer.
        price: The price of the offer.
        o: The offer.
        category: The category of the offer.
    """

    insert = """
        INSERT INTO offer (offer_id, offer_start, offer_end, cost, description, trip_package_id, offer_info_category)
        VALUES ({0}, '{1}', '{2}', {3}, '{4}', {5}, '{6}');
        """.format(id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), price, o.offer_desc, o.package_id, category)

    try:
        cur.execute(insert)
        con.commit()
        return True
        
    except (db.Error, db.Warning) as e:
        print(str(e))
        return False

def giveAway(N):
    if not N: raise Exception("Error! No number of clients was given.")
    N = int(N)

    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    cur=con.cursor()
    
    result = [("Winners", )]
    clients = get_clients(cur)
    client_package, clients = get_winners(cur, N, clients)
    
    taken_pack = list()

    # list of winning clients with their packages
    winnin_res_pack = list()
    search_failed = False
    for cl in client_package:
        
        package = cl.packages

        # search for package
        package_found = False
        for p in package:
            if p[0] not in taken_pack:
                package_found = True
                winnin_res_pack.append(winning_package(cl.id, cl.name, cl.surname, cl.gender, p, cl.discount))
                taken_pack.append(p[0])
                break
        
        if package_found == False and search_failed == False: # check if there is a winning client with no available locations to visit
            search_failed = True
            if 1 <= len(clients):
                new_cl, clients = get_winners(cur, 1, clients)
                client_package.append(new_cl[0])

    winning_offers = list()

    for w in winnin_res_pack:
        offer = get_offer(cur, w.location[0])

        winning_offers.append(winning_offer(w.gender, w.name, w.surname, offer[1], offer[3], offer[2], offer[0], w.location[1], w.discount, offer[4]))

    for o in winning_offers:
        category = None
        price    = None

        # find price and category
        if o.discount == 0:
            price = o.price
            category = 'full-price'
        else:
            price = round(0.75*o.price, 2)
            category = 'group-discount'

        # find next available key 
        id = find_next_id(cur)

        # find start and end date
        start_date = datetime.date.today()
        end_date   = start_date + datetime.timedelta(days=14)

        # insert customer to the database
        insert_customer(cur, con, id, start_date, end_date, price, o, category)

        # find the correct pronoun
        pronoun = None
        if o.gender == "male": pronoun = "Mr"
        else: pronoun = "Ms"

        # create & return message
        s = """
            Congratulations {0} {1} {2}!
            Pack your bags and get ready to enjoy the {3}! At ART TOUR travel we
            acknowledge you as a valued customer and we've selected the most incredible
            tailor-made travel package for you. We offer you the chance to travel to {4} at the incredible price of {5}. Our offer ends on {6}. Use code
            OFFER{7} to book your trip. Enjoy these holidays that you deserve so much!
            """.format(pronoun, o.name, o.surname, o.offer_desc, o.loc_name, price, end_date, id)
        
        result.append((s, ))
    
    # close connection to database
    con.close()

    return result
