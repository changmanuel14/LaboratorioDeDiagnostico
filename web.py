from flask import Flask, render_template, url_for, flash, redirect, request, Response, session, send_from_directory, make_response
from flask_session import Session
import os
from os import path
import pymysql
from datetime import date, datetime
import pdfkit
from operator import attrgetter

app = Flask(__name__)
app.secret_key = 'd589d3d0d15d764ed0a98ff5a37af547'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route("/hojareq")
def hojareq():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	return render_template('hojareq.html', title='Hoja de requisición', logeado=logeado, idtipouser = idtipouser)

@app.route("/inhojareq", methods=['GET', 'POST'])
def inhojareq():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select codigo, nombre, presentacion from insumos where activo = 1 order by codigo asc;"
				cursor.execute(consulta)
				insumostotales = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		solicitante = request.form['solicitante']
		carrera = request.form['carrera']
		fecha = request.form['fecha']
		cantidad = request.form['cantidad']
		curso = request.form['curso']
		semestre = request.form['semestre']
		numhojareq = request.form['numhojareq']
		numhojareq = "Hoja de requisición " + str(numhojareq)
		if(len(carrera) == 0):
			carrera = 'null'
		if(len(semestre) == 0):
			semestre = 'null'
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO egresosheader(solicitante, fecha, curso, semestre, carrera, numhojareq) VALUES (%s, %s, %s, %s, %s, %s);"
					cursor.execute(consulta, (solicitante, fecha, curso, semestre, carrera, numhojareq))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "select MAX(idegresosheader) from egresosheader;"
					cursor.execute(consulta)
					idheader = cursor.fetchall()
					idheader = idheader[0][0]
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)

		for i in range(int(cantidad)):
			aux = 'codigo' + str(i)
			codigo = request.form[aux]
			aux = 'cantidad' + str(i)
			cant = request.form[aux]
			aux = 'recibe' + str(i)
			recibe = request.form[aux]
			try:
				conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
				try:
					with conexion.cursor() as cursor:
						consulta = "select idinsumos, existencia from insumos where codigo = %s and activo = 1;"
						cursor.execute(consulta, codigo)
						idinsumo = cursor.fetchall()
						existencia = idinsumo[0][1]
						idinsumo = idinsumo[0][0]
						consulta = "INSERT INTO egresosdesc(idegresosheader, idinsumo, cantidad, inicialesrecibe, iduser) VALUES(%s, %s, %s, %s, %s);"
						cursor.execute(consulta, (idheader, idinsumo, cant, recibe, session['iduser']))
						existencia = existencia - float(cant)
						consulta = "update insumos set existencia = %s where idinsumos = %s;"
						cursor.execute(consulta, (existencia, idinsumo))
					conexion.commit()
				finally:
					conexion.close()
			except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
				print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('kardex'))
	return render_template('inhojareq.html', title='Ingreso Hoja de requisición', logeado=logeado, idtipouser = idtipouser, insumos = insumostotales)

@app.route("/inextra", methods=['GET', 'POST'])
def inextra():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select codigo, nombre, presentacion from insumos where activo = 1 order by codigo asc;"
				cursor.execute(consulta)
				insumostotales = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		razon = request.form['razon']
		fecha = request.form['fecha']
		cantidad = request.form['cantidad']
		numhojareq = request.form['numhojareq']
		#numhojareq = "Formulario de ingreso " + str(numhojareq)
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO ingresosheader(nombreordencompra, idordencompra, documento, fecha, user) VALUES (%s, null, %s, %s, %s);"
					cursor.execute(consulta, (razon, numhojareq, fecha, session['iduser']))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "select MAX(idingresosheader) from ingresosheader;"
					cursor.execute(consulta)
					idheader = cursor.fetchall()
					idheader = idheader[0][0]
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)

		for i in range(int(cantidad)):
			aux = 'codigo' + str(i)
			codigo = request.form[aux]
			aux = 'cantidad' + str(i)
			cant = request.form[aux]
			try:
				conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
				try:
					with conexion.cursor() as cursor:
						consulta = "select idinsumos, existencia from insumos where codigo = %s and activo=1;"
						cursor.execute(consulta, codigo)
						idinsumo = cursor.fetchall()
						existencia = idinsumo[0][1]
						existencia = existencia + float(cant)
						idinsumo = idinsumo[0][0]
						consulta = "INSERT INTO ingresosdesc(idheader, idinsumos, cantidad) VALUES(%s, %s, %s);"
						cursor.execute(consulta, (idheader, idinsumo, cant))
						consulta = "update insumos set existencia=%s where idinsumos = %s;"
						cursor.execute(consulta, (existencia, idinsumo))
					conexion.commit()
				finally:
					conexion.close()
			except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
				print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('kardex'))
	return render_template('inextra.html', title='Ingreso extraordinario', logeado=logeado, idtipouser = idtipouser, insumos = insumostotales)

@app.route("/inpedido", methods=['GET', 'POST'])
def inpedido():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select codigo, nombre, presentacion from insumos where activo = 1 order by codigo asc;"
				cursor.execute(consulta)
				insumostotales = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		razon = request.form['razon']
		fecha = request.form['fecha']
		cantidad = request.form['cantidad']
		numhojareq = request.form['numhojareq']
		numhojareq = "Factura " + str(numhojareq)
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO ingresosheader(nombreordencompra, idordencompra, documento, fecha, user) VALUES (%s, null, %s, %s, %s);"
					cursor.execute(consulta, (razon, numhojareq, fecha, session['iduser']))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "select MAX(idingresosheader) from ingresosheader;"
					cursor.execute(consulta)
					idheader = cursor.fetchall()
					idheader = idheader[0][0]
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)

		for i in range(int(cantidad)):
			aux = 'codigo' + str(i)
			codigo = request.form[aux]
			aux = 'cantidad' + str(i)
			cant = request.form[aux]
			try:
				conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
				try:
					with conexion.cursor() as cursor:
						consulta = "select idinsumos, existencia from insumos where codigo = %s and activo=1;"
						cursor.execute(consulta, codigo)
						idinsumo = cursor.fetchall()
						existencia = idinsumo[0][1]
						existencia = existencia + float(cant)
						idinsumo = idinsumo[0][0]
						consulta = "INSERT INTO ingresosdesc(idheader, idinsumos, cantidad) VALUES(%s, %s, %s);"
						cursor.execute(consulta, (idheader, idinsumo, cant))
						consulta = "update insumos set existencia=%s where idinsumos = %s;"
						cursor.execute(consulta, (existencia, idinsumo))
					conexion.commit()
				finally:
					conexion.close()
			except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
				print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('kardex'))
	return render_template('inpedido.html', title='Ingreso de Pedido', logeado=logeado, idtipouser = idtipouser, insumos = insumostotales)

