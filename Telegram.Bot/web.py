from flask import Flask, render_template, request, redirect, url_for
import pickle
from DB import database, auth
import main

web = Flask(__name__)

@web.route("/")
def inicio():
    return render_template('inicio.html')

@web.route('/registro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        password = request.form['password']
        
        user = auth.create_user_with_email_and_password(email, password)

        database.child("Usuario").child("Datos_Usuario").push({
            'nombre': nombre,
            'apellido': apellido,
            'email': email,
        })
        return redirect(url_for('inicio'))

    return render_template('registro.html')

@web.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            id_token = user['idToken'] #se obtiene el token de autenticacion
            user_data = auth.get_account_info(id_token) #se obtiene la informacion del usuario
            user_uid = user_data['users'][0]['localId']#se obtiene el id del usuario

            return redirect(url_for('datos_pedidos'))
        
        except Exception as e:
            print("Error:", e)
            return render_template('login.html', error=str(e))
    
    return render_template('login.html')

@web.route("/pedidos")
def datos_pedidos():
    try:
        response = database.child("Venta").child("Datos_Venta").get()
        if response:
            data = response.val()
        else:
            data = {} 
        return render_template('pedidos.html', data=data)
    except Exception as e:
        return render_template('login.html', error=str(e))
    
@web.route('/graficos')
def graficos():
    return render_template('graficos.html')

@web.route('/logout')
def logout():
    return redirect('/')

if __name__ == '__main__':
    web.run(debug=True)