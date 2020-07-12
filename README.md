Ejercicio de URL Shortener usando Redis como base de datos KV

La idea es crear URLs cortas que se asocien a URL largas que un administrador debe proveer por api.  Una vez asociadas, usando la URL corta en un browser automáticamente se redirige la página a la URL larga.

La api permite:
- ver todos los pares de URL corta y larga
- agregar una URL larga, devolviendo la corta
- borrar una URL corta

La api se accede a través de:
http://host/api/short-url

Para agregar una URL hay que enviar un POST con un JSON
El post se debe enviar a http://host/api/short-url
El Json debe tener este formato:
{
	"URL" : "<URL LARGA>"
}


Para borrar una URL corta ha que enviar un DELETE con un JSON
El DELETE se debe enviar a http://host/api/short-url
El Json debe tener este formato:
{
	"URL" : "<KEY>"
}

donde la KEY está contenida en la url corta de esta forma:
http://host/key
ej:
http://172.17.76.12/ANEspoZUubGZgMc2zbUXYT
donde la key es ANEspoZUubGZgMc2zbUXYT


Las key con sus respectivas URLs largas se almacenan en Redis.  En esta versión existen dos instanacias de Redis, una de cache local y otra para datos persistentes.

Pendings:
Proximo paso es probar Redis Cluster
Poner el Redis para caching local como opcional.
