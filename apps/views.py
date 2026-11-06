from datetime import date, timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q, Sum
from django.db.models.deletion import ProtectedError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from .catalogo import SECCIONES
from .forms import RegistroForm, FiltroReporteForm
from .models import Cita, Odontologo, Paciente


def configuracion(request, seccion, accion='view'):
    info = SECCIONES.get(seccion)
    if not info:
        raise Http404('Módulo no disponible.')
    if not request.user.has_perm(f'apps.{accion}_{info["modelo"]._meta.model_name}'):
        raise PermissionDenied('Tu cuenta no tiene permiso para esta operación. Contacta al administrador.')
    return info


def consulta(info, texto=''):
    registros = info['modelo'].objects.all()
    if info.get('relaciones'):
        registros = registros.select_related(*info['relaciones'])
    if texto:
        filtro = Q()
        for campo in info['buscar']:
            filtro |= Q(**{campo + '__icontains': texto})
        registros = registros.filter(filtro)
    return registros


def contexto_menu(request):
    return {'menu': [(clave, info['titulo']) for clave, info in SECCIONES.items()
                     if request.user.has_perm(f'apps.view_{info["modelo"]._meta.model_name}')]}


@never_cache
def ingresar(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    formulario = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and formulario.is_valid():
        login(request, formulario.get_user())
        request.session.set_expiry(60 * 60 * 24 * 14 if request.POST.get('recordarme') else 0)
        return redirect('inicio')
    return render(request, 'control/login.html', {'formulario': formulario, 'registro_abierto': settings.REGISTRATION_OPEN})


@never_cache
def registro(request):
    if not settings.REGISTRATION_OPEN:
        raise Http404('El registro está cerrado. Contacta al administrador.')
    if request.user.is_authenticated:
        return redirect('inicio')
    formulario = RegistroForm(request.POST or None)
    if request.method == 'POST' and formulario.is_valid():
        usuario = formulario.save()
        login(request, usuario)
        request.session.set_expiry(0)
        messages.success(request, 'Cuenta creada. Solicita al administrador los permisos de tu puesto para acceder a los módulos.')
        return redirect('inicio')
    return render(request, 'control/registro.html', {'formulario': formulario})


@login_required
@require_POST
def salir(request):
    logout(request)
    return redirect('login')


@never_cache
@login_required
def inicio(request):
    indicadores = []
    for clave in ['pacientes', 'citas', 'tratamientos', 'diagnosticos']:
        info = SECCIONES[clave]
        if request.user.has_perm(f'apps.view_{info["modelo"]._meta.model_name}'):
            indicadores.append((clave, info['titulo'], info['modelo'].objects.count()))
    hoy = timezone.localdate()
    try:
        seleccion = date.fromisoformat(request.GET.get('fecha', str(hoy)))
        if not 1901 <= seleccion.year <= 9998:
            seleccion = hoy
    except ValueError:
        seleccion = hoy
    lunes = seleccion - timedelta(days=seleccion.weekday())
    semana = [lunes + timedelta(days=i) for i in range(7)]
    proximas = []
    agenda_dia = []
    resumen_hoy = {'total': 0, 'atendidas': 0, 'pendientes': 0}
    if request.user.has_perm('apps.view_cita'):
        citas = Cita.objects.select_related('paciente', 'odontologo')
        proximas = citas.filter(fecha__gte=hoy, estado__in=['Pendiente', 'Confirmada']).order_by('fecha', 'hora')[:6]
        agenda_dia = citas.filter(fecha=seleccion).order_by('hora')
        de_hoy = citas.filter(fecha=hoy).exclude(estado='Cancelada')
        resumen_hoy = {'total': de_hoy.count(), 'atendidas': de_hoy.filter(estado='Atendida').count(),
                      'pendientes': de_hoy.filter(estado__in=['Pendiente', 'Confirmada']).count()}
    return render(request, 'control/inicio.html', {**contexto_menu(request), 'indicadores': indicadores,
        'proximas': proximas, 'hoy': hoy, 'semana': semana, 'seleccion': seleccion,
        'anterior': seleccion - timedelta(days=7), 'siguiente': seleccion + timedelta(days=7),
        'agenda_dia': agenda_dia, 'resumen_hoy': resumen_hoy})


@never_cache
@login_required
def listado(request, seccion):
    info = configuracion(request, seccion)
    q = request.GET.get('q', '').strip()[:100]
    pagina = Paginator(consulta(info, q), 15).get_page(request.GET.get('pagina'))
    return render(request, 'control/listado.html', {**contexto_menu(request), 'info': info, 'seccion': seccion,
        'pagina': pagina, 'q': q, 'puede_agregar': request.user.has_perm(f'apps.add_{info["modelo"]._meta.model_name}'),
        'puede_editar': request.user.has_perm(f'apps.change_{info["modelo"]._meta.model_name}'),
        'puede_eliminar': request.user.has_perm(f'apps.delete_{info["modelo"]._meta.model_name}')})


@never_cache
@login_required
def guardar(request, seccion, pk=None):
    info = configuracion(request, seccion, 'change' if pk else 'add')
    objeto = get_object_or_404(info['modelo'], pk=pk) if pk else None
    formulario = info['formulario'](request.POST if request.method == 'POST' else None, instance=objeto)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Serializar reservas sobre los mismos profesionales/pacientes.
                if seccion == 'citas':
                    for modelo, campo in [(Odontologo, 'odontologo'), (Paciente, 'paciente')]:
                        identificador = request.POST.get(campo, '')
                        if identificador.isdecimal():
                            list(modelo.objects.select_for_update().filter(pk=identificador))
                if formulario.is_valid():
                    formulario.save()
                    messages.success(request, 'Registro actualizado correctamente.' if pk else 'Registro guardado correctamente.')
                    return redirect('listado', seccion=seccion)
        except IntegrityError:
            formulario.add_error(None, 'No se pudo guardar. Revisa los datos y vuelve a intentarlo.')
    return render(request, 'control/formulario.html', {**contexto_menu(request), 'formulario': formulario,
                  'info': info, 'seccion': seccion, 'editando': bool(pk)})


@login_required
@require_POST
def eliminar(request, seccion, pk):
    info = configuracion(request, seccion, 'delete')
    objeto = get_object_or_404(info['modelo'], pk=pk)
    try:
        objeto.delete()
        messages.success(request, 'Registro eliminado correctamente.')
    except ProtectedError:
        messages.error(request, 'Este registro tiene información relacionada y no se puede eliminar.')
    return redirect('listado', seccion=seccion)


@never_cache
@login_required
def reportes(request, seccion='citas'):
    info = configuracion(request, seccion)
    if 'fecha' not in info:
        raise Http404('Este módulo no tiene reportes.')
    estados = info['modelo']._meta.get_field('estado').choices if seccion in ['citas', 'tratamientos'] else None
    filtro = FiltroReporteForm(request.GET, estados=estados)
    registros = info['modelo'].objects.none()
    total = None
    if filtro.is_valid():
        datos = filtro.cleaned_data
        registros = consulta(info, datos.get('q', ''))
        if datos.get('desde'):
            registros = registros.filter(**{info['fecha'] + '__gte': datos['desde']})
        if datos.get('hasta'):
            registros = registros.filter(**{info['fecha'] + '__lte': datos['hasta']})
        if datos.get('estado'):
            registros = registros.filter(estado=datos['estado'])
        if seccion == 'tratamientos':
            total = registros.aggregate(total=Sum('costo'))['total'] or 0
    opciones = [(clave, datos['titulo']) for clave, datos in SECCIONES.items() if 'fecha' in datos and request.user.has_perm(f'apps.view_{datos["modelo"]._meta.model_name}')]
    return render(request, 'control/reportes.html', {**contexto_menu(request), 'opciones': opciones,
        'info': info, 'seccion': seccion, 'filtro': filtro, 'registros': registros, 'total': total})


@never_cache
@login_required
def imprimir(request, seccion, pk):
    info = configuracion(request, seccion)
    if 'fecha' not in info:
        raise Http404('Documento no disponible.')
    objeto = get_object_or_404(consulta(info), pk=pk)
    cita = objeto
    for parte in info['clinico'].split('.'):
        if parte:
            cita = getattr(cita, parte)
    campos = [(campo.verbose_name.capitalize(), campo.name) for campo in info['modelo']._meta.fields if campo.name != 'id']
    return render(request, 'control/imprimir.html', {**contexto_menu(request), 'objeto': objeto, 'info': info,
                 'seccion': seccion, 'campos': campos, 'cita': cita})
