from django.db import models

class Diagnostico(models.Model):
    cita = models.ForeignKey('apps.Cita', on_delete=models.PROTECT, related_name='diagnosticos')
    descripcion = models.TextField()
    recomendaciones = models.TextField(blank=True)
    fecha = models.DateField()

    class Meta:
        db_table = 'diagnosticos'
        ordering = ['-fecha', '-id']
        verbose_name = 'diagnóstico'

    def __str__(self):
        return f'DX-{self.pk} · {self.cita.paciente}'
