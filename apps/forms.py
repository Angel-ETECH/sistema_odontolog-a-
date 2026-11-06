from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Paciente, Especialidad, Odontologo, Cita, Diagnostico, Tratamiento, Receta


class FormularioBase(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nombre, campo in self.fields.items():
            campo.label = nombre.replace('_', ' ').capitalize()
            if isinstance(campo, forms.DateField):
                campo.widget = forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'})
                campo.initial = campo.initial or timezone.localdate
            elif isinstance(campo, forms.TimeField):
                campo.widget = forms.TimeInput(format='%H:%M', attrs={'type': 'time'})
            elif isinstance(campo.widget, forms.Textarea):
                campo.widget.attrs['rows'] = 3
        etiquetas = {'direccion': 'Dirección', 'telefono': 'Teléfono', 'descripcion': 'Descripción',
                     'odontologo': 'Odontólogo', 'diagnostico': 'Diagnóstico', 'numero_colegiatura': 'Número de colegiatura',
                     'duracion': 'Duración', 'fecha_emision': 'Fecha de emisión', 'dni': 'DNI'}
        for nombre, etiqueta in etiquetas.items():
            if nombre in self.fields:
                self.fields[nombre].label = etiqueta


class PacienteForm(FormularioBase):
    class Meta:
        model = Paciente
        exclude = ['created_at']

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data['fecha_nacimiento']
        if fecha > timezone.localdate():
            raise forms.ValidationError('La fecha de nacimiento no puede ser futura.')
        return fecha


class EspecialidadForm(FormularioBase):
    class Meta:
        model = Especialidad
        fields = '__all__'


class OdontologoForm(FormularioBase):
    class Meta:
        model = Odontologo
        fields = '__all__'


class CitaForm(FormularioBase):
    class Meta:
        model = Cita
        fields = '__all__'

    def clean(self):
        datos = super().clean()
        odontologo = datos.get('odontologo')
        if datos.get('estado') != 'Cancelada' and odontologo:
            if odontologo.estado != 'Activo' or odontologo.especialidad.estado != 'Activa':
                self.add_error('odontologo', 'Selecciona un odontólogo activo con especialidad activa.')
            if datos.get('fecha') and datos.get('hora'):
                citas = Cita.objects.filter(fecha=datos['fecha'], hora=datos['hora']).exclude(estado='Cancelada').exclude(pk=self.instance.pk)
                if citas.filter(odontologo=odontologo).exists():
                    self.add_error('hora', 'El odontólogo ya tiene una cita en ese horario.')
                if datos.get('paciente') and citas.filter(paciente=datos['paciente']).exists():
                    self.add_error('paciente', 'El paciente ya tiene una cita en ese horario.')
        return datos


class DiagnosticoForm(FormularioBase):
    class Meta:
        model = Diagnostico
        fields = '__all__'

    def clean(self):
        datos = super().clean()
        if datos.get('cita') and datos.get('fecha') and datos['fecha'] < datos['cita'].fecha:
            self.add_error('fecha', 'El diagnóstico no puede ser anterior a la cita.')
        return datos


class TratamientoForm(FormularioBase):
    class Meta:
        model = Tratamiento
        fields = '__all__'

    def clean(self):
        datos = super().clean()
        inicio, fin = datos.get('fecha_inicio'), datos.get('fecha_fin')
        if inicio and fin and fin < inicio:
            self.add_error('fecha_fin', 'La fecha final no puede ser anterior al inicio.')
        if inicio and datos.get('diagnostico') and inicio < datos['diagnostico'].fecha:
            self.add_error('fecha_inicio', 'El tratamiento no puede comenzar antes del diagnóstico.')
        return datos


class RecetaForm(FormularioBase):
    class Meta:
        model = Receta
        fields = '__all__'

    def clean(self):
        datos = super().clean()
        if datos.get('fecha_emision') and datos.get('diagnostico') and datos['fecha_emision'] < datos['diagnostico'].fecha:
            self.add_error('fecha_emision', 'La emisión no puede ser anterior al diagnóstico.')
        return datos


class RegistroForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class FiltroReporteForm(forms.Form):
    desde = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    hasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    q = forms.CharField(required=False, max_length=100, label='Paciente o contenido')
    estado = forms.ChoiceField(required=False)

    def __init__(self, *args, estados=None, **kwargs):
        super().__init__(*args, **kwargs)
        if estados:
            self.fields['estado'].choices = [('', 'Todos los estados')] + list(estados)
        else:
            del self.fields['estado']

    def clean(self):
        datos = super().clean()
        if datos.get('desde') and datos.get('hasta') and datos['desde'] > datos['hasta']:
            raise forms.ValidationError('La fecha inicial debe ser anterior o igual a la final.')
        return datos
