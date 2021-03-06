try:
    import usocket as socket
except:
    import socket

response_404 = """HTTP/1.0 404 NOT FOUND

<h1>404 Not Found</h1>
"""

response_500 = """HTTP/1.0 500 INTERNAL SERVER ERROR

<h1>500 Internal Server Error</h1>
"""
response_template = """HTTP/1.0 200 OK

%s
"""
import machine
import ntptime
import utime
from machine import RTC
from time import sleep

rtc = RTC()
try:
    seconds = ntptime.time()
except:
    seconds = 0
rtc.datetime(utime.localtime(seconds))

# time view
def time():
    body = """<html>
<body>
<h1>Time</h1>
<p>%s</p>
</body>
</html>
""" % str(rtc.datetime())

    return response_template % body

# dummy view
def dummy():
    body = "This is a dummy endpoint"
    return response_template % body

# routing dictionary for different view functions.
handlers = {
    'time': time,
    'dummy': dummy,
}

def main():
    s = socket.socket()
    ai = socket.getaddrinfo("0.0.0.0", 8080)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(addr)
    s.listen(5)
    print("Listening, connect your browser to http://", end='')
    print(addr)

    while True:
        sleep(.5)
        print("Before accept")
        res = s.accept()
        client_s = res[0]
        client_addr = res[1]
        req = client_s.recv(4096)
        print("Request:")
        print(req)

        # This first line of a request looks like "GET /arbitrary/path/ HTTP/1.1 "
        # It has three parts and seperated by a space char (' ').
        # So the first part is the GET method, second is the path, the third is the
        # HTTP version used. We only need the second part.
        # The first line of a request is: req.decode().split('\r\n')[0]
        # The second part of first line is:
        # req.decode().split('\r\n')[0].split(" ")[1]
        try:
            path = req.decode().split('\r\n')[0].split(' ')[1]
            # the path like /dummy/dog/, we want to only get 'dummy'
            # so we need to strip slashes from the left or right side of the path.
            # and then get the first string from the remaining path.
            handler = handlers[path.strip('/').split('/')[0]]
            # if the handler is 'dummy', then we will call dummy().
            response = handler()
        except KeyError:
            response = response_404
        except Exception as e:
            response = response_500
            print(str(e))

        client_s.send(b"\r\n".join([line.encode() for line in response.split("\n")]))

        client_s.close()
        print()

main()
