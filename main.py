import psycopg2
from flask import Flask, jsonify, request

###Enunciados##
#-------------#
# Login
# Crear proyecto
# Asignar gestor a proyecto
# Asignar cliente a proyecto
# Crear tareas a proyecto
# Asignar programador a proyecto
# Asignar programadores a tareas
# Obtener programadores
# Obtener proyectos (activos o todos)
# Obtener tareas de un proyecto


def ejecutar_sql(consulta: str):
    connection = psycopg2.connect(
        host="localhost",
        port="5432",
        dbname="alexsoft",
        user="postgres",
        password="postgres",
        options="-c search_path=public"
    )
    cursor = connection.cursor()
    cursor.execute(consulta)
    columnas = [desc[0] for desc in cursor.description]
    resultados = cursor.fetchall()
    empleados = [dict(zip(columnas, fila)) for fila in resultados]
    connection.close()

    return empleados

app = Flask(__name__)

#1.Login
@app.route('/gestor/login', methods=['POST'])
def login():
    body_request = request.json
    user = body_request["user"]
    passwd = body_request["passwd"]

    query = f'''
    SELECT *
    FROM public."Gestor"
    WHERE usuario = '{user}' AND passwd = '{passwd}';
    '''
    logged = ejecutar_sql(query)
    if len(logged) == 0:
        return jsonify({"msg": "Credenciales incorrectas"}), 401

    empleado_id = logged[0].get("empleado")
    empleado = ejecutar_sql(
        f"SELECT * FROM public.\"Empleado\" WHERE id = '{empleado_id}';"
    )
    if len(empleado) == 0:
        return jsonify({"msg": "Empleado no encontrado"}), 404

    return jsonify(
        {
            "id_empleado": empleado[0]["id"],
            "id_gestor": logged[0]["id"],
            "nombre": empleado[0]["nombre"],
            "email": empleado[0]["email"],
        }
    )

#2.Crear proyecto
@app.route('/crear/proyecto', methods=['POST'])
def nuevo_proyecto():
    try:
        body_request = request.json
        nombre = body_request['nombre']
        descripcion = body_request['descripcion']
        fecha_inicio = body_request['fecha_inicio']
        fecha_finalizacion = body_request['fecha_finalizacion']
        cliente = body_request['cliente']

        query = f'''
        INSERT INTO public."Proyecto" (
            nombre, descripcion, fecha_creacion, fecha_inicio, fecha_finalizacion, cliente
        ) VALUES (
            '{nombre}',
            '{descripcion}',
            CURRENT_TIMESTAMP,
            '{fecha_inicio}',
            '{fecha_finalizacion}',
            {cliente}
        )
        RETURNING id;
        '''
        proyecto = ejecutar_sql(query)

        return jsonify({"id": proyecto[0]['id'], "mensaje": "Proyecto creado exitosamente"}), 201

    except psycopg2.Error as e:
        return jsonify({"error": "Error al crear proyecto", "detalles": str(e)}), 500

#3.Asignar gestor a proyecto
@app.route('/asignar/gestor', methods=['POST'])
def asignar_gestor():
    try:
        body_request = request.json
        gestor_id = body_request['gestor']
        proyecto_id = body_request['proyecto']

        query_gestor = 'SELECT id FROM public."Gestor" WHERE id = {gestor_id};'
        gestor = ejecutar_sql(query_gestor)
        if not gestor:
            return jsonify({"error": "Gestor no encontrado"}), 404

        query_proyecto = 'SELECT id FROM public."Proyecto" WHERE id = {proyecto_id};'
        proyecto = ejecutar_sql(query_proyecto)
        if not proyecto:
            return jsonify({"error": "Proyecto no encontrado"}), 404

        query_asignar = f'''
        INSERT INTO public."GestoresProyecto" (gestor, proyecto, fecha_asignacion)
        VALUES ({gestor_id}, {proyecto_id}, CURRENT_TIMESTAMP);
        '''
        ejecutar_sql(query_asignar)

        return jsonify({"mensaje": f"Gestor {gestor_id} asignado al proyecto {proyecto_id}"}), 201

    except psycopg2.Error as e:
        return jsonify({"error": "Error al asignar gestor", "detalles": str(e)}), 500

#4.Asignar cliente a proyecto
@app.route('/asignar/cliente', methods=['POST'])
def asignar_cliente():
   try:
       body_request = request.json
       nombre_proyecto = body_request['nombre']
       descripcion = body_request['descripcion']
       fecha_inicio = body_request['fecha_inicio']
       fecha_finalizacion = body_request['fecha_finalizacion']
       cliente_id = body_request['cliente']

       query_cliente = f'SELECT id FROM public."Cliente" WHERE id = {cliente_id};'
       cliente = ejecutar_sql(query_cliente)
       if not cliente:
           return jsonify({"error": "Cliente no encontrado"}), 404

       query_asignar = f'''
       INSERT INTO public."Proyecto" (nombre, descripcion, fecha_creacion, fecha_inicio, fecha_finalizacion, cliente)
       VALUES (
           '{nombre_proyecto}', 
           '{descripcion}', 
            CURRENT_TIMESTAMP, 
           '{fecha_inicio}', 
           '{fecha_finalizacion}', 
            {cliente_id}
        );'''

       ejecutar_sql(query_asignar)
       return jsonify({"mensaje": f"Cliente {cliente_id} asignado al proyecto '{nombre_proyecto}'"}), 201

   except psycopg2.Error as e:
       return jsonify({"error": "Error al asignar cliente", "detalles": str(e)}), 500