@app.route("/kardex", methods=['GET', 'POST'])
def kardex():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	data = []
	ins = ""
	existencia = 0
	fechaactual = datetime.now()
	dia = str(fechaactual.day)
	if int(dia) < 10:
		dia = '0' + dia
	mes = str(fechaactual.month)
	if int(mes) < 10:
		mes = '0' + mes
	anio = str(fechaactual.year)
	if int(anio) < 10:
		anio = '0' + anio
	hora = str(fechaactual.hour)
	if int(hora) < 10:
		hora = '0' + hora
	minuto = str(fechaactual.minute)
	if int(minuto) < 10:
		minuto = '0' + minuto
	actual = dia + '-' + mes + '-' + anio + ' ' + hora + ':' + minuto
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select codigo, nombre, presentacion from insumos where activo = 1 order by codigo asc;"
				cursor.execute(consulta)
				insumostotales = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		codigo = request.form['codigo']
		nombre = request.form['nombre']
		ins = nombre
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "select idinsumos, existencia from insumos where activo = 1 and codigo = %s;"
					cursor.execute(consulta, codigo)
					idinsumo = cursor.fetchall()
					existencia = idinsumo[0][1]
					idinsumo = idinsumo[0][0]
					consulta = 'select concat(e.solicitante, " ",e.curso) as razon, e.numhojareq, DATE_FORMAT(e.fecha,"%d/%m/%Y"), d.cantidad, u.nombre from egresosheader e inner join egresosdesc d on e.idegresosheader = d.idegresosheader inner join users u on u.idusers = d.iduser where d.idinsumo = ' + str(idinsumo) + " order by e.fecha desc;"
					#print(consulta)
					cursor.execute(consulta)
					datae = cursor.fetchall()
					consulta = "select h.nombreordencompra, h.documento, DATE_FORMAT(h.fecha,'%d/%m/%Y'), d.cantidad, u.nombre from ingresosheader h inner join ingresosdesc d ON h.idingresosheader = d.idheader inner join users u ON h.user = u.idusers where d.idinsumos = " + str(idinsumo) + " order by h.fecha desc;"
					#print(consulta)
					cursor.execute(consulta)
					datai = cursor.fetchall()

					for i in range(len(datae)):
						aux = datae[i]
						aux = list(aux)
						aux.insert(3, " ")
						data.append(aux)
					
					for i in range(len(datai)):
						aux = datai[i]
						aux = list(aux)
						aux.insert(4, " ")
						data.append(aux)
					
					cantdata = len(data)

					for i in range(cantdata-1):
						for j in range(cantdata-i-1):
							dia1, mes1, anio1 = [int(x) for x in data[j][2].split('/')]
							dia2, mes2, anio2 = [int(x) for x in data[j+1][2].split('/')]
							fecha1 = date(anio1, mes1, dia1)
							fecha2 = date(anio2, mes2, dia2)
							if fecha1 <  fecha2:
								data[j], data[j+1] = data[j+1], data[j]


			finally:
				conexion.close()	
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return render_template('kardex.html', title='Kardex', logeado=logeado, idtipouser = idtipouser, insumos=insumostotales, data=data, ins=ins, existencia=existencia, actual=actual)
	return render_template('kardex.html', title='Kardex', logeado=logeado, idtipouser = idtipouser, insumos=insumostotales, data=data, ins=ins, existencia=existencia, actual=actual)

@app.route("/login", methods=['GET', 'POST'])
def login():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	if logeado != 0:
		return redirect(url_for('inicio'))
	if request.method == 'POST':
		user = request.form["user"]
		pwd = request.form["pwd"]
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "SELECT idusers, nombre, idtipouser FROM users WHERE user = %s and pwd = md5(%s)"
					cursor.execute(consulta, (user, pwd))
					data = cursor.fetchall()
					if len(data) == 0:
						return render_template('login.html', title='Iniciar sesión', logeado=logeado, idtipouser = idtipouser, mensaje="Datos inválidos, intente nuevamente")
					else:
						session['logeado'] = 1
						session['iduser'] = data[0][0]
						session['nombreuser'] = data[0][1]
						session['idtipouser'] = data[0][2]
						session['user'] = user
						return redirect(url_for('inicio'))
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
	return render_template('login.html', title='Iniciar sesión', logeado=logeado, idtipouser = idtipouser, mensaje="")

@app.route("/logout")
def logout():
	session['logeado'] = 0
	session['nombreuser'] = ""
	session['user'] = ""
	session['iduser'] = ""
	session['idtipouser'] = ""
	return redirect(url_for('inicio'))

@app.route("/")
def inicio():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				cursor.execute("SELECT i.codigo, i.nombre, i.presentacion, t.tipo, i.existencia, DATE_FORMAT(i.fechavencimiento,'%d/%m/%Y') as fechavencimiento, i.minimos, i.maximos from insumos i inner join tipo t ON i.idtipo = t.idtipo where i.activo = 1  order by t.tipo asc, codigo asc;")
			# Con fetchall traemos todas las filas
				insumos = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('inicio.html', title='Inicio', insumos = insumos, logeado=logeado, idtipouser = idtipouser)

@app.route("/nuevoproveedor", methods=['GET', 'POST'])
def nuevoproveedor():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	if request.method == 'POST':
		nombre = request.form["nombre"]
		telefono = request.form["telefono"]
		nombrecontacto = request.form["nombrecontacto"]
		correo = request.form["correo"]
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO proveedores(nombre, telefono, correo, activo, nombrecontacto) values (%s, %s, %s, 1, %s);"
					cursor.execute(consulta, (nombre, telefono, correo, nombrecontacto))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('proveedores'))
	return render_template('nuevoproveedor.html', title='Nuevo proveedor', logeado=logeado, idtipouser = idtipouser)

@app.route("/crearusuario", methods=['GET', 'POST'])
def crearusuario():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0

	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT idtipouser, tipouser FROM inventario.tipouser;"
				cursor.execute(consulta)
				tyuser = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)

	if request.method == 'POST':
		nombre = request.form["nombre"]
		user = request.form["user"]
		pwd = request.form["pwd"]
		tipouser = request.form["tipouser"]
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO users(nombre, user, pwd, idtipouser) values (%s, %s, MD5(%s), %s);"
					cursor.execute(consulta, (nombre, user, pwd, tipouser))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('inicio'))
	return render_template('crearusuario.html', title='Nuevo Usuario', logeado=logeado, idtipouser = idtipouser, tipos = tyuser)

