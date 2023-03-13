from flask import Flask, request, render_template
from datetime import datetime
from hashlib import sha256
import json

tiempo = str(datetime.today())

class Bloque:
    #1er paso agregar nonce
    def __init__(self, index, transacciones, timestamp, hash_anterior, nonce=0):
        self.index = index
        self.transacciones = transacciones
        self.timestamp = timestamp
        self.hash_anterior = hash_anterior
        #Agregamos nonce
        self.nonce = nonce
    # paso 2 creamos una funcion que nos cripte un bloque
    def criptador(self):
        bloque_string = json.dumps(self.__dict__, sort_keys=True)

        return sha256(bloque_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.transacciones_pendientes = []
        self.cadena = []
        self.crear_bloque_genesis()

    #Paso 6

    def crear_bloque_genesis(self):
        bloque_genesis = Bloque(0,["Bloque genesis"], tiempo, "0")

        # Encriptamos el bloque genesis
        bloque_genesis.hash = bloque_genesis.criptador()
        
        self.cadena.append(bloque_genesis)
    
    @property
    def ultimo_bloque(self):
        return self.cadena[-1]
    
    # Paso 3
    #Agregamos la diicultad a nuestra Bc
    dificultad = 2

    #Creamos la funcion PoW(prueba de trabajo)
    def prueba_de_trabajo(self, bloque):
        #Comenzamos con el nonce en 0

        bloque.nonce = 0

        #criptamos el bloque para saber el hash
        bloque_criptado = bloque.criptador()

        # Comparar el hash del bloque segun el ajuste de la dificultad
        while not bloque_criptado.startswith('0'* Blockchain.dificultad):
            # vamos incrementano el nonce hasta que el hash comience con la cantiadd de ceros en la dificultad
            bloque.nonce += 1

            #Criptamos el bloque con el nuevo valor del nonce
            bloque_criptado = bloque.criptador()

        return bloque_criptado
    
    # Paso 4
    def prueba_de_trabajo_es_validada(self, bloque, hash_del_bloque):
        return(hash_del_bloque.startswith('0'* Blockchain.dificultad) and
            hash_del_bloque == bloque.criptador())

    # Paso 5
    # agregar la validacion al agregar el bloque
    def agregar_bloque(self, bloque, prueba):
        #Traemos el hash anterior
        hash_anterior = self.ultimo_bloque.hash
        
        #Si el hash es diferente al hash del bloque anterior nos devuelve False
        if hash_anterior != bloque.hash_anterior:
            return False

        #Si no se valida que nos retorne falso tambien
        if not self.prueba_de_trabajo_es_validada(bloque, prueba):
            return False
        
        #Guardamos la prueba
        bloque.hash = prueba
        self.cadena.append(bloque)
        return True
    
    def agregar_transacciones(self, transaccion):
        self.transacciones_pendientes.append(transaccion)

    # Paso 7
    def cerrar_bloque(self):
        if not self.transacciones_pendientes:
            return False
        
        ultimo_bloque = self.ultimo_bloque

        # definimos cada parametro y modificamos para que nos traiga el ultimo hash
        nuevo_bloque = Bloque(ultimo_bloque.index + 1, transacciones=self.transacciones_pendientes, timestamp=tiempo, hash_anterior=ultimo_bloque.hash)

        # Agregamos la prueba que hicimos anteriormente
        prueba = self.prueba_de_trabajo(nuevo_bloque)
        
        # Al agregar el nuevo bloque tambien debe entregar la prueba
        self.agregar_bloque(nuevo_bloque, prueba)
        self.transacciones_pendientes = []
        return nuevo_bloque.index
    
    ## Comienza el flask ##


app = Flask(__name__)

pengucoin = Blockchain()


@app.route('/')
def index():
    return render_template('base.html')

@app.route('/cerrar', methods=['GET', 'POST'])
def minar():
    if request.method == 'POST':
        pengucoin.cerrar_bloque()
    return render_template('minar.html')

@app.route('/transaccion/nueva', methods=['GET', 'POST'])
def nueva_transaccion():
    if request.method == 'POST':
        transaccion = request.form['nueva_transaccion']
        nueva_transaccion = pengucoin.agregar_transacciones(transaccion)
    
        return render_template('transaccion_nueva.html'), nueva_transaccion
    return render_template('transaccion_nueva.html')


@app.route('/cadena', methods=['GET'])
def cadena_completa():
    cadena = []
    for bloque in pengucoin.cadena:
        cadena.append(bloque.__dict__)
    
    return render_template('cadena.html', cadena=cadena)
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)