"""
Validation utilities for OpenXCom save file integrity and structure.
Provides basic validation checks to ensure save files remain functional.
"""
from typing import Any, Dict, List, Optional, Tuple


class SaveGameValidator:
    """Validates OpenXCom save game file structure and data integrity."""
    
    # Required top-level keys that should exist in the main game data document
    # Note: name, version, engine, time are typically in the header document
    REQUIRED_KEYS = [
        'funds', 'bases'
    ]
    
    # Expected data types for critical fields in main game data
    TYPE_VALIDATORS = {
        'funds': list,
        'bases': list,
        'monthsPassed': int,
        'daysPassed': int,
        'difficulty': int,
    }
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_save_structure(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate basic save file structure.
        Returns (is_valid, errors, warnings).
        """
        self.errors.clear()
        self.warnings.clear()
        
        # Check required keys
        self._check_required_keys(data)
        
        # Check data types
        self._check_data_types(data)
        
        # Validate funds structure
        self._validate_funds(data.get('funds', []))
        
        # Validate bases structure
        self._validate_bases(data.get('bases', []))
        
        # Check for reasonable value ranges
        self._check_reasonable_values(data)
        
        return len(self.errors) == 0, self.errors.copy(), self.warnings.copy()
    
    def _check_required_keys(self, data: Dict[str, Any]) -> None:
        """Check that all required keys are present."""
        for key in self.REQUIRED_KEYS:
            if key not in data:
                self.errors.append(f"Missing required key: {key}")
    
    def _check_data_types(self, data: Dict[str, Any]) -> None:
        """Validate data types for critical fields."""
        for key, expected_type in self.TYPE_VALIDATORS.items():
            if key in data and not isinstance(data[key], expected_type):
                self.errors.append(f"Invalid type for {key}: expected {expected_type.__name__}, got {type(data[key]).__name__}")
    
    def _validate_funds(self, funds: Any) -> None:
        """Validate funds structure and values."""
        if not isinstance(funds, list):
            self.errors.append("Funds must be a list")
            return
        
        if len(funds) < 2:
            self.errors.append("Funds list must contain at least 2 values")
            return
        
        for i, fund_value in enumerate(funds):
            if not isinstance(fund_value, int):
                self.errors.append(f"Fund value at index {i} must be an integer")
            elif fund_value < 0:
                self.warnings.append(f"Negative funds at index {i}: {fund_value}")
            elif fund_value > 999999999:  # Reasonable upper limit
                self.warnings.append(f"Very high funds at index {i}: {fund_value}")
    
    def _validate_bases(self, bases: Any) -> None:
        """Validate bases structure."""
        if not isinstance(bases, list):
            self.errors.append("Bases must be a list")
            return
        
        if not bases:
            self.errors.append("At least one base must exist")
            return
        
        for i, base in enumerate(bases):
            if not isinstance(base, dict):
                self.errors.append(f"Base {i} must be a dictionary")
                continue
                
            # Check required base fields
            required_base_keys = ['name', 'facilities']
            for key in required_base_keys:
                if key not in base:
                    self.errors.append(f"Base {i} missing required key: {key}")
            
            # Validate facilities
            if 'facilities' in base:
                self._validate_facilities(base['facilities'], i)
            
            # Validate soldiers if present
            if 'soldiers' in base:
                self._validate_soldiers(base['soldiers'], i)
    
    def _validate_facilities(self, facilities: Any, base_index: int) -> None:
        """Validate base facilities structure."""
        if not isinstance(facilities, list):
            self.errors.append(f"Base {base_index} facilities must be a list")
            return
        
        for j, facility in enumerate(facilities):
            if not isinstance(facility, dict):
                self.errors.append(f"Base {base_index} facility {j} must be a dictionary")
                continue
            
            if 'type' not in facility:
                self.errors.append(f"Base {base_index} facility {j} missing type")
            
            # Check for facilities under construction
            if 'buildTime' in facility:
                build_time = facility['buildTime']
                if not isinstance(build_time, int):
                    self.errors.append(f"Base {base_index} facility {j} buildTime must be an integer")
                elif build_time < 0:
                    self.warnings.append(f"Base {base_index} facility {j} has negative build time")
    
    def _validate_soldiers(self, soldiers: Any, base_index: int) -> None:
        """Validate soldiers structure."""
        if not isinstance(soldiers, list):
            self.errors.append(f"Base {base_index} soldiers must be a list")
            return
        
        for j, soldier in enumerate(soldiers):
            if not isinstance(soldier, dict):
                self.errors.append(f"Base {base_index} soldier {j} must be a dictionary")
                continue
            
            # Check required soldier fields
            required_soldier_keys = ['name', 'currentStats']
            for key in required_soldier_keys:
                if key not in soldier:
                    self.errors.append(f"Base {base_index} soldier {j} missing required key: {key}")
            
            # Validate stats
            if 'currentStats' in soldier:
                self._validate_soldier_stats(soldier['currentStats'], base_index, j)
    
    def _validate_soldier_stats(self, stats: Any, base_index: int, soldier_index: int) -> None:
        """Validate soldier statistics."""
        if not isinstance(stats, dict):
            self.errors.append(f"Base {base_index} soldier {soldier_index} currentStats must be a dictionary")
            return
        
        # Expected stat ranges (reasonable values)
        stat_ranges = {
            'tu': (0, 200),
            'stamina': (0, 200),
            'health': (0, 200),
            'bravery': (0, 200),
            'reactions': (0, 200),
            'firing': (0, 200),
            'throwing': (0, 200),
            'strength': (0, 200),
            'psiStrength': (0, 200),
            'psiSkill': (0, 200),
            'melee': (0, 200),
            'mana': (0, 200)
        }
        
        for stat_name, (min_val, max_val) in stat_ranges.items():
            if stat_name in stats:
                stat_value = stats[stat_name]
                if not isinstance(stat_value, int):
                    self.errors.append(f"Base {base_index} soldier {soldier_index} {stat_name} must be an integer")
                elif stat_value < min_val or stat_value > max_val:
                    self.warnings.append(f"Base {base_index} soldier {soldier_index} {stat_name} value {stat_value} outside reasonable range ({min_val}-{max_val})")
    
    def _check_reasonable_values(self, data: Dict[str, Any]) -> None:
        """Check for reasonable value ranges in various fields."""
        # Check time values
        if 'time' in data and isinstance(data['time'], dict):
            time_data = data['time']
            time_ranges = {
                'second': (0, 59),
                'minute': (0, 59),
                'hour': (0, 23),
                'day': (1, 31),
                'month': (1, 12),
                'year': (1990, 2100)
            }
            
            for time_field, (min_val, max_val) in time_ranges.items():
                if time_field in time_data:
                    value = time_data[time_field]
                    if not isinstance(value, int) or value < min_val or value > max_val:
                        self.warnings.append(f"Time field {time_field} value {value} outside reasonable range ({min_val}-{max_val})")
        
        # Check months and days passed
        if 'monthsPassed' in data:
            months = data['monthsPassed']
            if months < 0 or months > 1200:  # 100 years max
                self.warnings.append(f"Months passed {months} seems unreasonable")
        
        if 'daysPassed' in data:
            days = data['daysPassed']
            if days < 0 or days > 36500:  # 100 years max
                self.warnings.append(f"Days passed {days} seems unreasonable")


def quick_validate_save(data: Dict[str, Any]) -> bool:
    """Quick validation check - returns True if save seems valid."""
    validator = SaveGameValidator()
    is_valid, _, _ = validator.validate_save_structure(data)
    return is_valid


def detailed_validate_save(data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    """Detailed validation - returns (is_valid, errors, warnings)."""
    validator = SaveGameValidator()
    return validator.validate_save_structure(data)