import functools, os
from flask import (flash, g, redirect, render_template, request, session, url_for)
from .blueprint import BP
from ..interface.task_interface import get_option_symbols, TaskInterface

bp = BP('tasks', __name__,'/tasks')

@bp.route('/', methods=('GET', 'POST'))
def tasks():
    syms = get_option_symbols()
    if request.method == 'POST':
        TaskInterface(request.form.getlist('symbols'),request.form.getlist('tasks'), request.form['interval'])
    return render_template('/tasks.html',syms=syms)

"""
- select tasks
- populate symbols
- select symbols
- run tasks
"""
