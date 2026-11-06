from django.core.validators import MinValueValidator
from django.db import models

class Tratamiento(models.Model):
    diagnostico = models.ForeignKey('apps.Diagnostico', on_delete=models.PROTECT, related_name='tratamientos')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    costo = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    estado = models.CharField(max_length=20, choices=[(v, v) for v in ['Pendiente', 'En proceso', 'Finalizado']], default='Pendiente')

    class Meta:
        db_table = 'tratamientos'
        ordering = ['-fecha_inicio', '-id']
        constraints = [models.CheckConstraint(condition=models.Q(costo__gte=0), name='tratamiento_costo_no_negativo'),
                       models.CheckConstraint(condition=models.Q(fecha_fin__gte=models.F('fecha_inicio')), name='tratamiento_fechas_validas')]

    def __str__(self):
        return f'{self.nombre} · {self.diagnostico.cita.paciente}'
