from django.db import models

class Odontologo(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    numero_colegiatura = models.CharField(max_length=30, unique=True)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    especialidad = models.ForeignKey('apps.Especialidad', on_delete=models.PROTECT, related_name='odontologos')
    estado = models.CharField(max_length=20, choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')], default='Activo')

    class Meta:
        db_table = 'odontologos'
        ordering = ['apellidos', 'nombres']
        verbose_name = 'odontólogo'

    def __str__(self):
        return f'{self.nombres} {self.apellidos}'
