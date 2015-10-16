# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import ensure_db

import werkzeug
import openerp

from openerp.addons.auth_signup.res_users import SignupError, random_token, res_users

class RemoteAccount(openerp.addons.web.controllers.main.Home):
    @http.route('/remote_account/remote_account/', auth='public')
    def index(self, **kw):
        raise werkzeug.exceptions.HTTPException

    @http.route('/remote_account/remote_account/upsert', auth='public', csrf=False)
    def upsert(self, **kw):

        qcontext = request.params.copy()

        # todo:加签名防止他人恶意使用
        sign = qcontext.get('sign')

        values = {
            'login': qcontext.get('email'),
            'name': qcontext.get('name'),
            'password': random_token(),
            'partner_id': openerp.SUPERUSER_ID,
            'lang': request.lang
        }

        if not values['name'] or not values['login']:
            raise werkzeug.exceptions.HTTPException

        try:
            db, login, password = request.registry['res.users'].signup(request.cr, openerp.SUPERUSER_ID, values, None)
        except Exception as e:
            # 重复等无视
            pass
        request.cr.commit()  # as authenticate will use its own cursor we need to commit the current transaction


        # todo:封装
        uid = request.registry['res.users'].try_login(values['login'])

        if not uid:
            raise werkzeug.exceptions.Forbidden

        wsgienv = request.httprequest.environ

        env = dict(
            base_location=request.httprequest.url_root.rstrip('/'),
            HTTP_HOST=wsgienv['HTTP_HOST'],
            REMOTE_ADDR=wsgienv['REMOTE_ADDR'],
        )

        # todo:登录逻辑,后期需要封装
        request.session.db = request.cr.dbname
        request.session.uid = uid
        request.session.login = values['login']
        request.uid = uid
        request.disable_db = False
        request.session.get_context()

        # todo:封装 end

        # todo:返回json
        return str(uid)

        pass

    @http.route('/remote_account/remote_account/remove', auth='public')
    def remove(self, **kw):
        """
        ...todo::
            删除还是设置status,具体要观察下,status会比较保守,但是对应try_login就要做相应地调整

        :param kw:
        :return:
        """

        qcontext = request.params.copy()

        # todo:加签名防止他人恶意使用
        sign = qcontext.get('sign')

        # 获取model
        request.registry['res.users'].drop(request.cr, openerp.SUPERUSER_ID, qcontext, None)



        return "Hello, world"

