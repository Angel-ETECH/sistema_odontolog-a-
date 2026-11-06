from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Prepara los grupos Recepción y Odontología sin agregar tablas de negocio.'

    def handle(self, *args, **options):
        recepcion, _ = Group.objects.get_or_create(name='Recepción')
        clinica, _ = Group.objects.get_or_create(name='Odontología')
        permisos = Permission.objects.filter(content_type__app_label='apps')
        recepcion.permissions.set(permisos.filter(codename__in=[
            'view_paciente', 'add_paciente', 'change_paciente', 'view_cita', 'add_cita', 'change_cita',
            'view_odontologo', 'view_especialidad']))
        clinica.permissions.set(permisos.exclude(codename__startswith='delete_'))
        self.stdout.write(self.style.SUCCESS('Roles preparados. Asigna los grupos desde Administración > Usuarios.'))
