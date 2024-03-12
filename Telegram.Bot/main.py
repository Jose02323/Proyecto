import  telebot #Manejar la API de Telegram
import web
import requests
from DB import database
from telebot import types 
from telebot.types import ReplyKeyboardMarkup #crear botones 
from datetime import datetime, timedelta #Tiempo de entrega
from geopy.distance import geodesic #Ubicar direccion

#Conexion con el bot
fecha = datetime.now().strftime('%d-%m-%Y')
TOKEN = '6849232672:AAEvaH5OTfBwyNYd-jL0raJRq8FnfA02xms'
bot = telebot.TeleBot(TOKEN)
pedido = []
total_pedido = 0
datos_cliente = {}
platos_seleccionados = []
detalle_plato = {}
detalles_pedido = []
detalles_por_plato = {} 

#comandos para opciones
@bot.message_handler(content_types=['text'])
def pregunta_opciones(message):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, input_field_placeholder='Selecciona una opción: ',resize_keyboard=True)
    markup.add('Menu', 'Direccion', 'Informacion')
    msg_welcome = bot.send_message(message.chat.id, 'Bienvenido al restaurante ABC \n Si desea ver nuestros platos oprima Menú \n Si desea ver la información del Restaurant oprima Información \n Si necesitas saber la Dirección de nuestro local oprime Dirección ', reply_markup=markup)
    bot.register_next_step_handler(msg_welcome, seleccion_boton)

def seleccion_boton(message):
    if message.text == "Menu":
        image_url = 'https://firebasestorage.googleapis.com/v0/b/databaserestaurante-6d2c7.appspot.com/o/menu%2Fmenu.png?alt=media&token=f8c2e589-2d97-4078-bb84-57faf4644d9a'
        response = requests.get(image_url)

        # Verifica si la descarga fue exitosa
        if response.status_code == 200:
            # Abre la imagen descargada en modo binario
            with open('menu.png', 'wb') as f:
                # Escribe los datos de la imagen descargada en el archivo local
                f.write(response.content)
            # Abre el archivo local y envía la imagen al usuario
            with open('menu.png', 'rb') as menu:
                bot.send_photo(message.chat.id, menu)

        markup = ReplyKeyboardMarkup(one_time_keyboard=True, input_field_placeholder='Selecciona una opción:  ',resize_keyboard=True)
        markup.add('Empezar Pedido', 'Atras')
        msg = bot.send_message(message.chat.id, 'Para iniciar el pedido oprime en Empezar Pedido', reply_markup=markup)
        bot.register_next_step_handler(msg, opciones_menu)  

    elif message.text == "Atras":
        bot.send_message(message.chat.id, "Volviendo atrás...")
        pregunta_opciones(message)
           
        
    elif message.text == "Direccion":
        msg = bot.send_location(message.chat.id, -0.11336903701952591, -78.50789376399999)
        markup = ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
        markup.add('Atras')
        msg = bot.send_message(message.chat.id, 'Si deseas regresar a las anteriores opciones oprime Atrás', reply_markup=markup)
        bot.register_next_step_handler(msg, opciones_menu)  

        if message.text == "Atras":
            bot.send_message(message.chat.id, "Volviendo atrás...")
            pregunta_opciones(message)
                
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            # Agrega el botón "Atras" al teclado
            keyboard.add(types.KeyboardButton('Atras'))


    elif message.text == "Informacion":
        msg = bot.send_message(message.chat.id, "Información Crucial que se quiera agregar sobre el restaurante")
        markup = ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
        markup.add('Atras')
        msg = bot.send_message(message.chat.id, 'Si deseas regresar a las anteriores opciones oprime Atrás', reply_markup=markup)
        bot.register_next_step_handler(msg, opciones_menu)  

        if message.text == "Atras":
            bot.send_message(message.chat.id, "Volviendo atrás...")
            pregunta_opciones(message)
                
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            # Agrega el botón "Atras" al teclado
            keyboard.add(types.KeyboardButton('Atras'))

cantidad_opciones_seleccionadas = 0

