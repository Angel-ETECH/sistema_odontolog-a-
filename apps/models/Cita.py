from django.db import models

class Cita(models.Model):
    ESTADOS = [(v, v) for v in ['Pendiente', 'Confirmada', 'Atendida', 'Cancelada']]
    paciente = models.ForeignKey('apps.Paciente', on_delete=models.PROTECT, related_name='citas')
    odontologo = models.ForeignKey('apps.Odontologo', on_delete=models.PROTECT, related_name='citas')
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.CharField(max_length=200)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = 'citas'
        ordering = ['-fecha', '-hora']

    def __str__(self):
        return f'{self.paciente} · {self.fecha:%d/%m/%Y} {self.hora:%H:%M}'
