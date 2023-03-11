# importar la libreria flask
from flask import Flask, jsonify, request

#importar el datetime
from datetime import datetime



tiempo = str(datetime.today())

# Crear un objeto bloque
class Bloque:
    # Inicializamos con estos atributos
    def __init__(self, index, transacciones, timestamp):
        self.index = index
        self.transacciones = transacciones
        self.timestamp = timestamp

# Crea un objeto blockchain
class Blockchain:
    # inicializar con los atributos
    def __init__(self):
        # Creamos una lista vacia para almacenar las transacciones pendientes
        self.transacciones_pendientes = []
        self.cadena = []

        # creamos el bloque genesis
        self.crear_bloque_genesis()


    #Creamos el metodo para agregar bloque genesis
    def crear_bloque_genesis(self):
        #Instanciamos el bloque genesis
        bloque_genesis = Bloque(0,["Bloque genesis"], tiempo)

        #Agrega el bloque genesis a la cadena
        self.cadena.append(bloque_genesis)
    
    # para definir la propiedad del ultimo bloque
    @property
    def ultimo_bloque(self):
        return self.cadena[-1]
    
    # nos permite agregar bloques a la cadena
    def agregar_bloque(self, bloque):
        self.cadena.append(bloque)
        return True
    
    # agrega la transaccion
    def agregar_transacciones(self, transaccion):
        self.transacciones_pendientes.append(transaccion)

    # cierre el bloque
    def cerrar_bloque(self):
        # Si no hay transacciones pendientes nos retorna False(falso)
        if not self.transacciones_pendientes:
            return False
        
        #traemos el ultimo bloque
        ultimo_bloque = self.ultimo_bloque

        #instanciamos el nuevo bloque
        # index + 1 hace que se vaya sumando el index automaticamente
        nuevo_bloque = Bloque(ultimo_bloque.index + 1, self.transacciones_pendientes, tiempo)

        #Agregamos el bloque
        self.agregar_bloque(nuevo_bloque)

        #Vaciamos la lista de transacciones pendientes ya que migraron a la cadena
        self.transacciones_pendientes = []

        return nuevo_bloque.index
    
app = Flask(__name__)

cadena = Blockchain()
# mina el bloque
@app.route('/cerrar', methods=['GET'])
def minar():
    bloque = cadena.cerrar_bloque()

    response = {
        'mensaje': "Nuevo bloque cerrado",
        'index': bloque.index,
        'transaccion': bloque.transacciones,
        'timestamp': bloque.timestamp
    }
    return jsonify(response), 200


# transaccion nueva
@app.route('/transaccion/nueva', methods=['POST'])
def nueva_transaccion():
    #Recibimos los datos
    values = request.get_json()

    #Agregamos una nueva transaccion
    index = cadena.agregar_transacciones(values['transaccion'])

    response = { 'mensaje': f'La transaccion se ha agregado correctamente'}
    return jsonify(response), 201

#Para ver la cadena completa
@app.route('/cadena', methods=['GET'])
def cadena_completa():
    cadena_completa = []

    for bloque in cadena.cadena:
        cadena_completa.append(bloque.__dict__)

    response = {
        'cadena': cadena_completa,
        'longitud': len(cadena_completa)
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)