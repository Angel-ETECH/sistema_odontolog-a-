from datetime import date, time
from decimal import Decimal
from django.apps import apps
from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from .models import Paciente, Especialidad, Odontologo, Cita, Diagnostico, Tratamiento, Receta
from .forms import CitaForm, PacienteForm, TratamientoForm


class ConsultorioTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_superuser('prueba', 'prueba@example.com', 'ClaveDePrueba123!')
        self.client.force_login(self.usuario)
        self.paciente = Paciente.objects.create(nombres='Paciente', apellidos='Prueba', dni='12345678', fecha_nacimiento=date(2000, 1, 1), telefono='999999999', direccion='Dirección de prueba', correo='paciente@example.com')
        self.especialidad = Especialidad.objects.create(nombre='General', descripcion='Prueba')
        self.odontologo = Odontologo.objects.create(nombres='Profesional', apellidos='Prueba', numero_colegiatura='COP-PRUEBA', telefono='999999999', correo='profesional@example.com', especialidad=self.especialidad)
        self.cita = Cita.objects.create(paciente=self.paciente, odontologo=self.odontologo, fecha=date(2026, 11, 6), hora=time(10, 0), motivo='Control')
        self.diagnostico = Diagnostico.objects.create(cita=self.cita, descripcion='Registro de prueba', fecha=date(2026, 11, 6))
        self.tratamiento = Tratamiento.objects.create(diagnostico=self.diagnostico, nombre='Tratamiento de prueba', descripcion='Prueba', fecha_inicio=date(2026, 11, 6), fecha_fin=date(2026, 11, 7), costo=Decimal('50.00'))
        self.receta = Receta.objects.create(diagnostico=self.diagnostico, medicamento='Ejemplo de prueba', dosis='Prueba', frecuencia='Prueba', duracion='Prueba', fecha_emision=date(2026, 11, 6))
        self.objetos = {'pacientes': self.paciente, 'especialidades': self.especialidad, 'odontologos': self.odontologo, 'citas': self.cita, 'diagnosticos': self.diagnostico, 'tratamientos': self.tratamiento, 'recetas': self.receta}

    def test_exactamente_siete_modelos_bigauto(self):
        modelos = list(apps.get_app_config('apps').get_models())
        self.assertEqual(len(modelos), 7)
        self.assertTrue(all(m._meta.pk.get_internal_type() == 'BigAutoField' for m in modelos))

    def test_pantallas_y_formularios_siete_modulos(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/admin/').status_code, 200)
        for seccion, objeto in self.objetos.items():
            for ruta in [reverse('listado', args=[seccion]), reverse('nuevo', args=[seccion]), reverse('editar', args=[seccion, objeto.pk])]:
                with self.subTest(ruta=ruta):
                    self.assertEqual(self.client.get(ruta).status_code, 200)

    def datos_objeto(self, objeto):
        datos = {}
        for campo in objeto._meta.fields:
            if campo.name in ['id', 'created_at']:
                continue
            valor = getattr(objeto, campo.name)
            if campo.is_relation:
                valor = valor.pk
            if isinstance(valor, time):
                valor = valor.strftime('%H:%M')
            datos[campo.name] = str(valor)
        return datos

    def test_crear_editar_buscar_y_eliminar_todos(self):
        for seccion, original in self.objetos.items():
            datos = self.datos_objeto(original)
            if seccion == 'pacientes':
                datos['dni'] = '87654321'
            if seccion == 'odontologos':
                datos['numero_colegiatura'] = 'COP-NUEVO'
            if seccion == 'citas':
                datos['hora'] = '15:00'
            modelo = type(original)
            cantidad = modelo.objects.count()
            respuesta = self.client.post(reverse('nuevo', args=[seccion]), datos)
            self.assertEqual(respuesta.status_code, 302, (seccion, respuesta.content[:300]))
            self.assertEqual(modelo.objects.count(), cantidad + 1, seccion)
            nuevo = modelo.objects.latest('pk')
            respuesta = self.client.post(reverse('editar', args=[seccion, nuevo.pk]), datos)
            self.assertEqual(respuesta.status_code, 302, seccion)
            self.assertEqual(self.client.get(reverse('listado', args=[seccion]), {'q': 'Prueba'}).status_code, 200)
            self.assertEqual(self.client.post(reverse('eliminar', args=[seccion, nuevo.pk])).status_code, 302)
            self.assertFalse(modelo.objects.filter(pk=nuevo.pk).exists())

    def test_proteger_relaciones_y_post_obligatorio(self):
        self.assertEqual(self.client.get(reverse('eliminar', args=['pacientes', self.paciente.pk])).status_code, 405)
        self.client.post(reverse('eliminar', args=['pacientes', self.paciente.pk]))
        self.assertTrue(Paciente.objects.filter(pk=self.paciente.pk).exists())

    def test_validar_dni_nacimiento_y_costo(self):
        datos = self.datos_objeto(self.paciente)
        datos.update(dni='incorrecto', fecha_nacimiento='2999-01-01')
        formulario = PacienteForm(datos)
        self.assertFalse(formulario.is_valid())
        self.assertIn('dni', formulario.errors)
        self.assertIn('fecha_nacimiento', formulario.errors)
        datos = self.datos_objeto(self.tratamiento)
        datos.update(costo='-1', fecha_fin='2026-01-01')
        formulario = TratamientoForm(datos)
        self.assertFalse(formulario.is_valid())
        self.assertIn('costo', formulario.errors)
        self.assertIn('fecha_fin', formulario.errors)

    def test_evitar_citas_duplicadas_y_permitir_canceladas(self):
        datos = self.datos_objeto(self.cita)
        formulario = CitaForm(datos)
        self.assertFalse(formulario.is_valid())
        self.assertIn('hora', formulario.errors)
        datos['estado'] = 'Cancelada'
        self.assertTrue(CitaForm(datos).is_valid())

    def test_reportes_filtros_y_documentos(self):
        for seccion in ['citas', 'diagnosticos', 'tratamientos', 'recetas']:
            ruta = reverse('reportes', args=[seccion])
            respuesta = self.client.get(ruta, {'desde': '2026-11-06', 'hasta': '2026-11-06', 'q': 'Prueba'})
            self.assertEqual(respuesta.status_code, 200)
            self.assertEqual(len(respuesta.context['registros']), 1)
            respuesta = self.client.get(ruta, {'desde': '2027-01-01'})
            self.assertEqual(len(respuesta.context['registros']), 0)
            respuesta = self.client.get(ruta, {'desde': '2027-01-01', 'hasta': '2026-01-01'})
            self.assertTrue(respuesta.context['filtro'].errors)
            respuesta = self.client.get(reverse('imprimir', args=[seccion, self.objetos[seccion].pk]))
            self.assertContains(respuesta, self.paciente.dni)
            self.assertContains(respuesta, self.odontologo.numero_colegiatura)

    def test_no_exponer_datos_sin_permisos(self):
        normal = User.objects.create_user('sinpermisos', password='ClaveNormal123!')
        self.client.force_login(normal)
        respuesta = self.client.get('/')
        self.assertNotContains(respuesta, self.paciente.dni)
        for seccion in self.objetos:
            self.assertEqual(self.client.get(reverse('listado', args=[seccion])).status_code, 403)
            self.assertEqual(self.client.post(reverse('nuevo', args=[seccion]), {}).status_code, 403)
        self.assertEqual(self.client.get(reverse('reportes', args=['diagnosticos'])).status_code, 403)

    def test_acceso_anonimo_y_csrf(self):
        anonimo = Client(enforce_csrf_checks=True)
        self.assertEqual(anonimo.get('/pacientes/').status_code, 302)
        self.assertEqual(anonimo.post('/login/', {}).status_code, 403)

    @override_settings(REGISTRATION_OPEN=True)
    def test_registro_sin_privilegios(self):
        self.client.logout()
        respuesta = self.client.post('/registro/', {'username': 'nuevousuario', 'email': 'nuevo@example.com', 'password1': 'UnaClaveFuerte2026!', 'password2': 'UnaClaveFuerte2026!'})
        self.assertEqual(respuesta.status_code, 302)
        usuario = User.objects.get(username='nuevousuario')
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
        self.assertFalse(usuario.has_perm('apps.view_paciente'))

    def test_login_recordarme_y_sesion_navegador(self):
        self.client.logout()
        datos = {'username': 'prueba', 'password': 'ClaveDePrueba123!', 'recordarme': '1'}
        self.assertEqual(self.client.post('/login/', datos).status_code, 302)
        self.assertEqual(self.client.session.get_expiry_age(), 14 * 86400)
        self.client.post('/logout/')
        datos.pop('recordarme')
        self.client.post('/login/', datos)
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_respuestas_clinicas_no_cacheadas(self):
        for ruta in ['/', '/pacientes/', '/reportes/diagnosticos/']:
            self.assertIn('no-store', self.client.get(ruta)['Cache-Control'])

    def test_agenda_semanal_filtra_el_dia_seleccionado(self):
        respuesta = self.client.get('/', {'fecha': '2026-11-06'})
        self.assertEqual(list(respuesta.context['agenda_dia']), [self.cita])
        self.assertEqual(len(respuesta.context['semana']), 7)
        respuesta = self.client.get('/', {'fecha': '2026-11-07'})
        self.assertEqual(len(respuesta.context['agenda_dia']), 0)
        for fecha in ['fecha-invalida', '0001-01-01', '9999-12-31']:
            self.assertEqual(self.client.get('/', {'fecha': fecha}).status_code, 200)
