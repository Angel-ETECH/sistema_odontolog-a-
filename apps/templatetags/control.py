from datetime import date, datetime, time
from decimal import Decimal
from django import template

register = template.Library()

@register.filter
def valor(objeto, campo):
    dato = getattr(objeto, campo, '')
    if isinstance(dato, datetime):
        return dato.strftime('%d/%m/%Y %H:%M')
    if isinstance(dato, date):
        return dato.strftime('%d/%m/%Y')
    if isinstance(dato, time):
        return dato.strftime('%H:%M')
    if isinstance(dato, Decimal):
        return f'S/ {dato:,.2f}'
    return dato if dato not in ('', None) else '—'

@register.filter
def etiqueta(modelo, campo):
    return modelo._meta.get_field(campo).verbose_name.replace('_', ' ').capitalize()
