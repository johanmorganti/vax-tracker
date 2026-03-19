from flask import Flask
from .lib.data import load_antigens, load_products, list_countries


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # Load shared data once at startup and inject into template context
    antigens = load_antigens()
    products = load_products()
    countries = list_countries()

    @app.context_processor
    def inject_globals():
        return {
            "antigens": antigens,
            "products": products,
            "countries": countries,
        }

    from .routes import bp
    app.register_blueprint(bp)

    return app
