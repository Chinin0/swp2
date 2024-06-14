from odoo import models, fields

class Inscripcion(models.Model):
    _name = 'colegio.inscripcion'
    _description = 'Formulario de Inscripción'

    name = fields.Char(string='Nombre del Estudiante', required=True)
    fecha_nacimiento = fields.Date(string='Fecha de Nacimiento')
    direccion = fields.Char(string='Dirección')
    telefono = fields.Char(string='Teléfono')
    email = fields.Char(string='Correo Electrónico')
    grado = fields.Selection([
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria'),
        ('preparatoria', 'Preparatoria')
    ], string='Grado')
