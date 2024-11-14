# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dotenv import load_dotenv
import os
import webbrowser
import boto3
import base64

# Cargar variables desde el archivo .env
load_dotenv()

# Ahora puedes acceder a las variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')


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
    materia = fields.Many2many('estudiante.materia', string='Materias')
    name_tutor = fields.Many2one('estudiante.tutor', string='Tutor')
    profesor_asignado = fields.Many2one('estudiante.profesor', string='Profesor Asignado')
    promedio_notas = fields.Float(string='Promedio de Notas', compute='_compute_promedio_notas', store=True)
    mensualidad_ids = fields.One2many('estudiante.mensualidad', 'estudiante_id', string='Mensualidades')
    horario_ids = fields.Many2many('estudiante.horario', string='Horarios')
    user_id = fields.Many2one('res.users', string='Usuario', ondelete='set null')
    password = fields.Char(string='Contraseña', help="Establezca una contraseña para el usuario asociado")
    show_password = fields.Boolean(string="Mostrar contraseña", default=True)
    estudiante_chat_ids = fields.Many2many('mail.channel', string="Chats de Materias", compute='_compute_estudiante_chat_ids')
    
    @api.depends('materia')
    def _compute_estudiante_chat_ids(self):
        for estudiante in self:
            estudiante.estudiante_chat_ids = estudiante.mapped('materia.chat_channel_id')
            
    def agregar_a_materia_chat(self, materia_id):
        materia = self.env['estudiante.materia'].browse(materia_id)
        if materia.chat_channel_id:
            materia.chat_channel_id.write({'channel_partner_ids': [(4, self.user_id.partner_id.id)]})

    @api.depends('nota')
    def _compute_promedio_notas(self):
        for estudiante in self:
            total_notas = sum(nota.nota for nota in estudiante.nota)
            count_notas = len(estudiante.nota)
            estudiante.promedio_notas = total_notas / count_notas if count_notas > 0 else 0

    @api.model
    def create(self, vals):
        # Crear un usuario en Odoo cuando se cree un estudiante
        if 'correo' in vals and 'password' in vals:
            usuario_vals = {
                'name': vals['name'],
                'login': vals['correo'],
                'email': vals['correo'],
                'password': vals['password'],
                'groups_id': [(6, 0, [
                    self.env.ref('estudiante.group_estudiante').id,
                    self.env.ref('base.group_user').id,  # Usuario interno (acceso general)
                    self.env.ref('base.group_partner_manager').id,  # Acceso a Contactos
                ])]  # Asigna el grupo de estudiantes
            }
            usuario = self.env['res.users'].sudo().create(usuario_vals)
            vals['user_id'] = usuario.id  # Asocia el usuario creado al estudiante
            vals['show_password'] = False  # Oculta el campo de contraseña después de la creación del usuario

        # Llamada al super para crear el registro de estudiante
        estudiante = super(Estudiante, self).create(vals)

        # Asocia al estudiante al chat de cada materia si existe en 'vals'
        if 'materia' in vals:
            for materia in estudiante.materia:
                estudiante.agregar_a_materia_chat(materia.id)

        return estudiante
    
    
    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            self.password = ''  # Limpia el valor de la contraseña
            self.show_password = False
    

