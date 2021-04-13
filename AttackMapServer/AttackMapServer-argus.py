#!/usr/bin/python3

"""
AUTHOR: Matthew May - mcmay.web@gmail.com
"""

# Imports
import json
import redis
import tornadoredis
#import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
#import re

from os import getuid, path
from sys import exit


# Look up service colors
service_rgb = {
                'FTP':'#ff0000',
                'SSH':'#ff8000',
                'TELNET':'#ffff00',
                'EMAIL':'#80ff00',
                'WHOIS':'#00ff00',
                'DNS':'#00ff80',
                'HTTP':'#00ffff',
                'HTTPS':'#0080ff',
                'SQL':'#0000ff',
                'SNMP':'#8000ff',
                'SMB':'#bf00ff',
                'AUTH':'#ff00ff',
                'RDP':'#ff0060',
                'DoS':'#ff0000',
                'ICMP':'#ffcccc',
                'OTHER':'#6600cc'
                }


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(request):
        request.render('index.html')

class DataHandler(tornado.web.RequestHandler):
    # @tornado.web.asynchronous
    def post(self):
        with open("../DataServer/available_infos.json", "r") as f:
            alarm_dict = json.load(f)
        alarm_id = self.get_argument("alarm_id")
        print(alarm_id)
        alarm_id = str(alarm_id)
        json_data = alarm_dict[alarm_id]
        print(json_data)

        if "prefix" in json_data:
            prefix = json_data["prefix"]
        else:
            prefix = None

        if "attacker" in json_data:
            attacker = json_data["attacker"]
        else:
            attacker = None

        if "victim" in json_data:
            victim = json_data["victim"]
        else:
            victim = None

        if "type" in json_data:
            attack_type = json_data["type"]
        else:
            attack_type = None

        if "normal_paths" in json_data:
            normal_paths = []
            t = json_data["normal_paths"]
            for path in t:
                normal_paths.append(path.split(" "))
        else:
            normal_paths = None

        if "abnormal_paths" in json_data:
            abnormal_paths = []
            t = json_data["abnormal_paths"]
            for path in t:
                abnormal_paths.append(path.split(" "))
        else:
            abnormal_paths = None

        if "attacker_country_code" in json_data:
            attacker_country_code = json_data["attacker_country_code"]
        else:
            attacker_country_code = None

        if "attacker_country_name" in json_data:
            attacker_country_name = json_data["attacker_country_name"]
        else:
            attacker_country_name = None

        if "victim_country_code" in json_data:
            victim_country_code = json_data["victim_country_code"]
        else:
            victim_country_code = None

        if "victim_country_name" in json_data:
            victim_country_name = json_data["victim_country_name"]
        else:
            victim_country_name = None

        if "normal_path_geos" in json_data:
            normal_path_geos = json_data["normal_path_geos"]
        else:
            normal_path_geos = None

        if "abnormal_path_geos" in json_data:
            abnormal_path_geos = json_data["abnormal_path_geos"]
        else:
            abnormal_path_geos = None

        if "index" in json_data:
            index = json_data['index']
        else:
            index = None

        if "timestamp" in json_data:
            timestamp = json_data["timestamp"]
        else:
            timestamp = None

        msg_to_send = {
            "timestamp" : timestamp,
            "alarm_id" : index,
            "prefix": prefix,
            "attacker": attacker,
            "victim": victim,
            "attack_type": attack_type,
            "normal_paths": normal_paths,
            "abnormal_paths": abnormal_paths,
            "attacker_country_code": attacker_country_code,
            "attacker_country_name": attacker_country_name,
            "victim_country_code": victim_country_code,
            "victim_country_name": victim_country_name,
            "normal_path_geos": normal_path_geos,
            "abnormal_path_geos": abnormal_path_geos
        }
        self.write(json.dumps(msg_to_send))
        self.finish()


class WebSocketChatHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(WebSocketChatHandler, self).__init__(*args,**kwargs)
        self.listen()

    def check_origin(self, origin):
        return True

    @tornado.gen.engine
    def listen(self):

        print('[*] WebSocketChatHandler opened')

        try:
            # This is the IP address of the DataServer
            self.client = tornadoredis.Client('127.0.0.1')
            self.client.connect()
            print('[*] Connected to Redis server')
            yield tornado.gen.Task(self.client.subscribe, 'attack-map-production')
            self.client.listen(self.on_message)
        except Exception as ex:
            print('[*] Could not connect to Redis server.')
            print('[*] {}'.format(str(ex)))

    def on_close(self):
        print('[*] Closing connection.')

    # This function is called everytime a Redis message is received
    def on_message(self, msg):

        if len(msg) == 0:
            print ("msg == 0\n")
            return None

        if 'ip_blocked' in msg:
          ip = re.split(":",msg)

        try:
            json_data = json.loads(msg.body)
        except Exception as ex:
            return None

        # print(json_data)

        if "prefix" in json_data:
            prefix = json_data["prefix"]
        else:
            prefix = None

        if "attacker" in json_data:
            attacker = json_data["attacker"]
        else:
            attacker = None

        if "victim" in json_data:
            victim = json_data["victim"]
        else:
            victim = None

        if "type" in json_data:
            attack_type = json_data["type"]
        else:
            attack_type = None

        if "normal_paths" in json_data:
            normal_paths = []
            t = json_data["normal_paths"]
            for path in t:
                normal_paths.append(path.split(" "))
        else:
            normal_paths = None

        if "abnormal_paths" in json_data:
            abnormal_paths = []
            t = json_data["abnormal_paths"]
            for path in t:
                abnormal_paths.append(path.split(" "))
        else:
            abnormal_paths = None

        if "attacker_country_code" in json_data:
            attacker_country_code = json_data["attacker_country_code"]
        else:
            attacker_country_code = None

        if "attacker_country_name" in json_data:
            attacker_country_name = json_data["attacker_country_name"]
        else:
            attacker_country_name = None

        if "victim_country_code" in json_data:
            victim_country_code = json_data["victim_country_code"]
        else:
            victim_country_code = None

        if "victim_country_name" in json_data:
            victim_country_name = json_data["victim_country_name"]
        else:
            victim_country_name = None

        if "normal_path_geos" in json_data:
            normal_path_geos = json_data["normal_path_geos"]
        else:
            normal_path_geos = None

        if "abnormal_path_geos" in json_data:
            abnormal_path_geos = json_data["abnormal_path_geos"]
        else:
            abnormal_path_geos = None

        if "index" in json_data:
            index = json_data['index']
        else:
            index = None

        if "timestamp" in json_data:
            timestamp = json_data["timestamp"]
        else:
            timestamp = None

        msg_to_send = {
            "timestamp" : timestamp,
            "alarm_id" : index,
            "prefix": prefix,
            "attacker": attacker,
            "victim": victim,
            "attack_type": attack_type,
            "normal_paths": normal_paths,
            "abnormal_paths": abnormal_paths,
            "attacker_country_code": attacker_country_code,
            "attacker_country_name": attacker_country_name,
            "victim_country_code": victim_country_code,
            "victim_country_name": victim_country_name,
            "normal_path_geos": normal_path_geos,
            "abnormal_path_geos": abnormal_path_geos
        }

        self.write_message(json.dumps(msg_to_send))

def main():
    # Register handler pages
    handlers = [
                (r'/data/', DataHandler),
                (r'/websocket', WebSocketChatHandler),
                (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'}),
                (r'/flags/(.*)', tornado.web.StaticFileHandler, {'path': 'static/flags'}),
                (r'/', IndexHandler)
                ]
    
    # Define the static path
    #static_path = path.join( path.dirname(__file__), 'static' )

    # Define static settings
    settings = {
                #'static_path': static_path
                }

    # Create and start app listening on port 8888
    try:
        app = tornado.web.Application(handlers, **settings)
        app.listen(8888)
        print('[*] Waiting on browser connections...')
        tornado.ioloop.IOLoop.instance().start()
    except Exception as appFail:
        print(appFail)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nSHUTTING DOWN')
        exit()
