# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Estudiante(models.Model):
    _name = 'estudiante.estudiante'
    _description = 'Estudiante'

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

    name = fields.Char()
    grado = fields.Char()
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
    direccion = fields.Char(string='Dirección')

class aula(models.Model):
    _name = 'estudiante.aula'
    _description = 'Aula'

    name = fields.Char(string='Nombre del aula', required=True)
    estudiante = fields.One2many('estudiante.estudiante','name_aula', string='Estudiantes')
    total_estudiantes = fields.Integer(string='Total estudiantes/aula', compute='_compute_total_estudiantes', store=True)
    materia = fields.Many2many('estudiante.materia', string='Materia')
    profesor_de_aula = fields.Many2one('estudiante.profesor', string='Profesor Asignado')
    nro_sillas = fields.Integer(string='Numero de sillas', required=True)
    descripcion = fields.Text(string='Descripción')
    
    @api.depends('estudiante')
    def _compute_total_estudiantes(self):
        for aula in self:
            aula.total_estudiantes = len(aula.estudiante)

    
class Tutor(models.Model):
    _name = 'estudiante.tutor'
    _description = 'Tutor'

    name = fields.Char(string='Nombre del Tutor', required=True)
    cel = fields.Char(string='Celular')
    correo = fields.Char(string='Correo Electrónico')
    direccion = fields.Char(string='Dirección')
    relacion = fields.Selection([
        ('padre', 'Padre'),
        ('madre', 'Madre'),
        ('otros', 'Otros (escriba el tipo de relación)')
    ], string='Relación con el Estudiante', required=True)
    relacion_otros = fields.Char(string='Otra Relación')