def opciones_menu(message):
    global cantidad_opciones_seleccionadas
    global precio_plato

    if message.text == "Empezar Pedido":
        btn_pedido = ReplyKeyboardMarkup(one_time_keyboard=True, input_field_placeholder='Selecciona una opción: ',resize_keyboard=True)
        btn_pedido.add('Siguiente', 'Cancelar')
        
        platos_ref = database.child('Menu').child('Tipo_Plato').get()

        botones_menu = types.InlineKeyboardMarkup(row_width=2)

        if platos_ref:
            for plato in platos_ref.each():
                nombre_plato = plato.key()  # Obtiene el nombre del plato
                precio_plato = plato.val()
                
                # Crea un botón para cada plato
                btn_plato = types.InlineKeyboardButton(nombre_plato, callback_data=nombre_plato)
                botones_menu.add(btn_plato)

        bot.send_message(message.chat.id, "Si quieres seleccionar un plato, presiona una vez en cada botón del plato para agregarlo a tu pedido ", reply_markup=botones_menu)
        msg = bot.send_message(message.chat.id, 'Si ya tienes tu pedido listo, presiona Siguiente: ', reply_markup=btn_pedido)
        bot.register_next_step_handler(msg, datos_cliente)

    elif message.text == "Atras":
        bot.send_message(message.chat.id, "Volviendo atrás...")
        pregunta_opciones(message)

    
@bot.callback_query_handler(func=lambda call: True)
def agregar_plato(call):
    global platos_seleccionados
    global total_pedido
    global cantidad_opciones_seleccionadas


    if cantidad_opciones_seleccionadas >= 6:
        bot.answer_callback_query(call.id, "Ya has seleccionado el máximo de opciones permitidas.")

    plato_seleccionado = call.data
    precio_plato = obtener_precio_plato(plato_seleccionado)
    database.child("Pedido").push({"plato": plato_seleccionado, "fecha": fecha, "Total": precio_plato})

    if precio_plato is not None:
        platos_seleccionados.append(plato_seleccionado)
        total_pedido += precio_plato
        bot.answer_callback_query(callback_query_id=call.id, text='Plato agregado al pedido')
        bot.register_next_step_handler(call, gestion_pedido)
    else:
        bot.send_message(call.message.chat.id, "No se pudo obtener el precio del plato seleccionado.")

    cantidad_opciones_seleccionadas += 1

# Restablecer el contador cuando se realiza un nuevo pedido
cantidad_opciones_seleccionadas = 0

def obtener_precio_plato(plato_seleccionado):
    try:
        plato_ref = database.child('Menu').child('Tipo_Plato').child(plato_seleccionado).get()
        if plato_ref:
            return plato_ref.val()  # Retorna el precio del plato
        else:
            return None
    except Exception as e:
        print("Error al obtener el precio del plato:", e)
        return None

def datos_cliente(message_cliente):
    if message_cliente.text == "Siguiente":
        msg = bot.send_message(message_cliente.chat.id, "Para registrar el pedido.\nIngresa tu nombre, apellido y número de cédula separados por espacio ")
        bot.register_next_step_handler(msg, guardar_datos_cliente)
        
    elif message_cliente.text == "Cancelar":
        bot.send_message(message_cliente.chat.id, "Pedido cancelado.")
    else:
        bot.send_message(message_cliente.chat.id, "Comando no válido. Por favor, selecciona 'Siguiente' o 'Cancelar'.")

