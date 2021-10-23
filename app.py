import re
import secrets, os
import dbConnect
from flask import Flask, jsonify, render_template, request, session, redirect
from flask_session import Session
from werkzeug.utils import secure_filename

import enviarEmail

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(20)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = './static/images/upload'
Session(app)

# Instanciar módulo de conexión a la base de datos
conn = dbConnect

@app.route('/')
def login():
    return render_template('Login.html')


@app.route('/Index', methods=['GET', 'POST'])
def Index():
    if conn.validarContrasena(request.form["email"], request.form["password"]) is not False:
        session["username"] = request.form["email"]
        session["userType"] = conn.validarTipoUsuario(request.form["email"])
        datosusuarios=conn.obtenerDatosUsuario(request.form["email"])
        
        session["usuario"] = (datosusuarios['id_persona'],datosusuarios['nombre_persona'],datosusuarios['apellido_persona'],
                              datosusuarios['imagen_src']) 
        consultaProductos=conn.listaProductos()
        consultaProveedor=conn.listaProveedores()
        return render_template('Index.html', userType=session["userType"],usuario=session["usuario"],consultaProductos=consultaProductos,
                               consultaProveedor=consultaProveedor)
    else:
        session["username"] = None
        return redirect('/')


@app.route('/Home')
def Home():
    if not session.get("username"):
        return redirect("/")
    else:
        # Consulta para el index, aqui se realizaran dos consultas, Productos y proveedores.
        # La consulta productos retorna: 'nombre producto', 'Proveedor', 'disponibles', 'imagen_src','fecha_creado
        # La consulta proveedores retorna: 'nombre proveedor', 'imagen_src','fecha_creado'
        # Cada consulta se guarda en una variable distinta
        consultaProductos=conn.listaProductos()
        consultaProveedor=conn.listaProveedores()

        # return render_template('Index.html', userType=session["userType"],consultaProductos=consultaProductos,consultaProveedor=consultaProveedor)
        return render_template('Index.html', userType=session["userType"],usuario=session["usuario"],consultaProductos=consultaProductos,
                               consultaProveedor=consultaProveedor)


@app.route('/Productos', methods=['POST', 'GET'])
def Productos():
    if not session.get("username"):
        return redirect("/")
    else:
        # Consulta para productos retorna:(id,nombre_producto,proveedor,disponibles,descripcion,calificacion,imagen_src)
        print(conn.listaProductos())
        lista=conn.listaProductos()
        # lista=""
        return render_template('Productos.html',lista=lista)

@app.route('/Listas', methods=['POST', 'GET'])
def Listas():
    if not session.get("username"):
        return redirect("/")
    else:
        return render_template('Listas.html')


@app.route('/Configuracion', methods=['POST', 'GET'])
def Configuracion():
    if not session.get("username"):
        return redirect("/")
    else:
        if request.method == 'POST':
            
            datosusuarios=conn.obtenerDatosUsuarioById(request.form["id-user"])
            if(datosusuarios['descripcion_rol']=="admin"):
                datosusuarios['descripcion_rol']="Administrador"
            elif(datosusuarios['descripcion_rol']=="superAdmin"):
                datosusuarios['descripcion_rol']="Super administrador"
            else:
                datosusuarios['descripcion_rol']="Usuario";
                    
            return render_template('User.html',datosusuarios=datosusuarios)


@app.route('/Proveedores', methods=['POST', 'GET'])
def Proveedores():
    if not session.get("username"):
        return redirect("/")
    else:
        # Consulta para productos retorna:(id,nombre_proveedor,descripcion,imagen_src)
        lista=conn.listaProveedores()
        print(lista)
        return render_template('Proveedores.html',lista=lista)


@app.route('/Usuarios', methods=['POST', 'GET'])
def Usuarios():
    if not session.get("username"):
        return redirect("/")
    else:
        
        if session.get("userType")=='admin' or session.get("userType")=='superAdmin':
            ListaUsuarios = conn.obtenerListaDeUsuarios()
            
            for x in range(len(ListaUsuarios)):
                if(ListaUsuarios[x]['descripcion_rol']=="admin"):
                    ListaUsuarios[x]['descripcion_rol']="Administrador"
                elif(ListaUsuarios[x]['descripcion_rol']=="superAdmin"):
                    ListaUsuarios[x]['descripcion_rol']="Super administrador"
                else:
                    ListaUsuarios[x]['descripcion_rol']="Usuario";
                
            return render_template('Usuarios.html',ListaUsuarios=ListaUsuarios)
        else:
            return render_template('AccessDenied.html')

