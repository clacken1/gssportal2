# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_users import SignupError

import  werkzeug
import logging
import  uuid

_logger = logging.getLogger(__name__)

class ConfirmAccount(http.Controller):
    @http.route('/account-confirmation', type='http', auth="public", website=True)
    def confirmation(self, **kw):
        token = kw.get('token', '')

        if token:
            user = request.env['res.users'].sudo().with_context(active_test=False).search(
                [('confirm_token', '=', token)])

            if user:
                user.active = True
                user.confirm_token = ''

                return request.render('signup_email_verification.confirmation', {
                    'status': 'confirmed'
                })
            else:
                return request.render('signup_email_verification.confirmation', {
                    'status': 'invalid'
                })

        return request.render('signup_email_verification.confirmation', {})

class AuthSignupHome(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('token'):
                    user_sudo = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))])
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                               raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().with_context(
                            lang=user_sudo.lang,
                            auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
                        ).send_mail(user_sudo.id, force_send=True)

                    return super(AuthSignupHome, self).web_login(*args, **kw)
                else:
                    user_sudo = request.env['res.users'].sudo().with_context(active_test=False).search(
                        [('login', '=', qcontext.get('login'))])
                    user_sudo.active = False
                    user_sudo.confirm_token = uuid.uuid4().hex

                    template = request.env.ref('signup_email_verification.user_account_activation_mail',
                                               raise_if_not_found=False)

                    if user_sudo and template:
                        template.sudo().with_context(
                            lang=user_sudo.lang,
                        ).send_mail(user_sudo.id, force_send=True)

                    return request.redirect('/account-confirmation')

            except UserError as e:
                qcontext['error'] = e.name or e.value
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def _signup_with_values(self, token, values):
        db, login, password = request.env['res.users'].sudo().signup(values, token)
        request.env.cr.commit()