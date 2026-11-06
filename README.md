# Consultorio odontológico Sonrisa Perfecta

Proyecto individual con Python, Django, MariaDB, HTML, CSS y JavaScript.

## Ejecutar en esta laptop

Desde la terminal del proyecto:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 8003
```

Abrir http://127.0.0.1:8003/. MariaDB debe estar encendido en el puerto 3307. El script iniciar.ps1 puede iniciar la instancia instalada en esta laptop y luego Django. No se necesita Apache.

## Instalación en otra computadora

Se verificó con Python 3.14.9, Django 6.1.3 y MariaDB 11.4.13. No copiar .venv entre computadoras.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Configurar la conexión y una clave secreta aleatoria en .env. Ejecutar database/crear_bd.sql en MariaDB. Después:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py configurar_roles
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver 8003
```

## Organización

- config/: configuración y rutas principales.
- apps/models/: los siete modelos, cada uno en su archivo.
- apps/forms.py: formularios y validaciones.
- apps/catalogo.py: configuración de los módulos para compartir el CRUD.
- apps/views.py y apps/urls.py: operaciones y rutas.
- apps/templates/ y apps/static/: interfaz, estilos, iconos y JavaScript.
- apps/migrations/: creación de las tablas.
- apps/management/: comando para preparar los grupos de permisos.
- apps/templatetags/: formato de los valores en tablas y reportes.
- docs/: diagrama de relaciones, guía de sustentación y créditos de los iconos.

## Uso

Registrar especialidades, odontólogos y pacientes. Luego crear citas y relacionar los diagnósticos, tratamientos y recetas. Los siete módulos permiten registrar, listar, buscar, editar y eliminar. No se pueden borrar registros con información relacionada.

En Reportes se filtran citas, diagnósticos, tratamientos y recetas. Para guardar un PDF, pulsar Imprimir / Guardar PDF y elegir Guardar como PDF en el navegador.

## Permisos

Las cuentas nuevas no tienen permisos administrativos. El administrador asigna los grupos desde /admin/:

- Recepción: consultar, registrar y editar pacientes y citas; consultar profesionales y especialidades.
- Odontología: consultar, registrar y editar los siete módulos.
- Administrador: acceso completo y asignación de permisos.

La base local es consultorio_odontologico_db, independiente de los otros proyectos. La configuración de desarrollo es para uso local. Para usar datos reales se requiere HTTPS, desactivar DEBUG, limitar el registro y los permisos de base de datos, y definir respaldos y protección de la información.

## Pruebas

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test apps
```
