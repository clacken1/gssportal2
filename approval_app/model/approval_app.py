from odoo import models, fields,api, _
from lxml import etree
from odoo.exceptions import Warning, ValidationError


class ApprovalApp(models.Model):
    _name='approval.app'

    name=fields.Char('Job Name')
    submission_date=fields.Datetime('Submission Date')
    admin_officer=fields.Char('Admin Officer')
    admin_appro_date=fields.Datetime('Admin Approval Date')
    osd_officer_one=fields.Selection([('kim_possible', 'Kim Possible'), ('john_brown', 'John Brown')], string='OSD Officer')
    date_osd_officer_assigned=fields.Datetime('Date OSD Officer Assigned')
    date_approved_by_ocd_officer=fields.Datetime('Date Approved by OSD Officer')
    date_sent_to_lead_group=fields.Datetime('Date sent to Lead Group')
    date_appro_by_lead_group=fields.Datetime('Date Approved by Lead Group')
    date_sent_to_council=fields.Datetime('Date sent to Council')
    date_return_from_council=fields.Datetime('Date returned from Council')
    relese_date_to=fields.Datetime('Release Date To')
    job_title=fields.Char('Job Title')
    purpose_job=fields.Char('Purpose of Job	')
    level=fields.Selection([],string='Level')
    modality=fields.Selection([('ato', 'ATO'), ('internal', 'Internal')], string='Modality')
    no_of_person=fields.Integer('Number of persons expected to be trained')

    lead_group_member=fields.One2many('group.member','app_id',string='Lead Group Member	')
    contact =fields.Many2one('res.partner',string='Contact')
    office_phone=fields.Char('Office Phone')
    cell_phone=fields.Char('Cell Phone')
    email=fields.Char('Email')
    address=fields.Char('Address')
    industry=fields.Many2one('industry.company')
    sub_sector=fields.Many2one('sub.sector')
    date=fields.Date('Date')
    staff_headcount=fields.Integer('Staff Headcount	')
    vale_attr=fields.Text('Values and attitudes	')
    job_task=fields.One2many('task.description','app_1_id')
    # stage_id=fields.Many2one('approval.stage')
    stages=fields.Selection([
        ('new', 'New'),
        ('submission', 'Submissions'),
        ('admin_approval', 'Administrator approval'),
        ('osd_officer', 'OSD Officer assigned'),
        ('send_lead_group', 'Sent to lead group for approval'),
        ('sent_council', 'Sent to council for approval'),
        ('release_date','Release date for public use'),
    ], string="Stages", default='new')

    application_id=fields.Many2one('res.users','Login Applicant')

    def action_approval_submission(self):
        self.write({
            'stages':'submission',
            'submission_date':fields.datetime.now()
        })

    def action_admin_approval_submission(self):
        if not self.admin_officer:
            raise ValidationError(_('Please Add Admin Officer Name'))
        self.write({
            'stages': 'admin_approval',
            'admin_appro_date': fields.datetime.now()
        })

    def action_osd_officer_submission(self):
        if not self.osd_officer_one:
            raise ValidationError(_('Please Add OSD Officer Name'))
        self.write({
            'stages': 'osd_officer',
            'date_approved_by_ocd_officer': fields.datetime.now()
        })

    def action_send_to_lead_submission(self):
        self.write({
            'stages': 'send_lead_group',
            'date_sent_to_lead_group': fields.datetime.now()
        })

    def action_send_to_council_submission(self):
        self.write({
            'stages': 'sent_council',
            'date_sent_to_council': fields.datetime.now()
        })

    def action_relase_date_submission(self):
        self.write({
            'stages': 'release_date',
            'relese_date_to': fields.datetime.now()
        })

    @api.model
    def default_get(self, fields):
        res = super(ApprovalApp, self).default_get(fields)
        application_id = False
        if self.env.user:
            application_id = self.env.user.id
            application_id=self.env['res.users'].browse(application_id)
        res.update({
            'application_id': application_id.id,
            'contact':application_id.partner_id.id
        })
        return res


    @api.onchange('contact')
    def _onchange_contact(self):
        if self.contact:
            self.office_phone=self.contact.phone
            self.email=self.contact.email
            if self.contact.street:
                street=self.contact.street
            else:
                street=''
            if self.contact.street2:
                street2 = self.contact.street2
            else:
                street2 = ''
            self.address=street + street2

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        # OVERRIDE to add the 'available_partner_bank_ids' field dynamically inside the view.
        # TO BE REMOVED IN MASTER
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        group_id = self.env['res.users'].has_group('approval_app.admin_user_access_id')
        doc = etree.XML(res['arch'])

        if group_id:
            if view_type == 'tree':
                nodes = doc.xpath("//tree[@string='Approval App']")

                for node in nodes:
                    node.set('create', '0')

                res['arch'] = etree.tostring(doc)
            elif view_type == 'form':
                nodes = doc.xpath("//form[@string='Approval App']")

                for node in nodes:
                    node.set('create', '0')

                res['arch'] = etree.tostring(doc)

            elif view_type == 'kanban':
                nodes = doc.xpath("//kanban")

                for node in nodes:
                    node.set('create', '0')

                res['arch'] = etree.tostring(doc)

        return res
class GroupMember(models.Model):
    _name='group.member'

    app_id=fields.Many2one('approval.app')
    name=fields.Char('Name')
    email=fields.Char('Email')
    contact=fields.Char('Contact')
    title =fields.Selection([
        ('Chairman', 'Chairman'),
        ('Vice-Chairman', 'Vice-Chairman'),
    ('Member', 'Member')], string="Title", copy=False)


class IndustryCompany(models.Model):
    _name='industry.company'

    name=fields.Char('Name')


class SubSector(models.Model):
    _name = 'sub.sector'

    name = fields.Char('Name')


class TaskDescription(models.Model):
    _name='task.description'

    name=fields.Char('Job Tasks')
    detail_task=fields.Char('Details Of Task')
    app_1_id=fields.Many2one('approval.app')


class ApprovalStage(models.Model):
    _name='approval.stage'

    name=fields.Char('Name')


class ResPartner(models.Model):
    _inherit = 'res.partner'




