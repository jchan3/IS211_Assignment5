#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Docstring for Joe Chan: simulation.py."""


import urllib2
import argparse
import csv


class Queue(object):
    """A Printer class definition."""

    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)


class Server(object):
    """A Printer class definition."""

    def __init__(self):
        """Constructor for the Printer() class.

        Attributes:
            current_request (Request): A pseudo-private attribute.
            time_remaining (int): A pseudo-private attribute.
        """
        self.current_request = None
        self.time_remaining = 0

    def tick(self, curr_time):
        """A function that moves time forward one second."""
        if self.current_request != None:
            new_time = self.time_remaining + curr_time
            self.time_remaining = 0
            if self.time_remaining <= 0:
                self.current_request = None
        return new_time

    def busy(self):
        """A function that determines if the Server object is busy."""
        if self.current_request != None:
            return True
        else:
            return False

    def start_next(self, new_request):
        """A function that assigns a new Request object to the Server object."""
        self.current_request = new_request
        self.time_remaining = new_request.get_ptime()


class Request(object):
    """A Request class definition."""

    def __init__(self, rtime, filereq, ptime):
        """Constructor for the Request() class.

        Attributes:
            timestamp (int): A pseudo-private attribute assigned to the
            constructor variable rtime.
            filereq (string): A pseudo-private attribute assigned to the
            constructor variable filereq.
            ptime (int): A pseudo-private attribute assigned to the
            constructor variable ptime.
        """
        self.timestamp = rtime
        self.filereq = filereq
        self.ptime = ptime

    def get_rtime(self):
        """A function that returns the timestamp attribute."""
        return self.timestamp

    def get_filereq(self):
        """A function that returns the filereq attribute."""
        return self.filereq

    def get_ptime(self):
        """A function that returns the ptime attribute."""
        return self.ptime

    def wait_time(self, curr_time):
        """A function that returns the current-time subtracted by the timestamp
            attribute."""
        wait = curr_time - self.timestamp
        if wait < 0:
            return 0
        else:
            return wait


def simulateOneServer(urlstr):
    """Open and read a CSV file found at a website URL and return the wait time
        averages.

    Args:
        urlstr(string): The website whose data will be read and interpreted.

    Returns:
        float: The average wait time of the requests to the server.
    """
    lab_server = Server()
    server_queue = Queue()
    waiting_times = []

    try:
        response = urllib2.urlopen(urlstr)
        reader = csv.reader(response)
    except urllib2.HTTPError as e:
        print "The server could not fulfill the request."
        print "Error code: ", e.code
    except urllib2.URLError as e:
        print "We failed to reach a server."
        print "Reason: ", e.reason
    else:
        for line in reader:
            request_time = int(line[0])
            file_req = line[1]
            process_time = int(line[2])
            request = Request(request_time, file_req, process_time)
            server_queue.enqueue(request)

    current_second = 0

    while not server_queue.is_empty():
        next_request = server_queue.dequeue()
        lab_server.start_next(next_request)
        waiting_times.append(next_request.wait_time(current_second))
        if (next_request.wait_time(current_second)) == 0:
            oldtime = next_request.get_rtime()
        else:
            oldtime = current_second
        current_second = lab_server.tick(oldtime)

    average_wait = ((float(sum(waiting_times))) / len(waiting_times))
    return average_wait


def simulateManyServers(urlstr, numservers):
    """Open and read a CSV file found at a website URL and return the wait time
        averages.

    Args:
        urlstr(string): The website whose data will be read and interpreted.
        numservers(int): The number of server objects available.

    Returns:
        float: The average wait time of the requests to the server.
    """
    main_queue = Queue()
    lab_server_list = [None] * numservers
    qlist = [None] * numservers
    waiting_times = []

    for a in range(numservers):
        qlist[a] = Queue()
        lab_server_list[a] = Server()

    try:
        response = urllib2.urlopen(urlstr)
        reader = csv.reader(response)
    except urllib2.HTTPError as e:
        print "The server could not fulfill the request."
        print "Error code: ", e.code
    except urllib2.URLError as e:
        print "We failed to reach a server."
        print "Reason: ", e.reason
    else:
        for line in reader:
            request_time = int(line[0])
            file_req = line[1]
            process_time = int(line[2])
            request = Request(request_time, file_req, process_time)
            main_queue.enqueue(request)

    while not main_queue.is_empty():
        for i in range(numservers):
            if not main_queue.is_empty():
                temp_request = main_queue.dequeue()
                qlist[i].enqueue(temp_request)

    for j in range(numservers):
        current_second = 0
        while not qlist[j].is_empty():
            next_request = qlist[j].dequeue()
            lab_server_list[j].start_next(next_request)
            waiting_times.append(next_request.wait_time(current_second))
            if (next_request.wait_time(current_second)) == 0:
                oldtime = next_request.get_rtime()
            else:
                oldtime = current_second
            current_second = lab_server_list[j].tick(oldtime)

    average_wait = ((float(sum(waiting_times))) / len(waiting_times))
    return average_wait


if __name__ == "__main__":
    #url = "http://s3.amazonaws.com/cuny-is211-spring2015/requests.csv"

    parser = argparse.ArgumentParser(description="Enter URL address")
    parser.add_argument("-u", "--url",
                        help="Enter a URL linking to a csv file.")
    parser.add_argument("-n", "--num", help="Enter the number of servers.",
                        type=int)
    args = parser.parse_args()

    if args.num and args.url:
        url = args.url
        num = args.num
        avg_wait = simulateManyServers(url, num)
        print "Average Wait time is: %6.2f secs." %(avg_wait)
    elif args.url:
        url = args.url
        avg_wait = simulateOneServer(url)
        print "Average Wait time is: %6.2f secs." %(avg_wait)