class Profesor(models.Model):
    _name = 'estudiante.profesor'
    _description = 'estudiante.profesor'

    name = fields.Char(string='Nombre del Profesor', required=True)
    run = fields.Char(string='RUN', required=True)
    fecha_nacimiento = fields.Date(string='Fecha de Nacimiento', required=True)
    direccion = fields.Char(string='Dirección', required=True)
    materia = fields.Many2one('estudiante.materia', string='Materias')
    infraestructura = fields.Many2one('estudiante.infraestructura')
    correo = fields.Char(string='Correo Electrónico', required=True)
    celular = fields.Char(string='Número de Celular', required=True)
    user_id = fields.Many2one('res.users', string='Usuario',  required=True)
    password = fields.Char(string='Contraseña', help="Establezca una contraseña para el usuario asociado")
    show_password = fields.Boolean(string="Mostrar contraseña", default=True)
    materia_aula_ids = fields.One2many('estudiante.materia.profesor', 'profesor_id', string="Materias y Aulas Asignadas")
    tarea_ids = fields.One2many('estudiante.tarea', 'profesor_id', string='Tareas')
    
    def action_ver_mis_materias(self):
        return {
            'name': 'Mis Materias',
            'type': 'ir.actions.act_window',
            'res_model': 'estudiante.materia.profesor',
            'view_mode': 'kanban,tree,form',
            'domain': [('profesor_id', '=', self.id)],
            'context': {'default_profesor_id': self.id},
        }
    def action_ver_mis_tareas(self):
        return {
            'name': 'Mis Tareas',
            'type': 'ir.actions.act_window',
            'res_model': 'estudiante.tarea',
            'view_mode': 'tree,form',
            'domain': [('profesor_id', '=', self.id)],
            'context': {'default_profesor_id': self.id},
        }
    
    @api.model
    def create(self, vals):
        # Crear un usuario en Odoo cuando se cree un estudiante
        if 'correo' in vals and 'password' in vals:
            usuario_vals = {
                'name': vals['name'],
                'login': vals['correo'],
                'email': vals['correo'],
                'password': vals['password'],
                'groups_id': [(6, 0, [
                    self.env.ref('estudiante.group_profesor').id,  # Grupo de profesores
                    self.env.ref('base.group_user').id,  # Usuario interno
                    self.env.ref('base.group_partner_manager').id,  # Acceso a Contactos
                ])]  # Asigna el grupo de estudiantes
            }
            usuario = self.env['res.users'].sudo().create(usuario_vals)
            vals['user_id'] = usuario.id  # Asocia el usuario creado al estudiante
            vals['show_password'] = False  # Oculta el campo de contraseña después de la creación del usuario
        
        return super(Profesor, self).create(vals)
    
    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            self.password = ''  # Limpia el valor de la contraseña
            self.show_password = False
    

