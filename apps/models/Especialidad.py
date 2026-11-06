from django.db import models

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=[('Activa', 'Activa'), ('Inactiva', 'Inactiva')], default='Activa')

    class Meta:
        db_table = 'especialidades'
        ordering = ['nombre']
        verbose_name_plural = 'especialidades'

    def __str__(self):
        return self.nombre