@app.route("/nuevoinsumo", methods=['GET', 'POST'])
def nuevoinsumo():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				cursor.execute("SELECT idtipo, tipo from tipo;")
				tipos = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		tipo = request.form["tipo"]
		nombre = request.form["nombre"]
		presentacion = request.form["presentacion"]
		peligrosidad = request.form["peligrosidad"]
		cantidad = request.form["cantidad"]
		fechaven = request.form["fechaven"]
		minimos = request.form["min"]
		maximos = request.form["max"]

		if len(fechaven) > 0:
			fechaven = fechaven
		else:
			fechaven = None

		if len(minimos) > 0:
			minimos = minimos
		else:
			minimos = None

		if len(maximos) > 0:
			maximos = maximos
		else:
			maximos = None


		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "SELECT MAX(codigo) from insumos where idtipo = %s and activo = 1;"
					cursor.execute(consulta, tipo)
					maxid = cursor.fetchall()
					maxid = maxid[0][0]
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		letra = maxid[0]
		flag = 0
		straux = ""
		for i in range(len(maxid)):
			if maxid[i].isnumeric():
				straux = straux + maxid[i]

		maxid = str(int(straux) + 1)
		while len(maxid) < 3:
			maxid = '0' + maxid
		codigo = letra + str(maxid)

		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO insumos(idtipo, codigo, nombre, presentacion, existencia, idpeligrosidad, activo, fechavencimiento, minimos, maximos) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (tipo, codigo, nombre, presentacion, cantidad, peligrosidad,1, fechaven, minimos, maximos))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('inicio'))
	return render_template('nuevoinsumo.html', title='Agregar insumo', tipos = tipos, logeado=logeado, idtipouser = idtipouser)

@app.route("/nuevopedido", methods=['GET', 'POST'])
def nuevopedido():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0

	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				cursor.execute("SELECT i.codigo, i.nombre, i.presentacion, i.existencia, i.idinsumos from insumos i where i.activo = 1  order by i.nombre asc;")
			# Con fetchall traemos todas las filas
				insumos = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)

	if request.method == 'POST':
		nombre = request.form["nombre"]
		#insercion de pedido header
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO pedidosheader(nombre, fecha) values (%s, %s);"
					cursor.execute(consulta, (nombre, date.today()))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		#obtencion de id del pedido header
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "SELECT max(idpedidosheader) FROM inventario.pedidosheader;"
					cursor.execute(consulta)
					idheader = cursor.fetchall()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		#insercion de los detalles del pedido
		for i in insumos:
			aux = 'total_' + str(i[4])
			cantinsumo = request.form[aux]
			if len(cantinsumo) > 0 and float(cantinsumo) > 0:
				cantinsumo = float(cantinsumo)
				try:
					conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
					try:
						with conexion.cursor() as cursor:
							consulta = "INSERT INTO pedidosdesc(idheader, idinsumo, cantidad, activo, presentacion) values (%s, %s, %s,1,%s);"
							cursor.execute(consulta, (idheader, i[4], cantinsumo, i[2]))
						conexion.commit()
					finally:
						conexion.close()
				except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
					print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('pedidos'))
	return render_template('nuevopedido.html', title='Nuevo pedido', logeado=logeado, idtipouser = idtipouser, insumos=insumos)

@app.route("/agregarinsumos/<numero>&<idheader>", methods=['GET', 'POST'])
def agregarinsumos(numero, idheader):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	numero = int(numero)
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select codigo, nombre, existencia from insumos where activo = 1;"
				cursor.execute(consulta)
				insumostotales = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		insumos = []
		for i in range(numero):
			insumo = []
			aux = "codigo" + str(i)
			insumo.append(request.form[aux])
			aux = "cantidad" + str(i)
			insumo.append(request.form[aux])
			insumos.append(insumo)
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					for i in range(numero):
						consulta = 'SELECT idinsumos, presentacion FROM insumos WHERE codigo = "' + insumos[i][0] + '"'
						cursor.execute(consulta)
						idinsumo = cursor.fetchall()
						consulta = "INSERT INTO pedidosdesc(idheader, idinsumo, cantidad, activo, presentacion) values (%s, %s, %s,1,%s);"
						cursor.execute(consulta, (idheader, idinsumo[0][0], insumos[i][1], idinsumo[0][1]))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('pedido', id=idheader))
	return render_template('agregarinsumos.html', title='Agregar insumos', numero=numero, insumos=insumostotales, logeado=logeado, idtipouser = idtipouser)

@app.route("/agregarcotizacion/<id>", methods=['GET', 'POST'])
def agregarcotizacion(id):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select nombre from pedidosheader where idpedidosheader = %s"
				cursor.execute(consulta, id)
				nombrepedido = cursor.fetchall()
				try:
					nombrepedido = "Pedido " + str(nombrepedido[0][0])
				except:
					nombrepedido = 'Pedido'
				consulta = "select i.nombre, p.cantidad, p.presentacion, i.codigo, i.idinsumos from insumos i inner join pedidosdesc p on i.idinsumos = p.idinsumo inner join pedidosheader h on h.idpedidosheader = p.idheader where p.activo = 1 and h.idpedidosheader = %s group by i.idinsumos order by i.nombre;"
				cursor.execute(consulta, id)
				insumos = cursor.fetchall()
				cantidad = len(insumos)
				consulta = "select idproveedores, nombre from proveedores order by nombre;"
				cursor.execute(consulta)
				proveedores = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		proveedor = request.form['proveedor']
		numdoc = request.form['numdoc']
		if proveedor == 'Nuevo':
			newproveedor = request.form['nuevoproveedor']
			try:
				conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
				try:
					with conexion.cursor() as cursor:
						consulta = "INSERT INTO proveedores(nombre, telefono, correo, activo) values (%s, 0, '0', 1);"
						cursor.execute(consulta, (newproveedor))
					conexion.commit()
				finally:
					conexion.close()
			except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
				print("Ocurrió un error al conectar: ", e)
			try:
				conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
				try:
					with conexion.cursor() as cursor:
						consulta = "SELECT idproveedores FROM proveedores ORDER BY idproveedores desc;"
						cursor.execute(consulta)
						data = cursor.fetchall()
						proveedor = data[0][0]
				finally:
					conexion.close()
			except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
				print("Ocurrió un error al conectar: ", e)
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO cotizacionheader(idproveedor, idpedidosheader, codigo, activo) values (%s,%s,%s,1);"
					cursor.execute(consulta, (proveedor, id, numdoc))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		for i in insumos:
			aux = 'precio' + str(i[4])
			cantidad = request.form[aux]
			if len(cantidad) < 1:
				cantidad = 0
			try:
				conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
				try:
					with conexion.cursor() as cursor:
						consulta = "SELECT idcotizacionheader from cotizacionheader ORDER BY idcotizacionheader desc;"
						cursor.execute(consulta)
						data = cursor.fetchall()
						cotheader = data[0][0]
						consulta = "INSERT INTO cotizaciondesc(idheader, idinsumo, precio) VALUES(%s, %s, %s);"
						cursor.execute(consulta, (cotheader, i[4], cantidad))
					conexion.commit()
				finally:
					conexion.close()
			except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
				print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('pedido', id = id))
	return render_template('agregarcotizacion.html', title='Agregar cotizacion', proveedores=proveedores, nombre= nombrepedido, insumos = insumos, numero = cantidad, logeado=logeado, idtipouser = idtipouser)

