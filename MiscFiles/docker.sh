# Un fisier care contine un exemplu de comenzi pentru a crea toate bazele de date pe care le folosesc eu
# Daca modifici acest fisier nu il actualiza in git
docker run -p 42069:27017 --name Mongo1 -d mongo:latest
docker run -p 42070:27017 --name Mongo2 -d mongo:latest
docker run -p 42071:27017 --name Mongo3 -d mongo:latest