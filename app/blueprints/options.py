import functools, os
from flask import (flash, g, redirect, render_template, request, session, url_for)
from ..interface.options_interface import OptionsData, OptionsTimeSeries
from .blueprint import BP

bp = BP('options', __name__,'/options')

@bp.route('/', methods=('GET', 'POST'))
def options():
    data = OptionsData(request.form['symbol']).data if request.method == 'POST' else []
    #fig = OptionsTimeSeries(request.form['symbol'], 'dynamic', lines = [request.form['dimension'].lower()]).fig if request.method == 'POST' else None
    fig = OptionsTimeSeries(request.form['symbol'], 'dynamic', lines = ['implied_volatility']).fig if request.method == 'POST' else None
    params = {'symbol': request.form['symbol']} if request.method == 'POST' else None
    if request.method != 'POST' or not data:
       active_options, implied_volatility, max_pain, spread, price = [], None, None, None, None
    else:
        active_options, implied_volatility, max_pain, spread, price = data['active_options'], data['average_implied_volatility'], data['max_pain'], data['options_spread'], data['price']
    return render_template('/options.html', params=params, active_options=active_options, implied_volatility=implied_volatility, max_pain=max_pain, spread=spread, fig=fig, price=price)


## TO DO
# add an input on the form to pick which dimension to see on the y axis for the time series chart
    # this will be sent in the lines kwarg to the TimeSeries class