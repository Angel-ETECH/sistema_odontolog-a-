# Sonrisa Perfecta · Consultorio odontológico

Proyecto individual desarrollado con Python, Django, MariaDB, HTML, CSS y JavaScript. Incluye siete módulos con CRUD: pacientes, odontólogos, especialidades, citas, diagnósticos, tratamientos y recetas.

## Instalación para revisar el proyecto

Los comandos siguientes se ejecutan en **PowerShell**, desde la terminal de Visual Studio Code. No hace falta instalar el proyecto dentro de XAMPP ni encender Apache: Django utiliza su propio servidor.

### 1. Requisitos

- Git, para descargar el repositorio. También se puede usar **Code > Download ZIP** en GitHub y descomprimirlo.
- **Python 3.14 de 64 bits**, recomendado para usar las mismas versiones verificadas en esta entrega.
- **MariaDB 10.11 o superior**. Se verificó con MariaDB 11.4.13.

El proyecto utiliza Django 6.1.3 y mysqlclient 2.3.0. Algunas instalaciones de XAMPP incluyen MariaDB 10.4: esa versión no es compatible con este Django. Se puede utilizar otra instancia de MariaDB en un puerto diferente, sin reemplazar las bases existentes.

### 2. Descargar y abrir

```powershell
git clone https://github.com/Angel-ETECH/sistema_odontolog-a-.git consultorio_odontologico
cd consultorio_odontologico
```

Abrir esta carpeta en Visual Studio Code. Si se descargó el ZIP, abrir la carpeta donde está `manage.py` y continuar con el paso siguiente.

### 3. Crear el entorno e instalar dependencias

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Si el comando `py` no existe, utilizar `python -m venv .venv`, comprobando antes la versión con `python --version`.

No es necesario activar el entorno ni cambiar las políticas de PowerShell: todos los comandos llaman directamente a su Python. La carpeta `.venv` se crea en cada computadora y no se descarga desde GitHub.

### 4. Configurar el archivo .env

```powershell
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copiar la clave que imprime el segundo comando y colocarla como valor de `DJANGO_SECRET_KEY` en `.env`. Completar la conexión con los datos del servidor MariaDB del profesor:

```dotenv
DJANGO_DEBUG=1
DJANGO_SECRET_KEY=pegar-aqui-la-clave-generada
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
REGISTRATION_OPEN=1
DB_NAME=consultorio_odontologico_db
DB_USER=root
DB_PASSWORD=tu_contrasena_de_mariadb
DB_HOST=127.0.0.1
DB_PORT=3307
```

- `DB_PORT` debe coincidir con el puerto de MariaDB. En esta laptop es **3307**; si el servidor del profesor utiliza **3306**, cambiarlo a `3306`.
- Si su usuario no tiene contraseña, dejar `DB_PASSWORD=` vacío.
- Los valores de ejemplo se reemplazan por los reales; no se escriben los nombres de los ejemplos como contraseña.
- `.env` contiene la configuración privada de cada equipo y no se incluye en GitHub.

### 5. Crear la base de datos

Encender el servidor MariaDB. En su consola SQL, HeidiSQL o phpMyAdmin conectado a la instancia compatible, ejecutar el contenido de `database/crear_bd.sql`:

```sql
CREATE DATABASE IF NOT EXISTS consultorio_odontologico_db
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

La base se crea vacía. Django creará las tablas en el siguiente paso. No se necesita importar datos de otro proyecto.

### 6. Crear las tablas y los permisos

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py configurar_roles
.\.venv\Scripts\python.exe manage.py check
```

La revisión debe terminar con `System check identified no issues`. Las tablas internas de usuarios, permisos, sesiones y migraciones son propias de Django y no se cuentan entre las siete tablas del negocio.

### 7. Crear la cuenta del profesor

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Elegir un nombre de usuario, correo y contraseña. **Al escribir la contraseña, la terminal no muestra caracteres: es normal.** Esta cuenta permite revisar todos los módulos y el administrador. Los usuarios de la computadora del alumno no se transfieren al clonar el código.

### 8. Ejecutar

```powershell
.\.venv\Scripts\python.exe manage.py runserver 8003
```

Mantener esa terminal abierta. Abrir:

| Página | Dirección |
|---|---|
| Sistema | http://127.0.0.1:8003/ |
| Inicio de sesión | http://127.0.0.1:8003/login/ |
| Administración de Django | http://127.0.0.1:8003/admin/ |

Ingresar con la cuenta creada en el paso anterior. Para detener el servidor, presionar **Ctrl + C** en la terminal.

## Volver a ejecutarlo otro día

Encender MariaDB, abrir la terminal en la carpeta de `manage.py` y ejecutar:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 8003
```