@app.route("/matrizdecision/<id>", methods=['GET', 'POST'])
def matrizdecision(id):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select nombre from pedidosheader where idpedidosheader = %s order by fecha asc;"
				cursor.execute(consulta, id)
				nombrepedido = cursor.fetchall()
				try:
					nombrepedido = "Pedido " + str(nombrepedido[0][0])
				except:
					nombrepedido = 'Pedido'
				consulta = "select i.codigo, i.nombre, d.presentacion, d.cantidad, d.idpedidosdesc, i.idinsumos from insumos i inner join pedidosdesc d ON d.idinsumo = i.idinsumos where d.idheader = %s and d.activo = 1 order by i.nombre asc;"
				cursor.execute(consulta, id)
				insumos = cursor.fetchall()
				cantidad = len(insumos)
				consulta = "select idproveedores, nombre from proveedores order by nombre;"
				cursor.execute(consulta)
				proveedores = cursor.fetchall()
				consulta = "select c.idcotizacionheader, p.nombre from cotizacionheader c INNER JOIN proveedores p ON c.idproveedor = p.idproveedores where c.activo = 1 and idpedidosheader = %s order by p.nombre asc;"
				cursor.execute(consulta, id)
				cotheaders = cursor.fetchall()
				cantidad1 = len(cotheaders)
				precios = []
				for j in cotheaders:
					precio = []
					for i in insumos:
						consulta = "select idcotizaciondesc, precio from cotizaciondesc where idinsumo = "+str(i[5])+" and idheader = "+str(j[0])+";"
						cursor.execute(consulta)
						datagen = cursor.fetchall()
						arraux = []
						dato = datagen[0][0]
						arraux.append(dato)
						dato = datagen[0][1]
						arraux.append(dato)
						precio.append(arraux)
					precios.append(precio)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		provaux = []
		for i in insumos:
			aux = 'proveedor' + str(i[5])
			prov = request.form[aux]
			print(prov)
			if prov not in provaux:
				provaux.append(prov)
			try:
				conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
				try:
					with conexion.cursor() as cursor:
						if int(prov) != 6:
							consulta = 'SELECT idcotizacionheader FROM cotizacionheader WHERE activo = 1 and idproveedor = ' + str(prov) +' and idpedidosheader = ' + str(id) + ';'
							cursor.execute(consulta)
							#print(consulta)
							data = cursor.fetchall()
							idcot = data[0][0]
							consulta = 'INSERT INTO ordencompraheader(idpedido, idproveedor, idcotizacion, fecha, iduser) VALUES (%s, %s, %s, %s, %s);'
							cursor.execute(consulta, (id, prov, idcot, date.today(), session['iduser']))
							consulta = 'UPDATE pedidosdesc set activo = 0 where idheader = %s and idinsumo = %s;'
							cursor.execute(consulta, (id, i[5]))
						else:
							idcot = 0
							consulta = 'INSERT INTO ordencompraheader(idpedido, idproveedor, idcotizacion, fecha, iduser) VALUES (%s, %s, %s, %s, %s);'
							cursor.execute(consulta, (id, prov, idcot, date.today(), session['iduser']))
							consulta = 'UPDATE pedidosdesc set activo = 0 where idheader = %s and idinsumo = %s;'
							cursor.execute(consulta, (id, i[5]))
						print(idcot)
					conexion.commit()
				finally:
					conexion.close()
			except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
				print("Ocurrió un error al conectar: ", e)
			try:
				conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
				try:
					with conexion.cursor() as cursor:
						consulta = 'SELECT idordencompraheader FROM ordencompraheader WHERE idproveedor = ' + str(prov)  + ' and idpedido = ' + str(id) +';'
						print(consulta)
						cursor.execute(consulta)
						data = cursor.fetchall()
						idordencompraheader = data[0][0]
						if int(prov) == 6:
							consulta = 'INSERT INTO ordencompradesc(idinsumo, idpedidosdesc, idordencompraheader, cantidad, activo, precio, presentacion) VALUES (%s, %s, %s, %s, 1, %s, %s);'
							cursor.execute(consulta, (i[5], i[4], idordencompraheader, i[3], 0, i[2]))
						else:
							consulta = 'SELECT precio FROM cotizaciondesc WHERE idheader = ' + str(idcot) + ' and idinsumo = '+ str(i[5]) +';'
							print(consulta)
							cursor.execute(consulta)
							data = cursor.fetchall()
							precio = data[0][0]
							consulta = 'INSERT INTO ordencompradesc(idinsumo, idpedidosdesc, idordencompraheader, cantidad, activo, precio, presentacion) VALUES (%s, %s, %s, %s, 1, %s, %s);'
							cursor.execute(consulta, (i[5], i[4], idordencompraheader, i[3], precio, i[2]))
					conexion.commit()
				finally:
					conexion.close()
			except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
				print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('ordencomp', idpedido=id))
	return render_template('matrizdecision.html', title='Matriz de decisión', nombre= nombrepedido, insumos = insumos, numero = cantidad, cotheaders = cotheaders, precios = precios, numero1 = cantidad1, proveedores=proveedores, logeado=logeado, idtipouser = idtipouser)

@app.route("/pedidohist/<idheader>", methods=['GET', 'POST'])
def pedidohist(idheader):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select nombre from pedidosheader where idpedidosheader = %s;"
				cursor.execute(consulta, idheader)
				nombrepedido = cursor.fetchall()
				nombrepedido = nombrepedido[0][0]
				consulta = "select i.codigo, i.nombre, i.presentacion, d.cantidad, d.idpedidosdesc, i.idinsumos from insumos i inner join pedidosdesc d ON d.idinsumo = i.idinsumos where d.idheader = %s and d.activo = 0;"
				cursor.execute(consulta, idheader)
				insumos = cursor.fetchall()
				cantidad = len(insumos)
				consulta = "select idproveedores, nombre from proveedores;"
				cursor.execute(consulta)
				proveedores = cursor.fetchall()
				consulta = "select c.idcotizacionheader, p.nombre from cotizacionheader c INNER JOIN proveedores p ON c.idproveedor = p.idproveedores where idpedidosheader = %s;"
				cursor.execute(consulta, idheader)
				cotheaders = cursor.fetchall()
				cantidad1 = len(cotheaders)
				precios = []
				for j in cotheaders:
					precio = []
					for i in insumos:
						consulta = "select idcotizaciondesc, precio from cotizaciondesc where idheader = " +str(j[0])+ " and idinsumo = "+str(i[5])+";"
						cursor.execute(consulta)
						datagen = cursor.fetchall()
						arraux = []
						dato = datagen[0][0]
						arraux.append(dato)
						dato = datagen[0][1]
						arraux.append(dato)
						precio.append(arraux)
					precios.append(precio)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('pedidohist.html', title='Matriz de decisión', nombre= nombrepedido, insumos = insumos, numero = cantidad, cotheaders = cotheaders, precios = precios, numero1 = cantidad1, proveedores=proveedores, logeado=logeado, idtipouser = idtipouser)