def guardar_datos_cliente(message):
    global datos_cliente

    # Validar que la entrada del cliente tenga el formato correcto
    datos_ingresados = message.text.strip().split()

    if len(datos_ingresados) != 3:
        # Si no se ingresaron los tres campos, solicitar que se ingrese los datos nuevamente
        msg = bot.send_message(message.chat.id, "Debes ingresar nombre, apellido y número de cédula separados por espacios.")
        bot.register_next_step_handler(msg, guardar_datos_cliente)
        return

    nombre, apellido, cedula = datos_ingresados

    if len(nombre) < 2 or len(apellido) < 2 or len(cedula) < 10 or not nombre.isalpha() or not apellido.isalpha() or not cedula.isdigit():
        # Si alguno de los campos no cumple con las condiciones, solicitar que se ingrese los datos nuevamente
        msg = bot.send_message(message.chat.id, "Los datos ingresados no son válidos. Por favor ingresa datos reales.")
        bot.register_next_step_handler(msg, guardar_datos_cliente)
        return

    datos_cliente = {"nombre": nombre, "apellido": apellido, "cedula": cedula}
    database.child("Cliente").child("Datos_Cliente").push(datos_cliente)
    
    # Redirigir al manejo del pedido
    manejar_pedido(message)

def manejar_pedido(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Editar Pedido', 'Detalles Pedido')
    msg = bot.send_message(message.chat.id, 'Si deseas ver tu pedido oprime en Detalles Pedido \nSi deseas Editar algo de tu pedido Selecciona Editar Pedido', reply_markup=markup)
    bot.register_next_step_handler(msg, gestion_pedido)

def gestion_pedido(message):
    global platos_seleccionados
    global total_pedido

    if message.text == "Detalles Pedido":
        if platos_seleccionados:
            resumen_pedido = ""
            for plato in platos_seleccionados:
                detalle = ", ".join(detalles_por_plato.get(plato, ['Sin detalles']))
                resumen_pedido += f"{plato}: {detalle}\n"


            resumen_pedido += f"Total: ${total_pedido}\n\n"
            resumen_pedido += f"Datos del Cliente:\nNombre: {datos_cliente['nombre']}\nApellido: {datos_cliente['apellido']}\nCédula: {datos_cliente['cedula']}"

            try:
                # Guarda el pedido en Firebase
                database.child("Venta").child("Datos_Venta").push(resumen_pedido)
                mensaje_confirmacion = f"Detalles del Pedido\n\nResumen del pedido:\n{resumen_pedido}"
                bot.send_message(message.chat.id, mensaje_confirmacion)
                ofrecer_opciones_entrega(message)
                return  # Sale de la función después de procesar el pedido
            except Exception as e:
                print("Error al guardar el resumen del pedido en Firebase:", e)
                bot.send_message(message.chat.id, "Hubo un error al procesar tu pedido. Por favor, inténtalo de nuevo más tarde.")
        else:
            bot.send_message(message.chat.id, "No hay platos seleccionados en el pedido.")
    elif message.text == "Editar Pedido":
        mostrar_opciones_edicion(message)

def mostrar_opciones_edicion(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Editar plato', 'Eliminar plato', 'Cancelar')
    msg = bot.send_message(message.chat.id, "Selecciona una opción: \n Seleccione Editar plato si desea agregar algún detalle a un plato seleccionado anteriormente \n Seleccione Eliminar plato si desea eliminar algún plato seleccionado \n Seleccione Cancelar si desea Cancelar el pedido", reply_markup=markup)
    bot.register_next_step_handler(msg, procesar_opcion_edicion)

def procesar_opcion_edicion(message):
    opcion = message.text.lower()
    if opcion == 'editar plato':
        mostrar_menu_agregar(message)
    elif opcion == 'eliminar plato':
        mostrar_menu_eliminar(message)
    elif opcion == 'cancelar':
        bot.send_message(message.chat.id, "Edición de pedido cancelada.")
    else:
        msg = bot.send_message(message.chat.id, "Opción no válida. Por favor, selecciona una opción válida.")
        bot.register_next_step_handler(msg, procesar_opcion_edicion)

def mostrar_menu_agregar(message):
    global platos_seleccionados
    
    if platos_seleccionados:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for plato in platos_seleccionados:
            markup.add(plato)
        markup.add('Cancelar')
        msg = bot.send_message(message.chat.id, "Selecciona un plato para agregar un detalle o presiona Cancelar:", reply_markup=markup)
        bot.register_next_step_handler(msg, agregar_detalles)
    else:
        bot.send_message(message.chat.id, "No hay platos seleccionados para agregar detalles.")

def agregar_detalles(message):
    global platos_seleccionados

    plato_seleccionado = message.text
    if plato_seleccionado in platos_seleccionados:
        msg = bot.send_message(message.chat.id, f"Ingrese los detalles para '{plato_seleccionado}':")
        bot.register_next_step_handler(msg, lambda m: procesar_detalles(m, plato_seleccionado))

def procesar_detalles(message, plato_seleccionado):
    global detalles_por_plato

    # Verifica si el plato ya tiene detalles registrados
    if plato_seleccionado not in detalles_por_plato:
        detalles_por_plato[plato_seleccionado] = []

    detalles_por_plato[plato_seleccionado].append(message.text)
    bot.send_message(message.chat.id, f"Detalles para '{plato_seleccionado}' actualizados correctamente.")
    mostrar_opciones_confirmacion(message)



def mostrar_opciones_confirmacion(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Detalles Pedido', 'Editar Pedido', 'Cancelar Pedido', 'Confirmar Pedido')
    msg = bot.send_message(message.chat.id, 'Selecciona una opción', reply_markup=markup)
    bot.register_next_step_handler(msg, detalle_cancelar_pedido)

def detalle_cancelar_pedido(message):
    if message.text == 'Detalles Pedido':
        gestion_pedido(message)

    elif message.text == 'Editar Pedido':
        mostrar_opciones_edicion(message)

    elif message.text == 'Cancelar Pedido':
        cancelar_pedido(message)

    elif message.text == 'Confirmar Pedido':
        Confirmacion_de_Pedido(message)

    elif message.text == "Gracias":
        msg = bot.send_message(message.chat.id, 'Gracias por Preferirnos')
        
    else:
        bot.send_message(message.chat.id, 'Opción no válida. Por favor, selecciona una opción válida.')


def mostrar_menu_eliminar(message):
    global platos_seleccionados
    
    if platos_seleccionados:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for plato in platos_seleccionados:
            markup.add(plato)
        markup.add('Cancelar')
        msg = bot.send_message(message.chat.id, "Selecciona un plato que deseas eliminar de tu pedido:", reply_markup=markup)
        bot.register_next_step_handler(msg, eliminar_plato)
    else:
        bot.send_message(message.chat.id, "NTu pedido está vacío. No hay platos para eliminar.")


def eliminar_plato(message):
    global total_pedido

    plato_seleccionado = message.text
    if plato_seleccionado in platos_seleccionados:
        # Obtener el precio del plato seleccionado
        precio_plato_seleccionado = obtener_precio_plato(plato_seleccionado)
        if precio_plato_seleccionado:
            platos_seleccionados.remove(plato_seleccionado)
            total_pedido -= precio_plato_seleccionado
            bot.send_message(message.chat.id, f"Plato '{plato_seleccionado}' eliminado del pedido.")
            mostrar_opciones_confirmacion(message)
        else:
            bot.send_message(message.chat.id, "No se encontró el precio del plato seleccionado.")
    else:
        bot.send_message(message.chat.id, "El plato seleccionado no está en tu pedido.")

    
def reiniciar_pedido():
    # Reinicia el estado del pedido
    global pedido, total_pedido, datos_cliente
    pedido = []
    total_pedido = 0
    datos_cliente = {}

def mostrar_opciones_eliminar(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Editar Menú', 'Detalles Pedido', 'Volve a Editar')
    msg = bot.send_message(message.chat.id, 'Si desea ver el detalle del pedido seleccione Detalle Pedido\n Si deseas Editar tu pedido Selecciona Editar Pedido', reply_markup=markup)
    bot.register_next_step_handler(msg, detalle_cancelar_pedido)


def ofrecer_opciones_entrega(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Confirmar Pedido', 'Editar Pedido', 'Cancelar Pedido')
    msg = bot.send_message(message.chat.id, 'Selecciona una opción', reply_markup=markup)
    bot.register_next_step_handler(msg, detalle_cancelar_pedido)
    

def Confirmacion_de_Pedido(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('A domicilio', 'Retiro en el local', 'Editar Pedido', 'Cancelar Pedido')
    msg = bot.send_message(message.chat.id, '¿Cómo deseas recibir tu pedido?', reply_markup=markup)
    bot.register_next_step_handler(msg, procesar_opcion_entrega)


def procesar_opcion_entrega(message):
    
    opcion_entrega = message.text.lower()
    if opcion_entrega in ['a domicilio', 'retiro en el local']:
  
        if opcion_entrega == 'a domicilio':
            #lógica para la entrega a domicilio
            bot.send_message(message.chat.id, 'Por favor envíanos tu ubicación para calcular el tiempo de entrega.')
            bot.register_next_step_handler(message, calcular_tiempo_entrega)
        elif opcion_entrega == 'retiro en el local':
            bot.send_message(message.chat.id, 'En un aproximado de 15 minutos puedes pasar a retirar tu pedido en nuestro local.')
    elif message.text == 'Cancelar Pedido':
            cancelar_pedido(message)
    elif message.text == 'Editar Pedido':
            mostrar_opciones_edicion(message)
    else:
        msg = bot.send_message(message.chat.id, "Opción no válida. Por favor, selecciona una opción válida.")
        bot.register_next_step_handler(msg, procesar_opcion_entrega)


def calcular_tiempo_entrega(message):
    global cliente_location
    
    latitude = message.location.latitude
    longitude = message.location.longitude
    cliente_location = (latitude, longitude)
    database.child("Venta").child("Datos_Venta").push(cliente_location)
    
    # Coordenadas del restaurante
    restaurante_location = (-0.19478812288503225, -78.49143748799729)
    
    # Calcular la distancia entre el restaurante y la ubicación del cliente
    distancia = geodesic(restaurante_location, cliente_location).kilometers
    
    # Calcular el tiempo de entrega estimado (suponiendo una velocidad promedio de 30 km/h)
    tiempo_entrega_horas = distancia / 30
    tiempo_entrega_minutos = tiempo_entrega_horas * 60

    # Agregar 15 minutos al tiempo estimado de entrega
    tiempo_entrega_minutos += ((tiempo_entrega_minutos // 15) + 1) * 15

    # Calcular horas y minutos
    horas_entrega = int(tiempo_entrega_minutos // 60)
    minutos_entrega = int(tiempo_entrega_minutos % 60)

    # Calcular el costo del envío por cada 20 minutos
    costo_envio_por_bloque = 2
    costo_envio_total = ((tiempo_entrega_minutos // 20) + 1) * costo_envio_por_bloque

    if tiempo_entrega_minutos > 40:
        # Mensaje de tiempo de entrega alto
        tiempo_adicional = int(tiempo_entrega_minutos - 40)
        mensaje = f"El tiempo de entrega es de {horas_entrega} horas y {minutos_entrega} minutos, lo cual excede los 40 minutos habituales."
        mensaje += f"\nEl costo de envío adicional es de ${costo_envio_total}. ¿Deseas continuar?"
    else:
        # Mensaje de tiempo de entrega dentro del límite
        mensaje = f"El tiempo estimado de entrega es de {horas_entrega} horas y {minutos_entrega} minutos."
        mensaje += f"\nEl costo de envío adicional es de ${costo_envio_total}. ¿Deseas continuar?"

    # Enviar mensaje al cliente con las opciones de confirmar o cancelar el pedido
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Confirmar Pedido', 'Cancelar Pedido')
    bot.send_message(message.chat.id, mensaje, reply_markup=markup)
    bot.register_next_step_handler(message, confirmacion_pedido)


def confirmacion_pedido(message):
    bot.send_message(message.chat.id, 'Pedido Confirmado gracias por tu compra')


def cancelar_pedido(message):
    #cancelar el pedido
    global pedido, total_pedido
    pedido = []
    total_pedido = 0
    bot.send_message(message.chat.id, 'Pedido cancelado.')

if __name__ == "__main__":
    bot.infinity_polling()