class Materia(models.Model):
    _name = 'estudiante.materia'
    _description = 'estudiante.materia'
    _order = 'grado'

    name = fields.Char(string="Nombre de la Materia", required=True)
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
    profesor = fields.Many2one('res.users', string="Profesor")
    aula = fields.Many2one('estudiante.aula', string='aula')
    nota = fields.Many2one('estudiante.nota', string='Notas')
    total_estudiantes = fields.Integer(string='Total de Estudiantes', compute='_compute_total_estudiantes', store=True)
    chat_channel_id = fields.Many2one('mail.channel', string="Chat de la Materia", readonly=True)
    aula_ids = fields.Many2many('estudiante.aula', string='Aulas')
    
    @api.depends('aula_ids')
    def _compute_total_estudiantes(self):
        for materia in self:
            total_estudiantes = sum(aula.total_estudiantes for aula in materia.aula_ids)
            materia.total_estudiantes = total_estudiantes
            
    def action_view_assignments(self):
        """Abre la vista de asignaciones para esta materia"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Asignaciones',
            'view_mode': 'tree,form',
            'res_model': 'estudiante.asignacion',
            'domain': [('materia_id', '=', self.id)],
            'context': {'default_materia_id': self.id},
        }
        
    @api.model
    def create(self, vals):
        materia = super(Materia, self).create(vals)
        if not materia.chat_channel_id:
            channel = self.env['mail.channel'].create({
                'name': f"Chat de {materia.name}",
                'channel_type': 'chat',
                'public': 'private',
            })
            materia.chat_channel_id = channel.id
        return materia
    
    def agregar_estudiantes_chat(self):
        """ Agrega estudiantes al canal de chat al actualizar la materia """
        if self.chat_channel_id:
            partners = self.aula_ids.mapped('estudiante_ids.user_id.partner_id.id')
            self.chat_channel_id.write({'channel_partner_ids': [(4, partner) for partner in partners]})
            
        
class MateriaProfesor(models.Model):
    _name = 'estudiante.materia.profesor'
    _description = 'Relación Materia-Profesor-Aula'
    _rec_name = 'nombre_completo'

    profesor_id = fields.Many2one('estudiante.profesor', string="Profesor", required=True)  # Cambiado de 'profesor' a 'profesor_id'
    materia_id = fields.Many2one('estudiante.materia', string="Materia", required=True)    # Cambiado de 'materia' a 'materia_id'
    aula_id = fields.Many2one('estudiante.aula', string="Aula", required=True)             # Cambiado de 'name_aula' a 'aula_id'
    nombre_completo = fields.Char(string="Nombre", compute='_compute_nombre_completo', store=True)
    tarea_ids = fields.One2many('estudiante.tarea', 'materia_profesor_id', string="Tareas")  # Actualizado el campo relacionado  
    @api.depends('materia_id', 'aula_id')
    def _compute_nombre_completo(self):
        for record in self:
            if record.materia_id and record.aula_id:
                record.nombre_completo = f"{record.aula_id.name}-{record.materia_id.name}"
            else:
                record.nombre_completo = "Sin asignar"    
    def action_ver_tareas(self):
        return {
            'name': 'Tareas',
            'type': 'ir.actions.act_window',
            'res_model': 'estudiante.tarea',
            'view_mode': 'tree,form',
            'domain': [('materia_profesor_id', '=', self.id)],
            'context': {
                'default_materia_profesor_id': self.id,
                'default_materia_id': self.materia_id.id,
                'default_aula_id': self.aula_id.id,
                'default_profesor_id': self.profesor_id.id
            },
        }
class Asignacion(models.Model):
    _name = 'estudiante.asignacion'
    _description = 'Tareas y prácticos para estudiantes'

    name = fields.Char(string="Título de la Asignación", required=True)
    descripcion = fields.Text(string="Descripción")
    fecha_entrega = fields.Date(string="Fecha de Entrega")
    materia = fields.Many2one('estudiante.materia', string="Materia", required=True)
    profesor = fields.Many2one('res.users', string="Profesor", required=True)
    estudiante_ids = fields.Many2many('res.users', string="Estudiantes", domain=[('groups_id.name', '=', 'Estudiante')])

class Tarea(models.Model):
    _name = 'estudiante.tarea'
    _description = 'Tareas de las materias'
    _rec_name = 'titulo'
    
    titulo = fields.Char(string="Título de la Tarea", required=True)
    descripcion = fields.Text(string="Descripción", required=True)
    fecha_asignacion = fields.Date(string="Fecha de Asignación", default=fields.Date.context_today)
    fecha_entrega = fields.Date(string="Fecha de Entrega", required=True)
    materia_profesor_id = fields.Many2one('estudiante.materia.profesor', string="Materia-Profesor", required=True)  # Nuevo campo
    materia_id = fields.Many2one('estudiante.materia', string="Materia", required=True)
    aula_id = fields.Many2one('estudiante.aula', string="Aula", required=True)
    profesor_id = fields.Many2one('estudiante.profesor', string="Profesor")
    archivo_tarea = fields.Binary(string="Archivo de la Tarea")
    nombre_archivo = fields.Char(string="Nombre del Archivo")
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('publicada', 'Publicada'),
        ('vencida', 'Vencida')
    ], string="Estado", default='borrador')
    entrega_ids = fields.One2many('estudiante.entrega.tarea', 'tarea_id', string="Entregas")
    
    @api.onchange('materia_profesor_id')
    def _onchange_materia_profesor(self):
        if self.materia_profesor_id:
            self.materia_id = self.materia_profesor_id.materia_id
            self.aula_id = self.materia_profesor_id.aula_id
            self.profesor_id = self.materia_profesor_id.profesor_id
    
    def action_publicar(self):
        self.write({'estado': 'publicada'})
        
    @api.constrains('fecha_entrega')
    def _check_fecha_entrega(self):
        for record in self:
            if record.fecha_entrega < record.fecha_asignacion:
                raise ValidationError("La fecha de entrega no puede ser anterior a la fecha de asignación")

class EntregaTarea(models.Model):
    _name = 'estudiante.entrega.tarea'
    _description = 'Entregas de tareas por estudiantes'
    _rec_name = 'tarea_id'

    tarea_id = fields.Many2one('estudiante.tarea', string="Tarea", required=True)
    estudiante_id = fields.Many2one('estudiante.estudiante', string="Estudiante", required=True)
    fecha_entrega = fields.Datetime(string="Fecha de Entrega", default=fields.Datetime.now)
    archivo_entrega = fields.Binary(string="Archivo de Entrega")
    nombre_archivo = fields.Char(string="Nombre del Archivo")
    comentario = fields.Text(string="Comentario del Estudiante")
    calificacion = fields.Float(string="Calificación")
    estado = fields.Selection([
        ('entregada', 'Entregada'),
        ('calificada', 'Calificada'),
        ('retrasada', 'Retrasada')
    ], string="Estado", default='entregada')
    
    @api.model
    def create(self, vals):
        record = super(EntregaTarea, self).create(vals)
        if record.fecha_entrega.date() > record.tarea_id.fecha_entrega:
            record.estado = 'retrasada'
        return record
    def action_entregar(self):
        self.write({
            'estado': 'entregado',
            'fecha_entrega': fields.Datetime.now()
        })
        
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
    horario_ids = fields.One2many('estudiante.horario', 'aula_id', string='Horarios')
    name_infraestructura = fields.Many2one('estudiante.infraestructura', string='Colegio')
    
    @api.depends('estudiante')
    def _compute_total_estudiantes(self):
        for aula in self:
            aula.total_estudiantes = len(aula.estudiante)
            for materia in aula.materia:
                materia._compute_total_estudiantes()
            
         
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

class Horario(models.Model):
    _name = 'estudiante.horario'
    _description = 'Horario de Clases'

    name = fields.Char(string='Clase', required=True)
    aula_id = fields.Many2one('estudiante.aula', string='Aula', required=True)
    materia_id = fields.Many2one('estudiante.materia', string='Materia', required=True)
    profesor_id = fields.Many2one('estudiante.profesor', string='Profesor', required=True)
    dia_semana = fields.Selection([
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado')
    ], string='Día de la Semana', required=True)
    hora_inicio = fields.Float(string='Hora de Inicio', required=True)
    hora_fin = fields.Float(string='Hora de Fin', required=True)

    @api.constrains('hora_inicio', 'hora_fin')
    def _check_hours(self):
        for record in self:
            if record.hora_inicio >= record.hora_fin:
                raise ValidationError('La hora de inicio debe ser anterior a la hora de fin')

class Foro(models.Model):
    _name = 'estudiante.foro'
    _description = 'Foro para estudiantes de la misma materia'
    
    name = fields.Char(string="Título", required=True)
    materia_id = fields.Many2one('estudiante.materia', string="Materia", required=True)
    aula_id = fields.Many2one('estudiante.aula', string="Aula", required=True)
    mensaje_ids = fields.One2many('estudiante.mensaje', 'foro_id', string="Mensajes")
    active = fields.Boolean(default=True)
    fecha_creacion = fields.Datetime(string="Fecha de Creación", default=fields.Datetime.now, readonly=True)
    estudiante_ids = fields.Many2many('res.users', string="Estudiantes Participantes")
    profesor_id = fields.Many2one('estudiante.profesor', string="Profesor Creador")
    
    @api.onchange('materia_id', 'aula_id')
    def _onchange_materia_aula(self):
        """Filtra los estudiantes según la materia y aula seleccionada"""
        if self.materia_id and self.aula_id:
            estudiantes = self.env['estudiante.estudiante'].search([
                ('materia', 'in', self.materia_id.id),  # Estudiantes de la materia
                ('name_aula', '=', self.aula_id.id)  # Estudiantes de la misma aula
            ])
            self.estudiante_ids = [(6, 0, estudiantes.ids)]
    
    def _get_estudiantes_materia(self):
        """Obtiene los estudiantes que están en la materia y aula específica"""
        self.ensure_one()
        estudiantes = self.env['estudiante.estudiante'].search([
            ('materia', 'in', [self.materia_id.id]),
            ('name_aula', '=', self.aula_id.id)
        ])
        return estudiantes
    
    @api.model
    def create(self, vals):
        # Al crear el foro, automáticamente asignar los estudiantes correspondientes
        res = super(Foro, self).create(vals)
        if res.materia_id and res.aula_id:
            estudiantes = res._get_estudiantes_materia()
            if estudiantes:
                res.write({
                    'estudiante_ids': [(6, 0, estudiantes.mapped('user_id').ids)]
                })
        return res

class Mensaje(models.Model):
    _name = 'estudiante.mensaje'
    _description = 'Mensaje en el foro'
    
    foro_id = fields.Many2one('estudiante.foro', string="Foro")
    estudiante_id = fields.Many2one('res.users', string="Estudiante", default=lambda self: self.env.user)
    contenido = fields.Text(string="Mensaje")
    fecha = fields.Datetime(string="Fecha", default=fields.Datetime.now)
    imagen = fields.Binary(string="Imagen")
    audio = fields.Binary(string="Audio")
    video = fields.Binary(string="Video")
    es_inapropiado = fields.Boolean(string="Inapropiado", default=False, readonly=True)
    
    @api.model
    def check_explicit_content(self):
        """
        Usa Amazon Rekognition para verificar si las imágenes o videos contienen contenido explícito.
        """
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION')

        client = boto3.client(
            'rekognition',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )

        if self.imagen:
            image_bytes = base64.b64decode(self.imagen)
            
            response = client.detect_moderation_labels(
                Image={'Bytes': image_bytes},
                MinConfidence=80
            )

            for label in response['ModerationLabels']:
                if label['Name'] in ['Explicit Nudity', 'Pornography', 'Suggestive']:
                    self.es_inapropiado = True
                    return

        self.es_inapropiado = False

    @api.model
    def create(self, vals):
        res = super(Mensaje, self).create(vals)
        res.check_explicit_content()  # Verifica si el contenido es inapropiado al crear el mensaje
        return res

    def write(self, vals):
        res = super(Mensaje, self).write(vals)
        if 'imagen' in vals or 'video' in vals:
            self.check_explicit_content()  # Verifica si el contenido es inapropiado al actualizar el mensaje
        return res
    
    @api.constrains('imagen', 'video')
    def check_explicit_content(self):
        """
        Usa Amazon Rekognition para verificar si las imágenes o videos contienen contenido explícito.
        """
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION')

        # Inicializa el cliente de Rekognition
        client = boto3.client(
            'rekognition',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )

        if self.imagen:
            # Decodifica la imagen de base64
            image_bytes = base64.b64decode(self.imagen)
            
            # Analiza la imagen usando Rekognition
            response = client.detect_moderation_labels(
                Image={'Bytes': image_bytes},
                MinConfidence=80  # Nivel de confianza (ajusta según sea necesario)
            )
            # Revisa si contiene etiquetas de contenido explícito
            for label in response['ModerationLabels']:
                if label['Name'] in ['Explicit Nudity', 'Pornography', 'Suggestive']:
                    raise ValidationError(_("La imagen contiene contenido inapropiado y no puede ser subida al foro."))

        if self.video:
            # Similar a la imagen, aquí puedes implementar la lógica para videos,
            # pero ten en cuenta que el procesamiento de videos requiere un análisis diferente en Rekognition.
            raise ValidationError(_("La detección de contenido explícito en videos no está implementada en este ejemplo."))


class MateriaChat(models.Model):
    _name = 'materia.chat'
    _description = 'Chat de Materia'
    _order = 'fecha_envio desc'

    materia_id = fields.Many2one('estudiante.materia', string="Materia", required=True)
    estudiante_id = fields.Many2one('res.users', string="Estudiante", default=lambda self: self.env.user, required=True)
    mensaje = fields.Text(string="Mensaje", required=True)
    fecha_envio = fields.Datetime(string="Fecha de Envío", default=fields.Datetime.now, required=True)

    @api.constrains('materia_id', 'estudiante_id')
    def _check_materia_estudiante(self):
        for record in self:
            if record.estudiante_id not in record.materia_id.estudiante_ids:
                raise ValidationError("El estudiante debe estar inscrito en la materia para enviar mensajes.")
            
class ResUsers(models.Model):
    _inherit = 'res.users'

    estudiante_ids = fields.One2many('estudiante.estudiante', 'user_id', string="Estudiantes Relacionados")
