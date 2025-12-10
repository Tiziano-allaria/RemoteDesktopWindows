"""
Módulo para verificar si la PC está unida a un dominio de Active Directory.
Autor: Tu Nombre
Fecha: 2024-12-04
"""

import win32api
import win32net
import win32netcon
import logging
from typing import Dict, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DomainChecker:
    """
    Clase para verificar el estado de pertenencia a un dominio de Windows.
    """
    
    def __init__(self):
        """Inicializa el verificador de dominio."""
        self.domain_info = None
    
    def is_domain_joined(self) -> bool:
        """
        Verifica si la computadora está unida a un dominio.
        
        Returns:
            bool: True si está en un dominio, False si está en workgroup
            
        Raises:
            Exception: Si hay un error al consultar la información del sistema
        """
        try:
            # Obtener información del dominio/workgroup
            info = win32net.NetWkstaGetInfo(None, 102)
            
            # lanman_root contiene el tipo de red:
            # - Si está en dominio, tendrá el nombre del dominio
            # - Si está en workgroup, tendrá el nombre del workgroup
            
            # wki102_langroup contiene el nombre del dominio o workgroup
            workgroup_or_domain = info['langroup']
            
            # Verificar el tipo de instalación
            # Si el valor de 'wki102_ver_major' indica que está en dominio
            join_status = self._get_join_status()
            
            self.domain_info = {
                'name': workgroup_or_domain,
                'is_domain': join_status == 'Domain',
                'join_type': join_status
            }
            
            logger.info(f"Estado de la red: {join_status} - Nombre: {workgroup_or_domain}")
            
            return self.domain_info['is_domain']
            
        except Exception as e:
            logger.error(f"Error al verificar dominio: {str(e)}")
            return False
    
    def _get_join_status(self) -> str:
        """
        Obtiene el estado detallado de unión al dominio usando NetGetJoinInformation.
        
        Returns:
            str: 'Domain', 'Workgroup', o 'Unknown'
        """
        try:
            # NetGetJoinInformation devuelve el tipo de unión
            # 0 = NetSetupUnknownStatus
            # 1 = NetSetupUnjoined
            # 2 = NetSetupWorkgroupName
            # 3 = NetSetupDomainName
            
            join_status = win32net.NetGetJoinInformation(None)
            
            status_map = {
                0: 'Unknown',
                1: 'Unjoined',
                2: 'Workgroup',
                3: 'Domain'
            }
            
            return status_map.get(join_status[1], 'Unknown')
            
        except Exception as e:
            logger.warning(f"No se pudo obtener NetGetJoinInformation: {str(e)}")
            return 'Unknown'
    
    def get_domain_info(self) -> Optional[Dict[str, any]]:
        """
        Obtiene información completa del dominio/workgroup.
        
        Returns:
            Dict con información del dominio o None si no se ha ejecutado is_domain_joined()
        """
        if self.domain_info is None:
            logger.warning("Debe ejecutar is_domain_joined() primero")
            return None
        
        return self.domain_info
    
    def get_computer_name(self) -> str:
        """
        Obtiene el nombre de la computadora.
        
        Returns:
            str: Nombre de la computadora
        """
        try:
            return win32api.GetComputerName()
        except Exception as e:
            logger.error(f"Error al obtener nombre de computadora: {str(e)}")
            return "UNKNOWN"
    
    def get_full_computer_name(self) -> str:
        """
        Obtiene el nombre completo de la computadora (FQDN si está en dominio).
        
        Returns:
            str: Nombre completo (ej: MIPC.midominio.com)
        """
        try:
            return win32api.GetComputerNameEx(win32netcon.ComputerNameDnsFullyQualified)
        except Exception as e:
            logger.error(f"Error al obtener FQDN: {str(e)}")
            return self.get_computer_name()


# Función de utilidad para uso rápido
def check_domain_status() -> Dict[str, any]:
    """
    Función helper para verificar rápidamente el estado del dominio.
    
    Returns:
        Dict con toda la información del dominio
    """
    checker = DomainChecker()
    is_domain = checker.is_domain_joined()
    
    return {
        'is_domain_joined': is_domain,
        'computer_name': checker.get_computer_name(),
        'full_name': checker.get_full_computer_name(),
        'domain_info': checker.get_domain_info()
    }


# Script de prueba (solo se ejecuta si se corre directamente este archivo)
if __name__ == "__main__":
    print("=" * 60)
    print("VERIFICADOR DE DOMINIO - Prueba")
    print("=" * 60)
    
    checker = DomainChecker()
        
    # Obtener nombre de la PC
    computer_name = checker.get_computer_name()
    print(f"\n📌 Nombre de la PC: {computer_name}")
        
    # Obtener nombre completo
    full_name = checker.get_full_computer_name()
    print(f"📌 Nombre completo: {full_name}")
        
    # Verificar si está en dominio
    print("\n🔍 Verificando conexión a dominio...")
    is_domain = checker.is_domain_joined()
        
    # Mostrar resultados
    domain_info = checker.get_domain_info()
        
    print("\n" + "=" * 60)
    print("RESULTADOS:")
    print("=" * 60)
        
    if is_domain:
        print("✅ Esta PC ESTÁ unida a un dominio")
        print(f"   Dominio: {domain_info['name']}")
    else:
        print("❌ Esta PC NO está en un dominio")
        print(f"   Workgroup: {domain_info['name']}")
            
    print(f"\nTipo de conexión: {domain_info['join_type']}")
    print("=" * 60)
       
    