@app.route("/editarcotizaciones/<idheader>", methods=['GET', 'POST'])
def editarcotizaciones(idheader):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select nombre from pedidosheader where idpedidosheader = %s;"
				cursor.execute(consulta, idheader)
				nombrepedido = cursor.fetchall()
				nombrepedido = nombrepedido[0][0]
				consulta = "select i.codigo, i.nombre, i.presentacion, d.cantidad, d.idpedidosdesc, i.idinsumos from insumos i inner join pedidosdesc d ON d.idinsumo = i.idinsumos where d.idheader = %s and d.activo = 1;"
				cursor.execute(consulta, idheader)
				insumos = cursor.fetchall()
				cantidad = len(insumos)
				consulta = "select idproveedores, nombre from proveedores order by nombre asc;"
				cursor.execute(consulta)
				proveedores = cursor.fetchall()
				consulta = "select c.idcotizacionheader, p.nombre from cotizacionheader c INNER JOIN proveedores p ON c.idproveedor = p.idproveedores where idpedidosheader = %s order by p.nombre asc;"
				cursor.execute(consulta, idheader)
				cotheaders = cursor.fetchall()
				cantidad1 = len(cotheaders)
				precios = []
				print(cotheaders)
				for j in cotheaders:
					precio = []
					for i in insumos:
						consulta = "select idcotizaciondesc, precio from cotizaciondesc where idheader = " +str(j[0])+ " and idinsumo = "+str(i[5])+";"
						cursor.execute(consulta)
						datagen = cursor.fetchall()
						arraux = []
						dato = datagen[0][0]
						arraux.append(dato)
						dato = datagen[0][1]
						arraux.append(dato)
						precio.append(arraux)
					precios.append(precio)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					for j in cotheaders:
						for i in insumos:
							consulta = "select idcotizaciondesc from cotizaciondesc where idheader = " +str(j[0])+ " and idinsumo = "+str(i[5])+";"
							cursor.execute(consulta)
							data = cursor.fetchall()
							iddesc = data[0][0]
							aux = 'c' + str(iddesc)
							newcant = request.form[aux]
							consulta = "UPDATE cotizaciondesc set precio = %s where idcotizaciondesc = %s;"
							cursor.execute(consulta, (newcant, iddesc))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('pedido', id=idheader))
	return render_template('editarcotizaciones.html', title='Editar cotizaciones', nombre= nombrepedido, insumos = insumos, numero = cantidad, cotheaders = cotheaders, precios = precios, numero1 = cantidad1, proveedores=proveedores, logeado=logeado, idtipouser = idtipouser)

@app.route("/pedidos", methods=['GET', 'POST'])
def pedidos():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select h.idpedidosheader, h.nombre from pedidosheader h inner join pedidosdesc d ON h.idpedidosheader = d.idheader where d.activo = 1 group by h.idpedidosheader, h.nombre;"
				cursor.execute(consulta)
				pedidos = cursor.fetchall()
				cantidad = len(pedidos)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('pedidos.html', title='Pedidos', pedidos=pedidos, cantidad=cantidad, logeado=logeado, idtipouser = idtipouser)

@app.route("/pedidoshist", methods=['GET', 'POST'])
def pedidoshist():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select h.idpedidosheader, h.nombre from pedidosheader h inner join pedidosdesc d ON h.idpedidosheader = d.idheader where d.activo = 0 group by h.idpedidosheader, h.nombre;"
				cursor.execute(consulta)
				pedidos = cursor.fetchall()
				cantidad = len(pedidos)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('pedidoshist.html', title='Pedidos Historico', pedidos=pedidos, cantidad=cantidad, logeado=logeado, idtipouser = idtipouser)

@app.route("/ordenescompra", methods=['GET', 'POST'])
def ordenescompra():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select h.idpedidosheader, h.nombre from pedidosheader h inner join ordencompraheader o ON h.idpedidosheader = o.idpedido inner join ordencompradesc d on d.idordencompraheader = o.idordencompraheader where d.activo = 1 group by h.nombre order by h.nombre, h.idpedidosheader;"
				cursor.execute(consulta)
				pedidos = cursor.fetchall()
				cantidad = len(pedidos)
				consulta = "select p.idproveedores, p.nombre from proveedores p inner join ordencompraheader h on p.idproveedores = h.idproveedor inner join ordencompradesc d on h.idordencompraheader = d.idordencompraheader where d.activo = 1 group by p.nombre order by p.nombre;"
				cursor.execute(consulta)
				empresas = cursor.fetchall()
				cantidad1 = len(empresas)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('ordenescompra.html', title='Ordenes de Compra', pedidos=pedidos, cantidad=cantidad, logeado=logeado, idtipouser = idtipouser, empresas = empresas, cantidad1 = cantidad1)

@app.route('/ordencompempresaimprimir/<id>')
def ordencompempresaimprimir(id):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = '''select ped.nombre, c.codigo, h.fecha, u.nombre, p.nombre, i.nombre, d.presentacion, d.cantidad, d.precio 
				from pedidosheader ped inner join ordencompraheader h on ped.idpedidosheader = h.idpedido
				inner join cotizacionheader c on c.idcotizacionheader = h.idcotizacion
				inner join users u on u.idusers = h.iduser
				inner join proveedores p on p.idproveedores = h.idproveedor
				inner join ordencompradesc d on d.idordencompraheader = h.idordencompraheader
				inner join insumos i on i.idinsumos = d.idinsumo
				where d.activo = 1 and p.idproveedores = '''
				consulta = consulta + str(id)
				consulta = consulta + " order by ped.nombre asc;"
				cursor.execute(consulta)
				data = cursor.fetchall()
				cantidad = len(data)
				total = 0
				for i in data:
					total = total + float(i[8])

				total = "{:,.2f}".format(total)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	
	rendered = render_template('ordencompempresaimprimir.html', title='Ordenes de Compra', data=data, cantidad=cantidad, logeado=logeado, idtipouser = idtipouser, total = total, id=id)
	options = {'enable-local-file-access': None, 'page-size': 'Letter', 'orientation': 'Portrait', 'margin-left': '0', 'margin-right': '0', 'margin-top': '0', 'margin-bottom': '5', 'encoding': 'utf-8', 'zoom': '0.8'}
	config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
	pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'inline; filename=reportediario.pdf'
	print(response)
	return response

