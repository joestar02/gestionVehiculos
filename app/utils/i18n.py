# Simple i18n helper for templates
# Provides a small filter `t` that maps internal enum values to Spanish labels.
# This is intentionally minimal - for full i18n use Flask-Babel.

TRANSLATIONS = {
    # general
    'available': 'Disponible',
    'in_use': 'En Uso',
    'maintenance': 'Mantenimiento',
    'out_of_service': 'Fuera de Servicio',
    'pending': 'Pendiente',
    'paid': 'Pagado',
    'overdue': 'Vencido',
    'exempt': 'Exento',
    'bank_transfer': 'Transferencia Bancaria',
    'card': 'Tarjeta',
    'cash': 'Efectivo',
    'direct_debit': 'Domiciliación',

    # fuel types
    'gasoline': 'Gasolina',
    'diesel': 'Diésel',
    'electric': 'Eléctrico',
    'hybrid': 'Híbrido',
    'lpg': 'GLP',

    # driver/license/document
    'Passport': 'Pasaporte',
    'DNI': 'DNI',
    'NIE': 'NIE',

    # generic uppercase variants
    'ivtm': 'IVTM',
    'favorable': 'Favorable',
    'desfavorable': 'Desfavorable',
    'negativa': 'Negativa',
    'passed': 'Aprobada',
    'failed': 'No Aprobada',
    'expired': 'Vencida',

    # fine types
    'speeding': 'Exceso de Velocidad',
    'parking': 'Estacionamiento',
    'traffic_light': 'Semáforo',
    'documentation': 'Documentación',
    'other': 'Otra',

    # other
    'appealed': 'Recurrida',
    'dismissed': 'Anulada',
}


def translate(value):
    if value is None:
        return ''
    key = str(value)
    # Try direct lookup
    if key in TRANSLATIONS:
        return TRANSLATIONS[key]
    # Try lower-case lookup
    lk = key.lower()
    if lk in TRANSLATIONS:
        return TRANSLATIONS[lk]
    # If value looks like an enum name with underscores, prettify
    return key.replace('_', ' ').capitalize()
