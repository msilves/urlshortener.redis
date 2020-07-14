from flask import Flask, redirect, request, render_template, make_response
from flask_restful import Resource, Api
import redis, sys, shortuuid, yaml
import netifaces as ni

# Abro la configuración desde el archivo configy.yml que está en el mismo folder que la app
file = open('config.yml', 'r')
cfg = yaml.load(file, Loader=yaml.FullLoader)

#short url host
if( cfg['myhost']=="" ):
    ni.ifaddresses('eth0')
    server_ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
    myhost="http://" + server_ip


app = Flask(__name__)
api = Api(app)
redis_cache = redis.Redis(host = cfg['redis_cache']['host'], port = cfg['redis_cache']['port'], db = cfg['redis_cache']['db_number'])
redis_persist = redis.Redis(host = cfg['redis_persist']['host'], port = cfg['redis_persist']['port'], db = cfg['redis_persist']['db_number'])

class setup(Resource): # La uso en /api/short_url/.  Implementa el agregado y borrado de urls
    def get(self):
        headers = {'Content-Type': 'text/html'}
        output = {}
        for key in redis_persist.keys():
            key = key.decode('ascii')
            #print(key)
            value =  redis_persist.get(key).decode('ascii') + ' ; ' + str(redis_persist.ttl(key))
            short_url = myhost + '/' + key
            output[short_url] = value # esta función es para lab únicamente, en un entrno real con una base grande podría llenar la memoria
        return make_response(render_template('index.html', result = output),200,headers) # devuelve una table html con los valores de todas las keys y values

    def post(self):
        
        long_url = request.json['VALUE']
        # print(long_url)
        
        shortener = URL_Shortener()
        short_url = shortener.shorten_url(long_url)

        # print(long_url + "," + myhost + "/" + short_url)
        return myhost + "/" + short_url

    def delete(self):
        short_url = request.json['VALUE']
        redis_persist.delete(short_url)
        redis_cache.delete(short_url)
        return('Done')

class short2long(Resource): # La uso en /<short_url>.  Toma la short url que viene del get y devuelve la long url asociada
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
        redis_cache.setex(short_url, cfg['redis_cache']['expire'], long_url) # Resetea el timeout del cache (expira en expire_cache segundos).  Esta escritura tiene un costo alto que no es aconsejable mantener con utilización alta
        print(long_url)
        return redirect(long_url)
        
class print_short2long(Resource):  #La uso en /api/short_url/<short_url>.  No encontré la forma de meterla en la clase setup
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
        for key in redis_persist.keys(): # Verifico si la url ya existe en la base.  Este chequeo está deprecado si se usa una función determinística, lo dejo por si lo cambio por hash o implemento un control de duplicados
            key = key.decode('ascii')
            value = redis_persist.get(key).decode('ascii')

            if(value == long_url):
                short_url = key # la long_url se encontró en la base
    
        if(short_url == ""): # la long_url no se encontró en la base
            short_url = shortuuid.uuid(name=long_url)
        if(cfg['redis_persist']['expire'] == ""):
            redis_persist.set(short_url,long_url)
        else:
            redis_persist.setex(short_url, cfg['redis_persist']['expire'], long_url)  # Si existía igualmente reescribe el TTL
        return str(short_url)
    
    

api.add_resource(short2long, '/<short_url>')
api.add_resource(setup, '/api/short_url/')
api.add_resource(print_short2long, '/api/short_url/<short_url>')


if __name__ == '__main__':
    app.run(host=cfg['listen_host'], port=cfg['listen_port'])

