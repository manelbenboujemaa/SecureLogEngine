"""Secure Log Engine : moteur d'analyse de logs de sécurité en flux.

Le package est organisé en sous-packages correspondant aux modules du cahier
des charges :

- ``ingestion``  : lecture paresseuse des sources (Module 1) ;
- ``parsing``    : structuration et routage ``match-case`` (Modules 1-2) ;
- ``pipeline``   : transformations fonctionnelles (Module 2) ;
- ``analysis``   : agrégation et détection de force brute (Module 3) ;
- ``security``   : moteur de règles modulaire (Module 4) ;
- ``audit``      : introspection de l'environnement d'exécution (Module 4) ;
- ``reporting``  : production des rapports.
"""

__all__ = ["__app_name__", "__version__"]

__app_name__: str = "secure-log-engine"
__version__: str = "0.1.0"