@app.route("/ordencompempresa/<id>", methods=['GET', 'POST'])
def ordencompempresa(id):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = '''select ped.nombre, c.codigo, h.fecha, u.nombre, p.nombre, i.nombre, d.presentacion, d.cantidad, d.precio 
				from pedidosheader ped inner join ordencompraheader h on ped.idpedidosheader = h.idpedido
				inner join cotizacionheader c on c.idcotizacionheader = h.idcotizacion
				inner join users u on u.idusers = h.iduser
				inner join proveedores p on p.idproveedores = h.idproveedor
				inner join ordencompradesc d on d.idordencompraheader = h.idordencompraheader
				inner join insumos i on i.idinsumos = d.idinsumo
				where d.activo = 1 and p.idproveedores = '''
				consulta = consulta + str(id)
				consulta = consulta + " order by ped.nombre asc;"
				cursor.execute(consulta)
				data = cursor.fetchall()
				cantidad = len(data)
				print(cantidad)
				total = 0
				for i in data:
					total = total + float(i[8])
				total = "{:,.2f}".format(total)

		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('ordencompempresa.html', title='Ordenes de Compra', data=data, cantidad=cantidad, logeado=logeado, idtipouser = idtipouser, total = total, id=id)

@app.route("/ordenescomprahist", methods=['GET', 'POST'])
def ordenescomprahist():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select h.idpedidosheader, h.nombre from pedidosheader h inner join ordencompraheader o ON h.idpedidosheader = o.idpedido inner join ordencompradesc d on d.idordencompraheader = o.idordencompraheader where d.activo = 0 group by h.nombre order by h.nombre, h.idpedidosheader;"
				cursor.execute(consulta)
				pedidos = cursor.fetchall()
				cantidad = len(pedidos)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('ordenescomprahist.html', title='Ordenes de Compra', pedidos=pedidos, cantidad=cantidad, logeado=logeado, idtipouser = idtipouser)

@app.route("/ordencomp/<idpedido>", methods=['GET', 'POST'])
def ordencomp(idpedido):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select p.nombre, o.idordencompraheader, d.activo from proveedores p inner join ordencompraheader o ON p.idproveedores = o.idproveedor inner join ordencompradesc d ON d.idordencompraheader = o.idordencompraheader where o.idpedido = %s and d.activo = 1 group by p.nombre;"
				cursor.execute(consulta, idpedido)
				ordenes = cursor.fetchall()
				cantidad = len(ordenes)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('ordencomp.html', title='Ordenes de Compra', ordenes=ordenes, cantidad=cantidad, logeado=logeado, idtipouser = idtipouser, idpedido = idpedido)

@app.route("/ordencomphist/<idpedido>", methods=['GET', 'POST'])
def ordencomphist(idpedido):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select p.nombre, o.idordencompraheader, d.activo from proveedores p inner join ordencompraheader o ON p.idproveedores = o.idproveedor inner join ordencompradesc d ON d.idordencompraheader = o.idordencompraheader where o.idpedido = %s and d.activo = 0 group by p.nombre;"
				cursor.execute(consulta, idpedido)
				ordenes = cursor.fetchall()
				cantidad = len(ordenes)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('ordencomphist.html', title='Ordenes de Compra', ordenes=ordenes, cantidad=cantidad, logeado=logeado, idtipouser = idtipouser, idpedido = idpedido)

@app.route("/liquidacionoc/<id>", methods=['GET', 'POST'])
def liquidacionoc(id):
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = 'update ordencompradesc set activo=0 where idordencompraheader = ' + str(id) + ';'
				cursor.execute(consulta)
			conexion.commit()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return redirect(url_for('inicio'))

@app.route('/ordencompimprimir/<id>')
def ordencompimprimir(id):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "Select idproveedor from ordencompraheader where idordencompraheader = %s"
				cursor.execute(consulta, id)
				varaux = cursor.fetchall()
				idproveedor = varaux[0][0]
				print(idproveedor)
				if int(idproveedor) == 6:
					consulta = '''SELECT p.nombre, e.nombre, u.nombre, DATE_FORMAT(o.fecha,'%d/%m/%Y') as fecha from ordencompraheader o 
								INNER JOIN pedidosheader p ON o.idpedido = p.idpedidosheader
								INNER JOIN proveedores e ON o.idproveedor = e.idproveedores
								INNER JOIN users u ON o.iduser = u.idusers
								WHERE o.idordencompraheader = '''
					consulta = consulta + str(id) + ';'
					cursor.execute(consulta)
					dataheader = cursor.fetchall()
				else:
					consulta = '''SELECT p.nombre, e.nombre, u.nombre, DATE_FORMAT(o.fecha,'%d/%m/%Y') as fecha, c.codigo from ordencompraheader o 
								INNER JOIN pedidosheader p ON o.idpedido = p.idpedidosheader
								INNER JOIN proveedores e ON o.idproveedor = e.idproveedores
								INNER JOIN cotizacionheader c ON c.idcotizacionheader = o.idcotizacion
								INNER JOIN users u ON o.iduser = u.idusers
								WHERE o.idordencompraheader = '''
					consulta = consulta + str(id) + ';'
					cursor.execute(consulta)
					dataheader = cursor.fetchall()
				consulta = '''SELECT i.nombre, o.presentacion, o.cantidad, o.precio
							FROM ordencompradesc o
							INNER JOIN insumos i ON o.idinsumo = i.idinsumos
							WHERE o.idordencompraheader = %s;'''
				cursor.execute(consulta, id)
				datadesc = cursor.fetchall()
				cantidad = len(datadesc)
				total = 0
				for i in datadesc:
					total = total + float(i[3])

		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	
	rendered = render_template('ordencompimprimir.html', title='Orden de Compra', logeado=logeado, idtipouser = idtipouser, dataheader=dataheader, datadesc=datadesc, cantidad = cantidad, id=id, idproveedor=idproveedor, total = total)
	options = {'enable-local-file-access': None, 'page-size': 'Letter', 'orientation': 'Portrait', 'margin-left': '0', 'margin-right': '0', 'margin-top': '0', 'margin-bottom': '5', 'encoding': 'utf-8', 'zoom': '0.8'}
	config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
	pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'inline; filename=reportediario.pdf'
	print(response)
	return response

