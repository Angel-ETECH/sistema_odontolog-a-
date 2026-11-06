from django.db import models

class Receta(models.Model):
    diagnostico = models.ForeignKey('apps.Diagnostico', on_delete=models.PROTECT, related_name='recetas')
    medicamento = models.CharField(max_length=150)
    dosis = models.CharField(max_length=100)
    frecuencia = models.CharField(max_length=100)
    duracion = models.CharField(max_length=100)
    indicaciones = models.TextField(blank=True)
    fecha_emision = models.DateField()

    class Meta:
        db_table = 'recetas'
        ordering = ['-fecha_emision', '-id']

    def __str__(self):
        return f'RX-{self.pk} · {self.medicamento}'
