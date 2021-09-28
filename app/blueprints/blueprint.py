from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)

class BP(Blueprint):
    def __init__(self, name, import_name, url_prefix):
        Blueprint.__init__(self, name, import_name, url_prefix=url_prefix)