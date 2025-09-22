"""
EXPLICACIÓN: Container de Dependency Injection que configura todas las dependencias.
Implementa el patrón Service Locator para gestionar las dependencias de la aplicación.
Este es el "cerebro" que conecta interfaces con implementaciones.
"""

from typing import Dict, Any, Optional

# Repositories - Interfaces
from interfaces.repositories.user_repository import UserRepository
from interfaces.repositories.client_repository import ClientRepository
from interfaces.repositories.pet_repository import PetRepository
from interfaces.repositories.appointment_repository import AppointmentRepository

# Repositories - Implementaciones
from infra.database.repositories.user_repository import SQLUserRepository
from infra.database.repositories.client_repository import SQLClientRepository
from infra.database.repositories.pet_repository import SQLPetRepository
from infra.database.repositories.appointment_repository import SQLAppointmentRepository

# Services
from services.auth_service import AuthService
from services.client_service import ClientService
from services.pet_service import PetService
from services.appointment_service import AppointmentService

class DIContainer:
    """
    Contenedor de Dependency Injection.
    
    Maneja la creación y configuración de todas las dependencias de la aplicación.
    Implementa el patrón Singleton para asegurar una sola instancia de cada servicio.
    """
    
    def __init__(self):
        self._repositories: Dict[str, Any] = {}
        self._services: Dict[str, Any] = {}
        self._initialized = False
    
    def initialize(self):
        """
        Inicializa todas las dependencias.
        Debe ser llamado después de inicializar la base de datos.
        """
        if self._initialized:
            return
        
        self._setup_repositories()
        self._setup_services()
        self._initialized = True
    
    def _setup_repositories(self):
        """Configura todas las implementaciones de repositories"""
        # Crear instancias de repositories
        self._repositories['user'] = SQLUserRepository()
        self._repositories['client'] = SQLClientRepository()
        self._repositories['pet'] = SQLPetRepository()
        self._repositories['appointment'] = SQLAppointmentRepository()
    
    def _setup_services(self):
        """
        Configura todos los services inyectando sus dependencias.
        Aquí es donde se "conectan" los services con los repositories.
        """
        # AuthService solo necesita UserRepository
        self._services['auth'] = AuthService(
            user_repository=self._repositories['user']
        )
        
        # ClientService solo necesita ClientRepository
        self._services['client'] = ClientService(
            client_repository=self._repositories['client']
        )
        
        # PetService necesita PetRepository y ClientRepository
        self._services['pet'] = PetService(
            pet_repository=self._repositories['pet'],
            client_repository=self._repositories['client']
        )
        
        # AppointmentService necesita múltiples repositories
        self._services['appointment'] = AppointmentService(
            appointment_repository=self._repositories['appointment'],
            pet_repository=self._repositories['pet'],
            user_repository=self._repositories['user']
        )
    
    def get_repository(self, name: str) -> Any:
        """
        Obtiene un repository por nombre.
        
        Args:
            name: Nombre del repository ('user', 'client', 'pet', 'appointment')
            
        Returns:
            Instancia del repository solicitado
            
        Raises:
            KeyError: Si el repository no existe
            RuntimeError: Si el container no está inicializado
        """
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        
        if name not in self._repositories:
            available_repos = list(self._repositories.keys())
            raise KeyError(f"Repository '{name}' not found. Available: {available_repos}")
        
        return self._repositories[name]
    
    def get_service(self, name: str) -> Any:
        """
        Obtiene un service por nombre.
        
        Args:
            name: Nombre del service ('auth', 'client', 'pet', 'appointment')
            
        Returns:
            Instancia del service solicitado
            
        Raises:
            KeyError: Si el service no existe
            RuntimeError: Si el container no está inicializado
        """
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        
        if name not in self._services:
            available_services = list(self._services.keys())
            raise KeyError(f"Service '{name}' not found. Available: {available_services}")
        
        return self._services[name]
    
    def get_user_repository(self) -> UserRepository:
        """Helper method para obtener UserRepository con tipo correcto"""
        return self.get_repository('user')
    
    def get_client_repository(self) -> ClientRepository:
        """Helper method para obtener ClientRepository con tipo correcto"""
        return self.get_repository('client')
    
    def get_pet_repository(self) -> PetRepository:
        """Helper method para obtener PetRepository con tipo correcto"""
        return self.get_repository('pet')
    
    def get_appointment_repository(self) -> AppointmentRepository:
        """Helper method para obtener AppointmentRepository con tipo correcto"""
        return self.get_repository('appointment')
    
    def get_auth_service(self) -> AuthService:
        """Helper method para obtener AuthService con tipo correcto"""
        return self.get_service('auth')
    
    def get_client_service(self) -> ClientService:
        """Helper method para obtener ClientService con tipo correcto"""
        return self.get_service('client')
    
    def get_pet_service(self) -> PetService:
        """Helper method para obtener PetService con tipo correcto"""
        return self.get_service('pet')
    
    def get_appointment_service(self) -> AppointmentService:
        """Helper method para obtener AppointmentService con tipo correcto"""
        return self.get_service('appointment')
    
    def health_check(self) -> Dict[str, bool]:
        """
        Verifica el estado de salud del container.
        Útil para debugging y monitoreo.
        """
        health = {
            'initialized': self._initialized,
            'repositories_count': len(self._repositories),
            'services_count': len(self._services),
        }
        
        if self._initialized:
            health.update({
                'available_repositories': list(self._repositories.keys()),
                'available_services': list(self._services.keys())
            })
        
        return health

# Instancia global del container
# Esta es la única instancia que se usará en toda la aplicación
container = DIContainer()

def get_container() -> DIContainer:
    """
    Función helper para obtener la instancia global del container.
    Uso recomendado en los controllers.
    """
    return container