@app.route('/Logout', methods=['POST', 'GET'])
def Logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/Editarproducto', methods=['POST', 'GET'])
def Editarproducto():
    if not session.get("username"):
        return redirect("/")
    else:
        
        if request.method == 'POST':
            
            if request.form.get('submit_button') == 'editar':
                id=request.form['id']
                # Aqui se recibe el id del producto para su busqueda en la base de datos, esta retorna los datos
                # del producto
                
                # codigo temporal, se reemplaza por los datos de la consulta, solo para pruebas
                id=1
                nombre_producto="Motor toyota"
                proveedor="Contactamos S.A."
                descripcion="Motor para camionetas 2.0"
                cantidad="20"
                calificacion="4"
                image_src="/static/images/avatar.png"
               
                
                resultado1=(id,nombre_producto,proveedor,descripcion,cantidad,calificacion,image_src)
                return render_template('EditarProducto.html',resultado1=resultado1)
            
            elif request.form.get('submit_button') == 'eliminar':
                id=request.form['id']
                # consulta para eliminar producto
                print("Boton eliminar")
                
            elif request.form.get('submit_button')=='Añadir +':
                # Formulario en blanco para añadir producto
                id=""
                nombre_producto=""
                proveedor=""
                descripcion=""
                cantidad=""
                calificacion=""
                image_src="/static/images/proveedor.png"                            #Para pruebas
                resultado1=(id,nombre_producto,proveedor,descripcion,cantidad,calificacion,image_src)
                # return render_template('AdminUser.html',resultado1=resultado1)
                
            elif request.form.get('submit_button') == 'Disponible':
                id=request.form['id']
                # consulta para eliminar producto
                print("Boton eliminar")
            elif request.form.get('submit_button') == 'No disponible':
                id=request.form['id']
                # consulta para eliminar producto
                print("Boton eliminar")
        return render_template('EditarProducto.html')


@app.route('/AdminUser', methods=['POST', 'GET'])
def AdminUser():
    if not session.get("username"):
        return redirect("/")
    else:
        if request.method == 'POST':
            
            if request.form.get('submit_button') == 'editar':
                id=request.form['id']
                # Aqui se recibe el id del usuario para su busqueda en la base de datos, esta retorna los datos
                # del usuario
                datosusuarios=conn.obtenerDatosUsuarioById(request.form["id"])
                
                if(datosusuarios['descripcion_rol']=="admin"):
                    datosusuarios['descripcion_rol']="Administrador"
                elif(datosusuarios['descripcion_rol']=="superAdmin"):
                    datosusuarios['descripcion_rol']="Super administrador"
                else:
                    datosusuarios['descripcion_rol']="Usuario";
                
                
                return render_template('AdminUser.html',datosusuarios=datosusuarios)
            
            elif request.form.get('submit_button') == 'eliminar':
                print("Boton eliminar")
            elif request.form.get('submit_button')=='Añadir usuario +':
                id=""
                nombre=""
                apellido=""
                tipoUser="Usuario"
                email=""
                telefono=""
                contrasena=""
                image_src="/static/images/avatar.png"                            
                datosusuarios=[{'id_proveedor': 1, 'nombre_proveedor': 'Contactamos S.A.', 'descripcion_proveedor': 'Proveedor de llantas y amortiguadores', 'src_imagen': 'urlToImage.jpg'}]
                
                return render_template('AdminUser.html',datosusuarios=datosusuarios)
    # return render_template('AdminUser.html')


@app.route('/EditarLista', methods=['POST', 'GET'])
def EditarLista():
    if not session.get("username"):
        return redirect("/")
    else:
        return render_template('EditarListas.html')


@app.route('/EditarProveedores', methods=['POST', 'GET'])
def EditarProveedores():
    if not session.get("username"):
        return redirect("/")
    else:
        
        if request.method == 'POST':
            
            if request.form.get('submit_button') == 'editar':
                id=request.form['id']
                # Aqui se recibe el id del proveedor para su busqueda en la base de datos, esta retorna los datos
                # del usuario
                datosProveedor=conn.obtenerProveedorById(request.form['id'])
                
               
                return render_template('EditarProveedor.html',datosProveedor=datosProveedor)
            
            elif request.form.get('submit_button') == 'eliminar':
                id=request.form['id']
                # consulta para eliminar proveedor
                print("Boton eliminar")
                
            elif request.form.get('submit_button')=='Añadir +':
                # Formulario en blanco para añadir proveedor
                id=""
                nombre_proveedor="Motor toyota"
                descripcion="Motor para camionetas 2.0"
                image_src="/static/images/proveedor.png"                            #Para pruebas
                
                resultado1=(id,nombre_proveedor,descripcion,image_src)
                return render_template('EditarProveedor.html',resultado1=resultado1)
        

@app.route('/RecuperarPass', methods=['POST', 'GET'])
def RecuperarPass():
    if conn.validarUsuario(request.form["recuperarEmail"]) is not False:
        datosUsuario = conn.obtenerDatosUsuario(request.form['recuperarEmail'])
        nombreApellido = datosUsuario['nombre_persona'] + " " + datosUsuario['apellido_persona']
        datosEmail = enviarEmail.prepararEmail(datosUsuario['email'], nombreApellido, datosUsuario['id_usuario'])
        response = enviarEmail.enviarCorreo(datosEmail)

    return str(response)

@app.route('/NewPass')                      
def NewPass():
    
    return render_template('CambiarContrasena.html')        

