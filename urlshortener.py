from flask import Flask, redirect, request, render_template, make_response
from flask_restful import Resource, Api
import redis
import shortuuid
import netifaces as ni

# a ver si replica

# web server config
listen_host = '0.0.0.0'
listen_port = 5004

# redis config
redis_persist_host = '127.0.0.1'
redis_persist_port = 6379
redis_persist_db_number = 1
redis_cache_host = '127.0.0.1'
redis_cache_port = 6379
redis_cache_db_number = 0
expire_cache = 5 # tiempo en segundos que dura el cache en Redis

#short url host
ni.ifaddresses('eth0')
server_ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
myhost="http://" + server_ip

app = Flask(__name__)
api = Api(app)
redis_cache = redis.Redis(host = redis_cache_host, port = redis_cache_port, db = redis_cache_db_number)
redis_persist = redis.Redis(host = redis_persist_host, port = redis_persist_port, db = redis_persist_db_number)

class setup(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        output = {}
        for key in redis_persist.keys():
            key = key.decode('ascii')
            #print(key)
            value = redis_persist.get(key).decode('ascii')
            output[key] = value
        return make_response(render_template('index.html', result = output),200,headers)

    def post(self):
        
        long_url = request.json['URL']
        # print(long_url)
        
        shortener = URL_Shortener()
        short_url = shortener.shorten_url(long_url)

        print(long_url + "," + myhost + "/" + short_url)
        return long_url + "," + myhost + "/" + short_url

    def delete(self):
        short_url = request.json['URL']
        redis_persist.delete(short_url)
        redis_cache.delete(short_url)
        return('Done')

class short2long(Resource):
    def get(self,short_url):
        long_url = redis_cache.get(short_url)
        
        if(long_url==None):
            print("Failed Cache")
            value = redis_persist.get(short_url)
            if(value == None):
                return 'Not Found', 404
            else:
                long_url=value.decode('ascii')
        else:
            print("Matched Cache")
        redis_cache.setex(short_url, expire_cache, long_url) # expira en expire_cache segundos
        return redirect(long_url)
        
class print_short2long(Resource):
    def get(self,short_url):
        value = redis_persist.get(short_url)
        if(value == None):
            return 'Not Found', 404
        else:
            long_url=value.decode('ascii')
        return(long_url)


class URL_Shortener():
    
    def shorten_url(self, long_url):
        short_url=""
        for key in redis_persist.keys():
            key = key.decode('ascii')
            value = redis_persist.get(key).decode('ascii')

            if(value == long_url):
                short_url = key # la long_url se encontró en la base
    
        if(short_url == ""): # la long_url no se encontró en la base
            short_url = shortuuid.uuid(name=long_url)
            redis_persist.set(short_url,long_url)
            
        return str(short_url)
    
    

api.add_resource(short2long, '/<short_url>')
api.add_resource(setup, '/api/short_url/')
api.add_resource(print_short2long, '/api/short_url/<short_url>')


if __name__ == '__main__':
    app.run(host=listen_host, port=str(listen_port))

