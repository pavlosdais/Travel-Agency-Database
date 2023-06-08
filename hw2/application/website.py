import sys, os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
from bottle import route, run, static_file, request
import settings
import app

def renderTable(tuples):
    printResult = """<style type='text/css'> h1 {color:red;} h2 {color:blue;} p {color:green;} </style>
    <table border = '1' frame = 'above'>"""

    header='<tr><th>'+'</th><th>'.join([str(x) for x in tuples[0]])+'</th></tr>'
    data='<tr>'+'</tr><tr>'.join(['<td>'+'</td><td>'.join([str(y) for y in row])+'</td>' for row in tuples[1:]])+'</tr>'
        
    printResult += header+data+"</table>"
    return printResult

@route('/findTrips')
def findTrips():
    x = request.query.x
    a = request.query.a
    b = request.query.b
    table = app.findTrips(x,a,b)
    return "<html><body>" + renderTable(table) + "</body></html>"
	

@route('/findRevenue')
def findRevenue():
    x = request.query.x  
    table = app.findRevenue(x)
    return "<html><body>" + renderTable(table) + "</body></html>"
	
@route('/bestClient')
def bestClient():
    x = request.query.x
    table = app.bestClient(x)
    return "<html><body>" + renderTable(table) + "</body></html>"

@route('/giveAway')
def giveAway():
    N = request.query.N    
    table = app.giveAway(N)
    return "<html><body>" + renderTable(table) + "</body></html>"

 
@route('/:path')
def callback(path):
    return static_file(path, 'web')

@route('/')
def callback():
    return static_file("index.html", 'web')

run(host='localhost', port=settings.web_port, reloader=True, debug=True)