@app.route("/ordencompdetalles/<id>", methods=['GET', 'POST'])
def ordencompdetalles(id):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "Select idproveedor from ordencompraheader where idordencompraheader = %s"
				cursor.execute(consulta, id)
				varaux = cursor.fetchall()
				idproveedor = varaux[0][0]
				print(idproveedor)
				if int(idproveedor) == 6:
					consulta = '''SELECT p.nombre, e.nombre, u.nombre, DATE_FORMAT(o.fecha,'%d/%m/%Y') as fecha from ordencompraheader o 
								INNER JOIN pedidosheader p ON o.idpedido = p.idpedidosheader
								INNER JOIN proveedores e ON o.idproveedor = e.idproveedores
								INNER JOIN users u ON o.iduser = u.idusers
								WHERE o.idordencompraheader = '''
					consulta = consulta + str(id) + ';'
					cursor.execute(consulta)
					dataheader = cursor.fetchall()
				else:
					consulta = '''SELECT p.nombre, e.nombre, u.nombre, DATE_FORMAT(o.fecha,'%d/%m/%Y') as fecha, c.codigo from ordencompraheader o 
								INNER JOIN pedidosheader p ON o.idpedido = p.idpedidosheader
								INNER JOIN proveedores e ON o.idproveedor = e.idproveedores
								INNER JOIN cotizacionheader c ON c.idcotizacionheader = o.idcotizacion
								INNER JOIN users u ON o.iduser = u.idusers
								WHERE o.idordencompraheader = '''
					consulta = consulta + str(id) + ';'
					cursor.execute(consulta)
					dataheader = cursor.fetchall()
				consulta = '''SELECT i.nombre, o.presentacion, o.cantidad, o.precio
							FROM ordencompradesc o
							INNER JOIN insumos i ON o.idinsumo = i.idinsumos
							WHERE o.idordencompraheader = %s;'''
				cursor.execute(consulta, id)
				datadesc = cursor.fetchall()
				cantidad = len(datadesc)
				total = 0
				for i in datadesc:
					total = total + float(i[3])

		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)

	return render_template('ordencompdetalles.html', title='Orden de Compra', logeado=logeado, idtipouser = idtipouser, dataheader=dataheader, datadesc=datadesc, cantidad = cantidad, id=id, idproveedor=idproveedor, total = total)

@app.route("/ordencompdetalleshist/<id>", methods=['GET', 'POST'])
def ordencompdetalleshist(id):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = '''SELECT p.nombre, e.nombre, c.codigo, u.nombre, DATE_FORMAT(o.fecha,'%d/%m/%Y') as fecha from ordencompraheader o 
								INNER JOIN pedidosheader p ON o.idpedido = p.idpedidosheader
								INNER JOIN proveedores e ON o. idproveedor = e.idproveedores
								INNER JOIN cotizacionheader c ON c.idcotizacionheader = o.idcotizacion
								INNER JOIN users u ON o.iduser = u.idusers
								WHERE o.idordencompraheader = '''
				consulta = consulta + str(id) + ';'
				cursor.execute(consulta)
				dataheader = cursor.fetchall()
				consulta = '''SELECT i.nombre, o.presentacion, o.cantidad, o.precio
							FROM ordencompradesc o
							INNER JOIN insumos i ON o.idinsumo = i.idinsumos
							WHERE o.idordencompraheader = %s;'''
				cursor.execute(consulta, id)
				datadesc = cursor.fetchall()
				cantidad = len(datadesc)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)

	return render_template('ordencompdetalleshist.html', title='Orden de Compra', logeado=logeado, idtipouser = idtipouser, dataheader=dataheader, datadesc=datadesc, cantidad = cantidad, id=id)

@app.route("/pedidogen", methods=['GET', 'POST'])
def pedidogen():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select count(idcotizacionheader) from cotizacionheader where idpedidosheader = 0 and activo = 1;"
				cursor.execute(consulta)
				cantcot = cursor.fetchall()
				cantcot = cantcot[0][0]
				consulta = "select i.nombre, sum(p.cantidad), p.presentacion from insumos i inner join pedidosdesc p on i.idinsumos = p.idinsumo where p.activo = 1 group by i.idinsumos order by i.nombre;"
				cursor.execute(consulta)
				insumos = cursor.fetchall()
				cantidad = len(insumos)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('pedidogen.html', title='Listado Insumos', insumos=insumos, cantidad=cantidad, logeado=logeado, idtipouser = idtipouser, cantcot = cantcot)

@app.route("/pedido/<id>", methods=['GET', 'POST'])
def pedido(id):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select nombre from pedidosheader where idpedidosheader = %s;"
				cursor.execute(consulta, id)
				nombrepedido = cursor.fetchall()
				nombrepedido = nombrepedido[0][0]
				consulta = "select count(idcotizacionheader) from cotizacionheader where idpedidosheader = 0 and activo = 1;"
				cursor.execute(consulta)
				cantcot = cursor.fetchall()
				cantcot = cantcot[0][0]
				print(cantcot)
				consulta = "select i.nombre, d.presentacion, d.cantidad, d.idpedidosdesc from insumos i inner join pedidosdesc d ON d.idinsumo = i.idinsumos where d.idheader = %s and d.activo = 1 order by i.nombre;"
				cursor.execute(consulta, id)
				insumos = cursor.fetchall()
				cantidad = len(insumos)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('pedido.html', title='Listado Insumos', insumos=insumos, cantidad=cantidad, nombreped = nombrepedido, header=id, logeado=logeado, idtipouser = idtipouser, cantcot = cantcot)

@app.route("/pedidopdf/<id>", methods=['GET', 'POST'])
def pedidopdf(id):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select nombre from pedidosheader where idpedidosheader = %s;"
				cursor.execute(consulta, id)
				nombrepedido = cursor.fetchall()
				nombrepedido = nombrepedido[0][0]
				consulta = "select count(idcotizacionheader) from cotizacionheader where idpedidosheader = 0 and activo = 1;"
				cursor.execute(consulta)
				cantcot = cursor.fetchall()
				cantcot = cantcot[0][0]
				print(cantcot)
				consulta = "select i.nombre, d.presentacion, d.cantidad, d.idpedidosdesc from insumos i inner join pedidosdesc d ON d.idinsumo = i.idinsumos where d.idheader = %s and d.activo = 1 order by i.nombre;"
				cursor.execute(consulta, id)
				insumos = cursor.fetchall()
				cantidad = len(insumos)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	rendered = render_template('pedidopdf.html', title='Listado Insumos', insumos=insumos, cantidad=cantidad, nombreped = nombrepedido, header=id, logeado=logeado, idtipouser = idtipouser, cantcot = cantcot)
	options = {'enable-local-file-access': None}
	config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
	pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	aux = 'inline; filename=' + str(nombrepedido) + '.pdf'
	response.headers['Content-Disposition'] = aux
	print(response)
	return response

@app.route("/editarpedido/<id>", methods=['GET', 'POST'])
def editarpedido(id):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select nombre from pedidosheader where idpedidosheader = %s;"
				cursor.execute(consulta, id)
				nombrepedido = cursor.fetchall()
				nombrepedido = nombrepedido[0][0]
				consulta = "select i.nombre, d.presentacion, d.cantidad, d.idpedidosdesc from insumos i inner join pedidosdesc d ON d.idinsumo = i.idinsumos where d.idheader = %s and d.activo = 1 order by i.nombre asc;"
				cursor.execute(consulta, id)
				insumos = cursor.fetchall()
				cantidad = len(insumos)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					for i in range(cantidad):
						aux = 'cant' + str(i)
						newcant = request.form[aux]
						aux = 'presentacion' + str(i)
						newpres = request.form[aux]
						consulta = "UPDATE pedidosdesc set cantidad = %s, presentacion = %s where idpedidosdesc = %s;"
						cursor.execute(consulta, (newcant, newpres, insumos[i][3]))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('pedido', id=id))
	return render_template('editarpedido.html', title='Listado Insumos', insumos=insumos, cantidad=cantidad, nombreped = nombrepedido, header=id, logeado=logeado, idtipouser = idtipouser)

