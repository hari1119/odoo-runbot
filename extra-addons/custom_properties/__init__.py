# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

from . import controllers
from . import models
from . import decorators
from . import restful



def _test_pre_init_hook(cr):
    print("Pre init hook has been excuted sucessfully......")
    env = api.Environment(cr, SUPERUSER_ID, {})
    print("Users:",env['res.users'].search([('id','>',0)]))


def _test_post_init_hook(cr):
    print("Post init hook has been excuted sucessfully......")

def _test_uninstall_hook(cr):
    print("Uninstall hook has been excuted sucessfully......")

def _test_post_load():
    print("Post load hook has been excuted sucessfully......")
