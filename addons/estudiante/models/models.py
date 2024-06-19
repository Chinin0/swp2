# -*- coding: utf-8 -*-

from odoo import models, fields, api
import webbrowser


class Estudiante(models.Model):
    _name = 'estudiante.estudiante'
    _description = 'Estudiante'
    _order = 'name'

    name = fields.Char(string='Nombre Completo', required=True)
    cel = fields.Char(string='Celular')
    correo = fields.Char(string='Correo Electrónico')
    fecha_nacimiento = fields.Date(string='Fecha de Nacimiento')
    direccion = fields.Char(string='Dirección')
    name_infraestructura = fields.Many2one('estudiante.infraestructura', string='Colegio')
    name_aula = fields.Many2one('estudiante.aula', string='aula')
    nota = fields.Many2many('estudiante.nota', string='Notas')
    materia = fields.Many2many('estudiante.materia', string='materia')
    name_tutor = fields.Many2one('estudiante.tutor', string='Tutor')
    profesor_asignado = fields.Many2one('estudiante.profesor', string='Profesor Asignado')
    promedio_notas = fields.Float(string='Promedio de Notas', compute='_compute_promedio_notas', store=True)
    mensualidad_ids = fields.One2many('estudiante.mensualidad', 'estudiante_id', string='Mensualidades')
    
    @api.depends('nota')
    def _compute_promedio_notas(self):
        for estudiante in self:
            total_notas = sum(nota.nota for nota in estudiante.nota)
            count_notas = len(estudiante.nota)
            estudiante.promedio_notas = total_notas / count_notas if count_notas > 0 else 0
    

class profesor(models.Model):
    _name = 'estudiante.profesor'
    _description = 'estudiante.profesor'

    name = fields.Char(string='Nombre del Profesor', required=True)
    run = fields.Char(string='RUN', required=True)
    fecha_nacimiento = fields.Date(string='Fecha de Nacimiento', required=True)
    direccion = fields.Char(string='Dirección', required=True)
    materia = fields.Many2one('estudiante.materia', string='Materias')
    infraestructura = fields.Many2one('estudiante.infraestructura')
    correo = correo = fields.Char(string='Correo Electrónico', required=True)
    celular = fields.Char(string='Número de Celular', required=True)
    

class materia(models.Model):
    _name = 'estudiante.materia'
    _description = 'estudiante.materia'
    _order = 'grado'

    name = fields.Char()
    grado = fields.Selection([
        ('1', '1° Grado'),
        ('2', '2° Grado'),
        ('3', '3° Grado'),
        ('4', '4° Grado'),
        ('5', '5° Grado'),
        ('6', '6° Grado'),
    ], string='grado', required=True)
    seccion = fields.Selection([
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria')
    ], string='Sección', required=True)
    profesor = fields.Many2one('estudiante.profesor', string='Profesor Asignado')
    aula = fields.Many2one('estudiante.aula', string='aula')
    nota = fields.Many2one('estudiante.nota', string='Notas')
    
class nota(models.Model):
    _name = 'estudiante.nota'
    _description = 'nota'

    nota = fields.Float(string='Notas', required=True)
    estudiante = fields.Many2one('estudiante.estudiante', string='estudiante', required=True)
    materia = fields.Many2one('estudiante.materia', string='materia', required=True)
    profesor = fields.Many2one('estudiante.profesor', string='Profesor Asignado', required=True)
    descripcion = fields.Text(string='descripción')

class infraestructura(models.Model):
    _name = 'estudiante.infraestructura'
    _description = 'infraestructura'

    name = fields.Char(string='Nombre del colegio', required=True)
    nro_pisos = fields.Integer(string='Numero de pisos', required=True)
    total_aulas = fields.Integer(string='Total de aulas', compute='_compute_total_aulas', store=True)
    direccion = fields.Char(string='Dirección')
    aula_ids = fields.One2many('estudiante.aula', 'name_infraestructura', string='Aulas')
    
    @api.depends('aula_ids')
    def _compute_total_aulas(self):
        for infraestructura in self:
            infraestructura.total_aulas = self.env['estudiante.aula'].search_count([('name_infraestructura', '=', infraestructura.id)])