@app.route("/eliminarregistro/<id>", methods=['GET', 'POST'])
def eliminarregistro(id):
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "select idheader from pedidosdesc where idpedidosdesc=%s;"
				cursor.execute(consulta, id)
				header = cursor.fetchall()
				header = header[0][0]
				consulta = "DELETE FROM pedidosdesc WHERE idpedidosdesc = %s;"
				cursor.execute(consulta, id)
			conexion.commit()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return redirect(url_for('pedido', id=header))

@app.route("/editarinsumo/<id>", methods=['GET', 'POST'])
def editarinsumo(id):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				cursor.execute("SELECT idtipo, tipo from tipo;")
				tipos = cursor.fetchall()
				consulta = "SELECT idtipo, codigo, nombre, presentacion, idpeligrosidad, fechavencimiento, minimos, maximos from insumos where idinsumos = %s;"
				cursor.execute(consulta, id)
				insumo = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		tipo = request.form["tipo"]
		codigo = request.form["codigo"]
		nombre = request.form["nombre"]
		presentacion = request.form["presentacion"]
		peligrosidad = request.form["peligrosidad"]
		fechaven = request.form["fechaven"]
		minimos = request.form["min"]
		maximos = request.form["max"]
		if len(fechaven) > 0:
			if fechaven == "None":
				fechaven = None
			fechaven = fechaven
		else:
			fechaven = None
		if len(minimos) > 0:
			minimos = minimos
		else:
			minimos = None

		if len(maximos) > 0:
			maximos = maximos
		else:
			maximos = None
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "UPDATE insumos SET idtipo = %s, codigo = %s, nombre = %s, presentacion = %s, idpeligrosidad = %s, fechavencimiento = %s, minimos = %s, maximos = %s WHERE idinsumos = %s;"
					cursor.execute(consulta, (tipo, codigo, nombre, presentacion, peligrosidad, fechaven, minimos, maximos, id))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('inicio'))
	return render_template('editarinsumo.html', title='Editar insumo', tipos = tipos, insumo=insumo, logeado=logeado, idtipouser = idtipouser)

@app.route("/eliminarinsumo/<id>", methods=['GET', 'POST'])
def eliminarinsumo(id):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT i.nombre, i.codigo, i.presentacion, i.existencia, t.tipo from insumos i inner join tipo t ON i.idtipo = t.idtipo where idinsumos = %s"					
				cursor.execute(consulta, id)
				insumo = cursor.fetchall()
		finally:
			conexion.close()
	except(pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "UPDATE insumos SET activo = 0 WHERE idinsumos = %s;"
					cursor.execute(consulta, id)
 
			# Con fetchall traemos todas las filas
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('inicio'))
	return render_template('eliminarinsumo.html', title='Eliminar insumo', insumo=insumo, logeado=logeado, idtipouser = idtipouser)

@app.route("/desechables")
def desechables():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				cursor.execute("SELECT i.codigo, i.nombre, i.presentacion, t.tipo, i.existencia, i.idinsumos from insumos i inner join tipo t ON i.idtipo = t.idtipo where i.idtipo=2 and i.activo = 1 order by t.tipo asc, codigo asc;")
 
			# Con fetchall traemos todas las filas
				insumos = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('desechables.html', title='Desechables', insumos = insumos, logeado=logeado, idtipouser = idtipouser)

@app.route("/proveedores")
def proveedores():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				cursor.execute("SELECT idproveedores, nombre, telefono, correo, nombrecontacto from proveedores where activo = 1;")
 
			# Con fetchall traemos todas las filas
				proveedores = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('proveedores.html', title='Proveedores', proveedores = proveedores, logeado=logeado, idtipouser = idtipouser)

@app.route("/editarproveedor/<id>", methods=['GET', 'POST'])
def editarproveedor(id):
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT idproveedores, nombre, telefono, correo, nombrecontacto from proveedores where activo = 1 and idproveedores = %s;"
				cursor.execute(consulta, id)
 
			# Con fetchall traemos todas las filas
				proveedor = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		nombre = request.form["nombre"]
		telefono = request.form["telefono"]
		correo = request.form["correo"]
		nombrecontacto = request.form["nombrecontacto"]
		try:
			conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
			try:
				with conexion.cursor() as cursor:
					consulta = "UPDATE proveedores set nombre = %s, telefono = %s, correo = %s, nombrecontacto = %s where idproveedores = %s;"
					cursor.execute(consulta, (nombre, telefono, correo, nombrecontacto, id))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('proveedores'))
	return render_template('editarproveedor.html', title='Editar Proveedor', proveedor = proveedor, logeado=logeado, idtipouser = idtipouser)

@app.route("/eliminarproveedor/<id>", methods=['GET', 'POST'])
def eliminarproveedor(id):
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				consulta = "DELETE FROM proveedores WHERE idproveedores = %s;"
				cursor.execute(consulta, id)
			conexion.commit()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return redirect(url_for('proveedores'))

@app.route("/cristaleria")
def cristaleria():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				cursor.execute("SELECT i.codigo, i.nombre, i.presentacion, t.tipo, i.existencia, i.idinsumos from insumos i inner join tipo t ON i.idtipo = t.idtipo where i.idtipo=1 and i.activo = 1 order by t.tipo asc, codigo asc;")
 
			# Con fetchall traemos todas las filas
				insumos = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('cristaleria.html', title='Cristaleria', insumos = insumos, logeado=logeado, idtipouser = idtipouser)

@app.route("/reactivos")
def reactivos():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				cursor.execute("SELECT i.codigo, i.nombre, i.presentacion, t.tipo, i.existencia, i.idinsumos from insumos i inner join tipo t ON i.idtipo = t.idtipo where i.idtipo=3 and i.activo = 1 order by t.tipo asc, codigo asc;")
 
			# Con fetchall traemos todas las filas
				insumos = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('reactivos.html', title='Reactivos', insumos = insumos, logeado=logeado, idtipouser = idtipouser)

@app.route("/muestras")
def muestras():
	try:
		logeado = session['logeado']
		idtipouser = session['idtipouser']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host='localhost', user='root', password='database', db='inventario')
		try:
			with conexion.cursor() as cursor:
				cursor.execute("SELECT i.codigo, i.nombre, i.presentacion, t.tipo, i.existencia, i.idinsumos from insumos i inner join tipo t ON i.idtipo = t.idtipo where i.idtipo=4 or i.idtipo=5 and i.activo = 1 order by t.tipo asc, codigo asc;")
 
			# Con fetchall traemos todas las filas
				insumos = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('muestras.html', title='Muestras', insumos = insumos, logeado=logeado, idtipouser = idtipouser)

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5002)