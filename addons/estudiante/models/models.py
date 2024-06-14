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
    name_tutor = fields.Many2one('estudiante.tutor', string='Tutor')
    profesor_asignado = fields.Many2one('estudiante.profesor', string='Profesor Asignado')

class profesor(models.Model):
    _name = 'estudiante.profesor'
    _description = 'estudiante.profesor'

    name = fields.Char(string='Nombre del Profesor', required=True)
    run = fields.Char(string='RUN', required=True)
    fecha_nacimiento = fields.Date(string='Fecha de Nacimiento', required=True)
    direccion = fields.Char(string='Dirección', required=True)
    materia = fields.Many2one('estudiante.materia')
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

class Colegio(models.Model):
    _name = 'estudiante.colegio'
    _description = 'Colegio'

    name = fields.Char(string='Nombre del Colegio', required=True)
    direccion = fields.Char(string='Dirección')

class Curso(models.Model):
    _name = 'estudiante.curso'
    _description = 'Curso'

    name = fields.Char(string='Nombre del Curso', required=True)
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