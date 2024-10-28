import MySQLdb
from flask import Blueprint, request, flash, redirect, url_for, render_template, current_app,session

# Define Blueprint for recipes management
tools_bp = Blueprint('toolscontroller', __name__)


@tools_bp.route('/tools')
def tools():
    return render_template('tools.html')


@tools_bp.route('/benchpresscalculator')
def benchpresscalculator():
    return render_template('benchpresscalculator.html')


@tools_bp.route('/bmrcalculator')
def bmrcalculator():
    return render_template('bmrcalculator.html')