class aula(models.Model):
    _name = 'estudiante.aula'
    _description = 'Aula'
    _order = 'name'

    name = fields.Char(string='Nombre del aula', required=True)
    estudiante = fields.One2many('estudiante.estudiante','name_aula', string='Estudiantes')
    total_estudiantes = fields.Integer(string='Total estudiantes/aula', compute='_compute_total_estudiantes', store=True)
    materia = fields.Many2many('estudiante.materia', string='Materia')
    profesor_de_aula = fields.Many2one('estudiante.profesor', string='Profesor Asignado')
    nro_sillas = fields.Integer(string='Numero de sillas', required=True)
    descripcion = fields.Text(string='Descripción')
    grado = fields.Selection([
        ('1', '1° Grado'),
        ('2', '2° Grado'),
        ('3', '3° Grado'),
        ('4', '4° Grado'),
        ('5', '5° Grado'),
        ('6', '6° Grado'),
    ], string='Grado', required=True)
    seccion = fields.Selection([
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria')
    ], string='Sección', required=True)
    name_infraestructura = fields.Many2one('estudiante.infraestructura', string='Colegio')
    
    @api.depends('estudiante')
    def _compute_total_estudiantes(self):
        for aula in self:
            aula.total_estudiantes = len(aula.estudiante)
            
    """ @api.onchange('grado', 'seccion')
    def _onchange_grado_seccion(self):
        if self.grado and self.seccion:
            return {'domain': {'materia': [('grado', '=', self.grado), ('seccion', '=', self.seccion)]}}
        else:
            return {'domain': {'materia': []}} """
        
    """ @api.depends('grado', 'seccion')
    def _compute_materias(self):
        for aula in self:
            aula.materia = self.env['estudiante.materia'].search([('grado', '=', aula.grado), ('seccion', '=', aula.seccion)]) """
            
                
class TutorEstudianteRel(models.Model):
    _name = 'estudiante.tutor_estudiante_rel'
    _description = 'Relación entre Tutor y Estudiante'

    tutor_id = fields.Many2one('estudiante.tutor', string='Tutor', required=True)
    estudiante_id = fields.Many2one('estudiante.estudiante', string='Estudiante', required=True)
    relacion = fields.Selection([
        ('padre', 'Padre'),
        ('madre', 'Madre'),
        ('otros', 'Otro')
    ], string='Relación con el Estudiante', required=True)
    relacion_otros = fields.Char(string='Otra Relación')

class Tutor(models.Model):
    _name = 'estudiante.tutor'
    _description = 'Tutor'

    name = fields.Char(string='Nombre del Tutor', required=True)
    cel = fields.Char(string='Celular')
    correo = fields.Char(string='Correo Electrónico')
    direccion = fields.Char(string='Dirección')
    estudiante_rel_ids = fields.One2many('estudiante.tutor_estudiante_rel', 'tutor_id', string='Estudiantes a Cargo')
    
    def action_send_whatsapp(self):
        for record in self:
            if record.cel:
                phone_number = record.cel
                whatsapp_url = f'https://api.whatsapp.com/send?phone={phone_number}'
                return {
                    'type': 'ir.actions.act_url',
                    'url': whatsapp_url,
                    'target': 'new',
                }
            else:
                raise UserError("El campo 'Celular' está vacío.")
            
            
            
class Mensualidad(models.Model):
    _name = 'estudiante.mensualidad'
    _description = 'Mensualidad'

    name = fields.Char(string='Referencia de Pago')
    estudiante_id = fields.Many2one('estudiante.estudiante', string='Estudiante', required=True)
    fecha_pago = fields.Date(string='Fecha de Pago', required=True, default=fields.Date.context_today)
    monto = fields.Float(string='Monto Pagado', required=True)
    estado_pago = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
    ], string='Estado del Pago', default='pendiente')

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('estudiante.mensualidad') or 'Nuevo'
        result = super(Mensualidad, self).create(vals)
        return result
