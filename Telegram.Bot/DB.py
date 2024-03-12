import firebase_admin
import pyrebase
from firebase_admin import credentials, firestore

config = {
    "apiKey" : "AIzaSyA9qomrhIEuRV664PU2tNOTc2lZ2VMaA8w",
    "authDomain" : "databaserestaurante-6d2c7.firebaseapp.com",
    "projectId" : "databaserestaurante-6d2c7",
    "databaseURL" : "https://databaserestaurante-6d2c7-default-rtdb.firebaseio.com/",
    "storageBucket" : "databaserestaurante-6d2c7.appspot.com",
    "messagingSenderId" : "12672102283",
    "appId" : "1:12672102283:web:5b02cc7b3840308264498e",
    "measurementId" : "G-XTL200F4XB"
} 



firebase = pyrebase.initialize_app(config)
database = firebase.database()
auth=firebase.auth()

#data = {"Nombre": "Prueba", "Apellido": "Prueba", "email": "jsajj@hotmail.com"}


#database.push(data)
#database.child("Usuario").child("Datos_Usuario").set(data)

#data = {}
#database.child("Menu").child("Tipo_Plato").push({"Nombre_Plato":"Hamburgusa Doble", "Detalle": "Hamburguesa con doble carne", "Precio": 7})
#database.child("Menu").child("Hamrburguesa Simple").push({"Detalle": "Hamburguesa con una carne", "Precio": 5})
#database.child("Menu").child("Tipo_Plato").push({"Nombre_Plato": "Alitas BBQ", "Detalle": "6 Alitas con salsa BBQ", "Precio": 5})
#database.child("Menu").child("Tipo_Plato").push({"Nombre_Plato": "Alitas Bufalo", "Detalle": "6 Alitas con salsa picante bufalo", "Precio": 7})

#database.push(data)
#database.child("Plato").set(data)
