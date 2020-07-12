

# web server config
listen_host = '0.0.0.0'
listen_port = 5004

# redis config
redis_persist = {
    "host": "localhost",
    "port": 6379,
    "db_number": 1
}

redis_cache = {
    "host": "localhost",
    "port": 6379,
    "db_number": 0,
    "expire": 10      # tiempo en segundos que dura el cache en Redis
}

#short url host
# ejemplo myhost = "http://myhost.com".  Si se deja en blanco lo completa automáticamente con la ip de la interfaz eth0
myhost = ""
