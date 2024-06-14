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
    name_colegio = fields.Many2one('estudiante.colegio', string='Colegio')
    name_curso = fields.Many2one('estudiante.curso', string='Curso')
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
    colegio = fields.Many2one('estudiante.colegio')
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
    curso = fields.Many2one('estudiante.curso', string='curso')
    nota = fields.Many2one('estudiante.nota', string='Notas')
    
class nota(models.Model):
    _name = 'estudiante.nota'
    _description = 'nota'

    nota = fields.Float(string='Notas', required=True)
    estudiante = fields.Many2one('estudiante.estudiante', string='estudiante', required=True)
    materia = fields.Many2one('estudiante.materia', string='materia', required=True)
    profesor = fields.Many2one('estudiante.profesor', string='Profesor Asignado', required=True)
    descripcion = fields.Text(string='descripción')

class Colegio(models.Model):
    _name = 'estudiante.colegio'
    _description = 'Colegio'

    name = fields.Char(string='Nombre del Colegio', required=True)
    direccion = fields.Char(string='Dirección')

class Curso(models.Model):
    _name = 'estudiante.curso'
    _description = 'Curso'

    name = fields.Char(string='Nombre del Curso', required=True)
    estudiante = fields.Many2many('estudiante.estudiante', string='estudiante')
    materia = fields.Many2many('estudiante.materia', string='materia')
    profesor_de_curso = fields.Many2one('estudiante.profesor', string='Profesor Asignado')
    descripcion = fields.Text(string='Descripción')
    
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