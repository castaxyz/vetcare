import os
from web.app import create_app
from infra import get_container

# Crear aplicación Flask a nivel global (para Gunicorn)
config_name = os.environ.get('FLASK_CONFIG', 'development')
app = create_app(config_name)   # <--- aquí queda expuesto para Gunicorn

def main():
    """
    Función principal que inicializa y ejecuta la aplicación.
    """
    print("🚀 Iniciando VetCare...")
    print("=" * 50)
    print(f"📝 Configuración: {config_name}")

    # Configuraciones adicionales solo en desarrollo
    if config_name == 'development':
        from domain.entities.user import UserRole
        from vetcare.web.app import app  # tu import anterior
        from your_module import create_default_users, create_sample_data  # ajusta al módulo correcto

        print("🛠️  Modo desarrollo activado")
        with app.app_context():
            create_default_users()
            create_sample_data()

    # Ejecutar aplicación
    app.run(
        host='0.0.0.0' if config_name == 'production' else '127.0.0.1',
        port=int(os.environ.get('PORT', 5000)),
        debug=(config_name == 'development')
    )

if __name__ == '__main__':
    main()
