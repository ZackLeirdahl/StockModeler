import functools, os
from flask import (flash, g, redirect, render_template, request, session, url_for)
from .blueprint import BP

bp = BP('auth', __name__, '/')

@bp.route('/')
def auth():
    return render_template('/auth.html')