#5.Crear tareas a proyecto
@app.route('/crear/tareas', methods=['POST'])
def crear_tarea():
   try:
       body_request = request.json
       nombre = body_request['nombre']
       descripcion = body_request['descripcion']
       estimacion = body_request['estimacion']
       fecha_creacion = body_request['fecha_creacion']
       fecha_finalizacion = body_request['fecha_finalizacion']
       programador_id = body_request['programador']
       proyecto_id = body_request['proyecto']

       query_proyecto = f'SELECT id FROM public."Proyecto" WHERE id = {proyecto_id};'
       proyecto = ejecutar_sql(query_proyecto)
       if not proyecto:
           return jsonify({"error": "Proyecto no encontrado"}), 404

       query_programador = f'SELECT id FROM public."Programador" WHERE id = {programador_id};'
       programador = ejecutar_sql(query_programador)
       if not programador:
           return jsonify({"error": "Programador no encontrado"}), 404


       query_crear = f'''
       INSERT INTO public."Tarea" (nombre, descripcion, estimacion, fecha_creacion, fecha_finalizacion, programador, proyecto)
       VALUES (
           '{nombre}', 
           '{descripcion}', 
            {estimacion}, 
            '{fecha_creacion}', 
            '{fecha_finalizacion}', 
            {programador_id}, 
            {proyecto_id}
       );'''

       ejecutar_sql(query_crear)
       return jsonify({"message": "Tarea creada exitosamente"}), 201

   except psycopg2.Error as e:
       return jsonify({"error": "Error al crear tarea", "detalles": str(e)}), 500

#6.Asignar programador a proyecto
@app.route('/asignar/programador', methods=['POST'])
def asignar_programador():
    try:
        body_request = request.json
        programador_id = body_request['programador']
        proyecto_id = body_request['proyecto']

        query_programador = f'SELECT id FROM public."Programador" WHERE id = {programador_id};'
        programador = ejecutar_sql(query_programador)
        if not programador:
            return jsonify({"error": "Programador no encontrado"}), 404

        query_proyecto = 'SELECT id FROM public."Proyecto" WHERE id = {proyecto_id};'
        proyecto = ejecutar_sql(query_proyecto)
        if not proyecto:
            return jsonify({"error": "Proyecto no encontrado"}), 404

        query_asignar = f'''
        INSERT INTO public."ProgramadoresProyecto" (programador, proyecto, fecha_asignacion)
        VALUES ({programador_id}, {proyecto_id}, CURRENT_TIMESTAMP);
        '''
        ejecutar_sql(query_asignar)

        return jsonify({"mensaje": f"Programador {programador_id} asignado al proyecto {proyecto_id}"}), 201

    except psycopg2.Error as e:
        return jsonify({"error": "Error al asignar programador", "detalles": str(e)}), 500

#7.Asignar programador a tarea
@app.route('/asignar_programador_a_tarea', methods=['POST'])
def asignar_programador_tarea():
    try:
        body_request = request.json
        programador_id = body_request['programador']
        tarea_id = body_request['tarea']

        query_programador = f'''
        SELECT id FROM public."Programador" WHERE id = {programador_id};
        '''
        programador = ejecutar_sql(query_programador)
        if not programador:
            return jsonify({"error": "Programador no encontrado"}), 404

        query_tarea = f'''
        SELECT id FROM public."Tarea" WHERE id = {tarea_id};
        '''
        tarea = ejecutar_sql(query_tarea)
        if not tarea:
            return jsonify({"error": "Tarea no encontrada"}), 404

        query_asignar = f'''
        UPDATE public."Tarea"
        SET programador = {programador_id}
        WHERE id = {tarea_id};
        '''
        ejecutar_sql(query_asignar)

        return jsonify({"mensaje": f"Programador {programador_id} asignado a la tarea {tarea_id} exitosamente"}), 200

    except psycopg2.Error as e:
        return jsonify({"error": "Error al asignar programador a tarea", "detalles": str(e)}), 500

#8.Obtener programadores
@app.route('/empleado/programadores',methods=['GET'])
def obtener_programadores():
   try:
       programadores = ejecutar_sql(
           """
           SELECT * FROM public."Programador"
           ORDER BY id ASC
           """
       )
       return jsonify(programadores)

   except psycopg2.Error as e:
       return jsonify({"error": "Error al obtener programadores", "detalles": str(e)}), 500

#9.Obtener proyectos
@app.route('/proyecto/proyectos', methods=['GET'])
def obtener_proyectos():
    try:
        query = '''
        SELECT * FROM public."Proyecto"
        ORDER BY id ASC 
        '''
        proyectos = ejecutar_sql(query)

        return jsonify(proyectos)

    except psycopg2.Error as e:
        return jsonify({"error": "Error al obtener proyectos", "detalles": str(e)}), 500

#10.Obtener tareas
@app.route('/tareas',methods=['GET'])
def obtener_tareas():
   try:
       body_request = request.json
       proyecto_id = body_request['id']
       tareas = ejecutar_sql(
           f"""
           SELECT * FROM public."Tarea" t
           WHERE t.proyecto = {proyecto_id}
           """
       )
       return jsonify(tareas)

   except psycopg2.Error as e:
       return jsonify({"error": "Error al obtener tareas", "detalles": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)