No es necesario repetir las migraciones ni crear nuevamente la cuenta. El script `iniciar.ps1` usa las rutas de MariaDB de la laptop del alumno; en otro equipo se debe iniciar MariaDB con su herramienta habitual.

## Recorrido recomendado para la revisión

1. Registrar una especialidad.
2. Registrar un odontólogo asociado a esa especialidad.
3. Registrar un paciente con datos ficticios.
4. Crear una cita y buscarla en la agenda semanal del panel.
5. Registrar un diagnóstico asociado a la cita.
6. Registrar un tratamiento y una receta asociados al diagnóstico.
7. Probar búsquedas y editar registros en los siete módulos.
8. Filtrar reportes de citas, diagnósticos, tratamientos y recetas.
9. Pulsar **Imprimir / Guardar PDF** y elegir **Guardar como PDF** en el navegador.
10. Intentar eliminar el paciente con citas: el sistema protege sus relaciones. Para probar eliminaciones, usar registros de prueba sin dependencias.

La base de una instalación nueva no contiene pacientes ni datos clínicos de ejemplo.

## Registro y permisos

Las cuentas creadas desde **Crear una cuenta** no obtienen privilegios administrativos. El profesor puede asignar los grupos desde `/admin/`, en **Usuarios**:

- **Recepción:** consultar, registrar y editar pacientes y citas; consultar profesionales y especialidades.
- **Odontología:** consultar, registrar y editar los siete módulos, sin eliminar.
- **Superusuario:** acceso completo y administración de permisos; se crea con `createsuperuser`.

Los grupos permiten trabajar en la interfaz del consultorio; no convierten automáticamente al usuario en personal del administrador de Django.

## Pruebas automáticas

Con MariaDB encendido y la conexión configurada:

```powershell
.\.venv\Scripts\python.exe manage.py test apps --noinput
```

Se verificaron **13 pruebas**. Incluyen el CRUD, protección de relaciones, validaciones, autenticación, permisos, reportes y selección de días de la agenda. El comando crea y elimina una base temporal `test_consultorio_odontologico_db`; el usuario configurado debe tener permisos para esa operación. No utilizar una base con ese nombre para guardar información propia.

## Problemas comunes

| Mensaje o problema | Qué revisar |
|---|---|
| No se puede conectar al servidor / error 2003 | Encender MariaDB y comprobar `DB_HOST` y `DB_PORT`. |
| Access denied / error 1045 | Corregir `DB_USER` y `DB_PASSWORD`. |
| Unknown database / error 1049 | Crear la base del paso 5. |
| Se requiere una versión superior de MariaDB | Utilizar MariaDB 10.11 o superior; no desactivar la comprobación de Django. |
| No module named django | Instalar requirements.txt y utilizar el Python de `.venv`. |
| Error al instalar mysqlclient | Comprobar que Python sea 3.14 de 64 bits y que pip pueda acceder a internet. |
| Puerto 8003 ocupado | Ejecutar `manage.py runserver 8004` y abrir http://127.0.0.1:8004/. |
| Usuario autenticado sin autorización en `/admin/` | Ingresar con el superusuario creado en el paso 7. |
| Cambios de estilo que no aparecen | Recargar con **Ctrl + F5**. |

## Organización del código

- `config/`: configuración y rutas principales.
- `apps/models/`: los siete modelos, cada uno en su archivo.
- `apps/forms.py`: formularios y validaciones.
- `apps/catalogo.py`: configuración compartida de los módulos CRUD.
- `apps/views.py` y `apps/urls.py`: operaciones y rutas.
- `apps/templates/` y `apps/static/`: interfaz, estilos, fuentes, iconos y JavaScript.
- `apps/migrations/`: creación del esquema de tablas.
- `apps/management/`: comando para preparar los grupos de permisos.
- `apps/templatetags/`: formato de los valores en tablas y reportes.

El diagrama está en [docs/diagrama-er.png](docs/diagrama-er.png), la guía de explicación en [docs/GUIA_SUSTENTACION.md](docs/GUIA_SUSTENTACION.md) y los créditos de recursos gráficos en [docs/CREDITOS_ICONOS.md](docs/CREDITOS_ICONOS.md).

Esta configuración es para revisión educativa local. Para trabajar con datos reales se necesita preparar HTTPS, desactivar DEBUG, limitar el registro y los permisos de base de datos, y definir respaldos y protección de la información.
