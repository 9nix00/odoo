# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import ensure_db

import werkzeug
import openerp

from openerp.addons.auth_signup.res_users import SignupError


class RemoteAccount(openerp.addons.web.controllers.main.Home):
    @http.route('/remote_account/remote_account/', auth='public')
    def index(self, **kw):
        ensure_db()
        print(http.request.params)
        return "Hello, world"

    @http.route('/remote_account/remote_account/upsert', auth='public', csrf=False)
    def upsert(self, **kw):

        qcontext = request.params.copy()

        # todo:加签名防止他人恶意使用
        sign = qcontext.get('sign')

        values = {
            'login': qcontext.get('email'),
            'name': qcontext.get('name'),
            'password': 'abcbcbcb',
            'partner_id': openerp.SUPERUSER_ID,
            'lang': request.lang
        }

        if not values['name'] or not values['login']:
            raise werkzeug.exceptions.HTTPException

        try:
            db, login, password = request.registry['res.users'].signup(request.cr, openerp.SUPERUSER_ID, values, None)
        except Exception as e:
            return e.message

        request.cr.commit()  # as authenticate will use its own cursor we need to commit the current transaction
        uid = request.session.authenticate(db, login, password)

        if not uid:
            raise werkzeug.exceptions.HTTPException

        # todo: 返回json
        return "ok"

    @http.route('/remote_account/remote_account/remove', auth='public')
    def remove(self, **kw):
        return "Hello, world"

    def get_auth_signup_config(self):
        """retrieve the module config (which features are enabled) for the login page"""

        icp = request.registry.get('ir.config_parameter')
        return {
            'signup_enabled': icp.get_param(request.cr, openerp.SUPERUSER_ID, 'auth_signup.allow_uninvited') == 'True',
            'reset_password_enabled': icp.get_param(request.cr, openerp.SUPERUSER_ID, 'auth_signup.reset_password') == 'True',
        }

    def get_auth_signup_qcontext(self):
        """ Shared helper returning the rendering context for signup and reset password """
        qcontext = request.params.copy()
        qcontext.update(self.get_auth_signup_config())

        print(qcontext)

        if qcontext.get('token'):
            try:
                # retrieve the user info (name, login or email) corresponding to a signup token
                res_partner = request.registry.get('res.partner')
                token_infos = res_partner.signup_retrieve_info(request.cr, openerp.SUPERUSER_ID, qcontext.get('token'))
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
        return qcontext