@app.route('/ConfirmacionNewPass')
def ConfirmacionNewPass():
    return render_template('Login.html')

@app.route('/CambiarPass', methods=['POST', 'GET'])
def CambiarPass():
    if not session.get("username"):
        return redirect("/")
    else:
        if request.method == 'POST':
            if request.form['submit_button'] == 'Cambiar contraseña':
                return redirect("/Home")

# Guardar datos de los usuarios. Llega des la pagina adminUser
@app.route('/GuardarUser', methods=['POST', 'GET'])
def GuardarUser():
    
    if not session.get("username"):
        return redirect("/")
    else:
        if session.get("userType")=='admin' or session.get("userType")=='superAdmin':
            if request.method == 'POST':
                if request.form['submit_button'] == 'Guardar':
                    id=request.form['id']
                    nombre=request.form['nombre']
                    apellido=request.form['apellido']
                    tipoUser=request.form['selectedUsuario']    
                    if(tipoUser=="Administrador"):
                        tipoUser="admin"
                    elif(tipoUser=="Super administrador"):
                        tipoUser="superAdmin"
                    else:
                        tipoUser="usuario"; 

                    email=request.form['email']
                    telefono=request.form['telefono']
                    
                    image_src=request.files['archivo']            
                
                    if id=="":
                        
                        if image_src.filename !="":
                            image_src=uploader()            #Retorna Foto.png
                            image_src="/static/images/upload/"+image_src
                            
                        else:
                            image_src="/static/images/avatar.png"   # Si no se selecciona ninguna imagen, establece la imagen por defecto
                        
                        #Consulta para insert en la base de datos
                        
                    else:
                        if image_src.filename !="":
                            
                            image_src=uploader()            #Retorna Foto.png
                            image_src="/static/images/upload/"+image_src
                        
                            #Consulta para update en la base de datos cambiando la imagen por la seleccionada en el momento
                            
                        else:
                            #Consulta para update en la base de datos sin incluir imagen, permanece la actual
                            
                            pass 
                
                    # Despues de realizar la query regresa a la pagina de usuarios 
                    return redirect('/Usuarios')
                
                elif request.form['submit_button'] == 'Restablecer contraseña usuario':
                    # Codigo para enviar correo con la contraseña nueva
                    return redirect('/Usuarios')
                elif request.form['submit_button'] == 'Cancelar':
                    return redirect('/Usuarios')
        else:
            return render_template('AccessDenied.html')
        
# Guardar datos del productos. Llega des la pagina Editar productos
@app.route('/GuardarProducto', methods=['POST', 'GET'])
def GuardarProducto():
    if not session.get("username"):
        return redirect("/")
    else:
        if request.method == 'POST':
            id=request.form.get('id')
            # f = request.files['archivo']
            # imagen = secure_filename(f.filename)
            nombreProducto = request.form.get("name")
            
            proveedor = request.form.get('category')
            descripcion =request.form.get("descripcion")
            cantidad=request.form.get("cantidad")
            calificacion=request.form.get("category-cal")
            return ("ok")

# Guardar datos del proveedor. Llega des la pagina Editar proveedor
@app.route('/GuardarProveedor', methods=['POST', 'GET'])
def GuardarProveedor():
    if not session.get("username"):
        return redirect("/")
    else:
        if request.method == 'POST':
            if request.form['submit_button'] == 'Guardar':
                return redirect('/Proveedores')
            elif request.form['submit_button'] == 'Cancelar':
                return redirect('/Proveedores')   
            
# Guardar configuracion de usuario. Llega desde la pagina User
@app.route('/Guardarconfiguracion', methods=['POST', 'GET'])
def Guardarconfiguracion():
    if not session.get("username"):
        return redirect("/")
    else:
        if request.method == 'POST':
        
            
            if request.form['submit_button'] == 'Guardar':
                id=request.form['id']
                telefono=request.form['telefono']
                image_src=request.files['archivo']
                if image_src.filename !="":
                    image_src=uploader()            #Retorna Foto.png
                    image_src="/static/images/upload/"+image_src
                    #Consulta para update en la base de datos cambiando la imagen por la seleccionada en el momento. Busqueda por id
                else:
                    #Consulta para update en la base de datos sin cambiar la imagen. Busqueda por id
                    pass
                
                return redirect('/Home')
            elif request.form['submit_button'] == 'Cancelar':
                
                return redirect('/Home')
            elif request.form['submit_button'] == 'Cambiar contraseña':
                id=request.form['id']
                actualpw=request.form['actualpw']
                newpw=request.form['confirnpw']
                # Consulta para cambiar la contraseña del usuario por medio de su id
                return redirect('/Home')
            else:
                return ('ok')
        return

def uploader():
    """Funcion para subir la imagen en el servidor
        
    """
    if not session.get("username"):
        return redirect("/")
    else:
    # obtenemos el archivo del input "archivo"
        f = request.files['archivo']
        filename = secure_filename(f.filename)
        # Guardamos el archivo en el directorio 
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Retornamos una respuesta satisfactoria
        return (filename)
    