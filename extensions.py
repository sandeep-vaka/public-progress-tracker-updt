"""
extensions.py
─────────────
Central place for Flask extension instances that must be created
*before* the app factory runs (so other modules can import them
without pulling in the whole app and causing circular imports).

Usage
-----
    # in app.py
    from extensions import mail
    mail.init_app(app)

    # anywhere else
    from extensions import mail
    mail.send(msg)
"""

from flask_mail import Mail

# Flask-Mail instance — wired to the app inside create_app() via init_app()
mail = Mail()
