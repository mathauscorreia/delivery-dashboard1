"""
Módulo de normalização de endereços para agrupamento inteligente de entregas.
Responsável por padronizar endereços e remover variações que impedem agrupamento correto.
"""

import re
from typing import Dict


class AddressNormalizer:
    """Classe responsável pela normalização de endereços."""
    
    # Mapeamento de abreviações comuns de logradouros
    STREET_TYPES = {
        'rua': 'r',
        'r.': 'r',
        'r': 'r',
        'avenida': 'av',
        'av.': 'av',
        'av': 'av',
        'travessa': 'tv',
        'tv.': 'tv',
        'tv': 'tv',
        'alameda': 'al',
        'al.': 'al',
        'al': 'al',
        'praça': 'pç',
        'pç.': 'pç',
        'pç': 'pç',
        'estrada': 'est',
        'est.': 'est',
        'est': 'est',
        'rodovia': 'rod',
        'rod.': 'rod',
        'rod': 'rod',
        'largo': 'lg',
        'lg.': 'lg',
        'lg': 'lg',
    }
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normaliza texto básico: minúsculas, remove espaços duplicados.
        
        Args:
            text: Texto a ser normalizado
            
        Returns:
            Texto normalizado
        """
        if not text or not isinstance(text, str):
            return ''
        
        # Converte para minúsculas
        text = text.lower().strip()
        
        # Remove espaços duplicados
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    @staticmethod
    def normalize_street_type(address: str) -> str:
        """
        Normaliza o tipo de logradouro (Rua, Avenida, etc).
        
        Args:
            address: Endereço completo
            
        Returns:
            Endereço com tipo de logradouro normalizado
        """
        if not address:
            return ''
        
        address = AddressNormalizer.normalize_text(address)
        
        # Procura por tipo de logradouro no início do endereço
        for full_type, abbrev in AddressNormalizer.STREET_TYPES.items():
            # Padrão: tipo de logradouro seguido de espaço ou ponto
            pattern = r'^' + re.escape(full_type) + r'[\s\.]+'
            if re.match(pattern, address):
                address = re.sub(pattern, abbrev + ' ', address)
                break
        
        return address
    
    @staticmethod
    def normalize_number(number: str) -> str:
        """
        Normaliza número do endereço.
        
        Args:
            number: Número do endereço
            
        Returns:
            Número normalizado
        """
        if not number or not isinstance(number, str):
            return 's/n'
        
        number = str(number).strip().lower()
        
        # Trata casos de "sem número"
        if number in ['', 'sn', 's/n', 'sem numero', 'sem número', 'nan', 'none']:
            return 's/n'
        
        # Remove caracteres não numéricos (exceto hífen)
        number = re.sub(r'[^\d\-]', '', number)
        
        return number if number else 's/n'
    
    @staticmethod
    def normalize_complement(complement: str) -> str:
        """
        Normaliza complemento do endereço.
        
        Args:
            complement: Complemento do endereço
            
        Returns:
            Complemento normalizado
        """
        if not complement or not isinstance(complement, str):
            return ''
        
        complement = AddressNormalizer.normalize_text(complement)
        
        # Padroniza abreviações comuns
        replacements = {
            'apartamento': 'ap',
            'apto': 'ap',
            'apt': 'ap',
            'ap.': 'ap',
            'bloco': 'bl',
            'bl.': 'bl',
            'casa': 'cs',
            'cs.': 'cs',
            'conjunto': 'cj',
            'cj.': 'cj',
            'lote': 'lt',
            'lt.': 'lt',
            'quadra': 'qd',
            'qd.': 'qd',
        }
        
        for full, abbrev in replacements.items():
            complement = re.sub(r'\b' + full + r'\b', abbrev, complement)
        
        return complement
    
    @staticmethod
    def normalize_neighborhood(neighborhood: str) -> str:
        """
        Normaliza bairro.
        
        Args:
            neighborhood: Nome do bairro
            
        Returns:
            Bairro normalizado
        """
        return AddressNormalizer.normalize_text(neighborhood)
    
    @staticmethod
    def normalize_address(address_data: Dict[str, str]) -> Dict[str, str]:
        """
        Normaliza todos os campos de um endereço.
        
        Args:
            address_data: Dicionário com campos do endereço
            
        Returns:
            Dicionário com campos normalizados
        """
        return {
            'endereco': AddressNormalizer.normalize_street_type(
                address_data.get('endereco', '')
            ),
            'numero': AddressNormalizer.normalize_number(
                address_data.get('numero', '')
            ),
            'complemento': AddressNormalizer.normalize_complement(
                address_data.get('complemento', '')
            ),
            'bairro': AddressNormalizer.normalize_neighborhood(
                address_data.get('bairro', '')
            ),
        }
    
    @staticmethod
    def create_address_key(normalized_address: Dict[str, str]) -> str:
        """
        Cria uma chave única para agrupamento de endereços.
        
        Args:
            normalized_address: Endereço normalizado
            
        Returns:
            Chave única para agrupamento
        """
        # Combina endereço + número + bairro (complemento não conta para agrupamento)
        key_parts = [
            normalized_address.get('endereco', ''),
            normalized_address.get('numero', ''),
            normalized_address.get('bairro', ''),
        ]
        
        # Remove partes vazias e junta com separador
        key = '|'.join([part for part in key_parts if part])
        
        return key
