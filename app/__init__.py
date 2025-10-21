# -*- coding: utf-8 -*-
"""
Inicializacion de la aplicacion Flask
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

def create_app(config_name='default'):
    """Factory de aplicacion Flask"""
    app = Flask(__name__)
    
    # Inicializar extensiones
    CORS(app)
    JWTManager(app)
    
    return app
