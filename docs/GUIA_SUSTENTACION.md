# Guía para explicar mi proyecto

## Presentación

“Mi proyecto se llama Sonrisa Perfecta. Ayuda a un consultorio odontológico a organizar pacientes, citas y la información de sus atenciones. Antes estos datos se llevaban de forma manual; con el sistema puedo buscarlos y relacionarlos.”

## Modelos y relaciones

“Tengo siete modelos de negocio. Cada uno está en un archivo dentro de apps/models. El archivo __init__.py los importa para que Django los reconozca.”

“Un paciente puede tener varias citas. Cada cita tiene un odontólogo, y cada odontólogo pertenece a una especialidad. De una cita se registran diagnósticos. Cada diagnóstico puede tener tratamientos y recetas.”

Mostrar `docs/diagrama-er.svg`. Explicar que PK identifica un registro y FK enlaza con otro. Las relaciones usan PROTECT: si un paciente tiene citas, no se puede borrar y dejar la atención sin paciente.

## Formularios

“Uso ModelForm para generar los campos desde los modelos. Valido que el DNI tenga ocho dígitos, que el correo sea válido y que el costo no sea negativo. También reviso fechas y que un odontólogo o un paciente no tengan dos citas activas en el mismo horario.”

Mostrar `PacienteForm`, `CitaForm` y `TratamientoForm` en `apps/forms.py`. Las validaciones se ejecutan en el servidor; no dependen solo del HTML.

## Recorrido de una solicitud

“Cuando abro una sección, urls.py elige la vista. La vista verifica mis permisos y consulta los modelos. La plantilla muestra los registros. Cuando guardo, el formulario valida los datos, el modelo los guarda en MariaDB y la vista vuelve a la lista con un mensaje.”

Mostrar `guardar` en `views.py`. `catalogo.py` permite reutilizar ese mismo flujo para los siete módulos sin repetir siete veces la lógica.

## Autenticación y permisos

“El login usa la autenticación de Django. Si marco Mantener mi cuenta abierta, la sesión dura catorce días. Si no, termina al cerrar el navegador. El navegador puede restaurar sesiones según su configuración.”

“Registrarse no convierte a una persona en administrador. El administrador asigna los permisos según su puesto. Recepción trabaja con pacientes y citas; Odontología tiene acceso a la parte clínica. También verifico los permisos en las vistas.”

## Reportes

“Puedo elegir citas, diagnósticos, tratamientos o recetas. Filtro por paciente y fechas; citas y tratamientos también por estado. Después puedo imprimir el reporte o elegir Guardar como PDF en el navegador. El documento individual incluye al paciente y al odontólogo.”

## Migraciones

“makemigrations prepara los cambios de las tablas; migrate los aplica a MariaDB. Las tablas internas de Django no cuentan como modelos del negocio.”

## Demostración sugerida

1. Entrar a la cuenta.
2. Registrar una especialidad y un odontólogo.
3. Registrar un paciente con datos ficticios.
4. Crear una cita; intentar repetir su horario para mostrar la validación.
5. Registrar diagnóstico, tratamiento y receta con textos de demostración, sin instrucciones médicas reales.
6. Buscar al paciente y editar un registro.
7. Filtrar un reporte e imprimir o guardar como PDF.
8. Intentar eliminar el paciente con citas para mostrar la protección.
9. Explicar la diferencia entre una cuenta nueva y una con permisos.

No memorizar cada línea: recordar el orden **modelos → formularios → vistas → rutas → plantillas → reportes**.
