#!/usr/bin/env python3
"""
option_selector.py

Maps form data to one of 18 Term Sheet options (9 binding + 9 non-binding)
Drop this into your scripts/ folder and use in your workflow

Usage:
    from option_selector import determine_term_sheet_option, describe_option
    
    form_data = {
        'bindingStatus': 'binding',
        'dueDiligenceStructure': 'structured',
        'depositAmount': 0,
        'escrowRequired': True,
        'exclusivityRequired': True,
        'jurisdiction': 'exclusive'
    }
    
    result = determine_term_sheet_option(form_data)
    print(result['template_variant'])  # Output: BINDING_Option_1
"""

import json
from typing import Dict, List, Any


class TermSheetOptionSelector:
    """Maps form data characteristics to Term Sheet options"""
    
    # Define the characteristics of each option for reference
    OPTIONS_REFERENCE = {
        'BINDING': {
            1: {'dd': 'structured', 'deposit': False, 'escrow': True, 'exclusivity': True, 'jurisdiction': 'exclusive'},
            2: {'dd': 'unstructured', 'deposit': False, 'escrow': True, 'exclusivity': True, 'jurisdiction': 'exclusive'},
            3: {'dd': 'structured', 'deposit': True, 'escrow': True, 'exclusivity': True, 'jurisdiction': 'exclusive'},
            4: {'dd': 'unstructured', 'deposit': True, 'escrow': True, 'exclusivity': True, 'jurisdiction': 'exclusive'},
            5: {'dd': 'unstructured', 'deposit': False, 'escrow': False, 'exclusivity': True, 'jurisdiction': 'exclusive'},
            6: {'dd': 'unstructured', 'deposit': True, 'escrow': False, 'exclusivity': True, 'jurisdiction': 'exclusive'},
            7: {'dd': 'unstructured', 'deposit': True, 'escrow': True, 'exclusivity': False, 'jurisdiction': 'exclusive'},
            8: {'dd': 'unstructured', 'deposit': True, 'escrow': True, 'exclusivity': True, 'jurisdiction': 'non-exclusive'},
            9: {'dd': 'unstructured', 'deposit': True, 'escrow': True, 'exclusivity': True, 'jurisdiction': 'exclusive'},  # STANDARD
        },
        'NON_BINDING': {
            1: {'dd': 'structured', 'deposit': False, 'escrow': True, 'exclusivity': True, 'jurisdiction': 'exclusive'},
            2: {'dd': 'unstructured', 'deposit': False, 'escrow': True, 'exclusivity': True, 'jurisdiction': 'exclusive'},
            3: {'dd': 'structured', 'deposit': True, 'escrow': True, 'exclusivity': True, 'jurisdiction': 'exclusive'},
            4: {'dd': 'unstructured', 'deposit': True, 'escrow': True, 'exclusivity': True, 'jurisdiction': 'exclusive'},
            5: {'dd': 'unstructured', 'deposit': False, 'escrow': False, 'exclusivity': True, 'jurisdiction': 'exclusive'},
            6: {'dd': 'unstructured', 'deposit': True, 'escrow': False, 'exclusivity': True, 'jurisdiction': 'exclusive'},
            7: {'dd': 'unstructured', 'deposit': True, 'escrow': True, 'exclusivity': False, 'jurisdiction': 'exclusive'},
            8: {'dd': 'unstructured', 'deposit': True, 'escrow': True, 'exclusivity': True, 'jurisdiction': 'non-exclusive'},
            9: {'dd': 'unstructured', 'deposit': True, 'escrow': True, 'exclusivity': True, 'jurisdiction': 'exclusive'},  # STANDARD
        }
    }
    
    DESCRIPTIONS = {
        'BINDING': {
            1: "Structured DD, No Deposit, Escrow, Exclusivity, Exclusive JD",
            2: "Unstructured DD, No Deposit, Escrow, Exclusivity, Exclusive JD",
            3: "Structured DD, Deposit, Escrow, Exclusivity, Exclusive JD",
            4: "Unstructured DD, Deposit, Escrow, Exclusivity, Exclusive JD",
            5: "Unstructured DD, No Deposit, No Escrow, Exclusivity, Exclusive JD",
            6: "Unstructured DD, Deposit, No Escrow, Exclusivity, Exclusive JD",
            7: "Unstructured DD, Deposit, Escrow, No Exclusivity, Exclusive JD",
            8: "Unstructured DD, Deposit, Escrow, Exclusivity, Non-Exclusive JD",
            9: "STANDARD - Unstructured DD, Deposit, Escrow, Exclusivity, Exclusive JD",
        },
        'NON_BINDING': {
            1: "Structured DD, No Deposit, Escrow, Exclusivity, Exclusive JD",
            2: "Unstructured DD, No Deposit, Escrow, Exclusivity, Exclusive JD",
            3: "Structured DD, Deposit, Escrow, Exclusivity, Exclusive JD",
            4: "Unstructured DD, Deposit, Escrow, Exclusivity, Exclusive JD",
            5: "Unstructured DD, No Deposit, No Escrow, Exclusivity, Exclusive JD",
            6: "Unstructured DD, Deposit, No Escrow, Exclusivity, Exclusive JD",
            7: "Unstructured DD, Deposit, Escrow, No Exclusivity, Exclusive JD",
            8: "Unstructured DD, Deposit, Escrow, Exclusivity, Non-Exclusive JD",
            9: "STANDARD - Unstructured DD, Deposit, Escrow, Exclusivity, Exclusive JD",
        }
    }
    
    @staticmethod
    def determine_option(form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps form data to one of 18 options
        
        Args:
            form_data: Dictionary containing:
                - bindingStatus: 'binding' or 'non-binding'
                - dueDiligenceStructure: 'structured' or 'unstructured'
                - depositAmount: float (0 = no deposit)
                - escrowRequired: boolean
                - exclusivityRequired: boolean
                - jurisdiction: 'exclusive' or 'non-exclusive'
        
        Returns:
            {
                'binding_status': 'binding|non-binding',
                'option_number': 1-9,
                'template_variant': 'BINDING_Option_1' | 'NON_BINDING_Option_1' etc,
                'description': 'Human readable description',
                'characteristics': {...}
            }
        """
        
        # Extract and normalize inputs
        binding_status = str(form_data.get('bindingStatus', 'binding')).lower().strip()
        if 'non-binding' in binding_status or binding_status == 'false':
            binding_status = 'non-binding'
        else:
            binding_status = 'binding'
        
        dd_structure = str(form_data.get('dueDiligenceStructure', 'unstructured')).lower().strip()
        if 'struct' in dd_structure:
            dd_structure = 'structured'
        else:
            dd_structure = 'unstructured'
        
        # Deposit: check if amount > 0
        deposit_amount = form_data.get('depositAmount', 0)
        try:
            deposit_amount = float(deposit_amount) if deposit_amount else 0
        except (ValueError, TypeError):
            deposit_amount = 0
        has_deposit = deposit_amount > 0
        
        # Escrow: boolean or string
        has_escrow = form_data.get('escrowRequired', False)
        if isinstance(has_escrow, str):
            has_escrow = has_escrow.lower() in ['true', 'yes', 'on', '1']
        
        # Exclusivity: boolean or string
        has_exclusivity = form_data.get('exclusivityRequired', True)
        if isinstance(has_exclusivity, str):
            has_exclusivity = has_exclusivity.lower() in ['true', 'yes', 'on', '1']
        
        # Jurisdiction
        jurisdiction = str(form_data.get('jurisdiction', 'exclusive')).lower().strip()
        if 'non-exclusive' in jurisdiction or 'non' in jurisdiction:
            jurisdiction = 'non-exclusive'
        else:
            jurisdiction = 'exclusive'
        
        # Determine option number
        option_number = TermSheetOptionSelector._map_to_option(
            dd_structure, has_deposit, has_escrow, has_exclusivity, jurisdiction
        )
        
        # Build response
        template_prefix = 'BINDING' if binding_status == 'binding' else 'NON_BINDING'
        template_variant = f"{template_prefix}_Option_{option_number}"
        
        return {
            'binding_status': binding_status,
            'option_number': option_number,
            'template_variant': template_variant,
            'description': TermSheetOptionSelector.describe_option(option_number, binding_status),
            'characteristics': {
                'dd_structure': dd_structure,
                'has_deposit': has_deposit,
                'deposit_amount': deposit_amount,
                'has_escrow': has_escrow,
                'has_exclusivity': has_exclusivity,
                'jurisdiction': jurisdiction
            }
        }
    
    @staticmethod
    def _map_to_option(dd_structure: str, deposit: bool, escrow: bool, 
                       exclusivity: bool, jurisdiction: str) -> int:
        """
        Maps characteristics to option number 1-9 using sequential filtering
        
        Filter Priority:
        1. Due Diligence Structure (Structured vs Unstructured)
        2. Deposit (Yes/No)
        3. Escrow Agent (Yes/No)
        4. Exclusivity Clause (Yes/No)
        5. Jurisdiction (Exclusive/Non-Exclusive)
        """
        
        # Start with all 9 options
        candidates = set(range(1, 10))
        
        # FILTER 1: Due Diligence Structure
        if dd_structure == 'structured':
            candidates &= {1, 3}  # Structured only in Options 1 and 3
        else:
            candidates &= {2, 4, 5, 6, 7, 8, 9}  # Unstructured in these options
        
        # FILTER 2: Deposit
        if not deposit:
            candidates &= {1, 2, 5}  # No deposit in these options
        else:
            candidates &= {3, 4, 6, 7, 8, 9}  # Deposit in these options
        
        # FILTER 3: Escrow Agent
        if not escrow:
            candidates &= {5, 6}  # No escrow in these options
        else:
            candidates &= {1, 2, 3, 4, 7, 8, 9}  # Escrow in these options
        
        # FILTER 4: Exclusivity
        if not exclusivity:
            candidates &= {7}  # No exclusivity in Option 7 only
        else:
            candidates &= {1, 2, 3, 4, 5, 6, 8, 9}  # Exclusivity in these options
        
        # FILTER 5: Jurisdiction
        if jurisdiction == 'non-exclusive':
            candidates &= {8}  # Non-exclusive in Option 8 only
        else:
            candidates &= {1, 2, 3, 4, 5, 6, 7, 9}  # Exclusive in these options
        
        # Return first matching option, or default to 9 (standard)
        if candidates:
            return sorted(list(candidates))[0]
        else:
            # Fallback: return 9 (most comprehensive option)
            print("⚠️  Warning: No matching option found, defaulting to Option 9 (Standard)")
            return 9
    
    @staticmethod
    def describe_option(option_number: int, binding_status: str) -> str:
        """Returns human-readable description of the selected option"""
        prefix = 'BINDING' if 'binding' in binding_status.lower() else 'NON_BINDING'
        return TermSheetOptionSelector.DESCRIPTIONS.get(prefix, {}).get(option_number, "Unknown Option")
    
    @staticmethod
    def validate_form_data(form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates form data and returns validation result
        
        Returns:
            {
                'is_valid': boolean,
                'errors': [list of error messages],
                'warnings': [list of warning messages]
            }
        """
        errors = []
        warnings = []
        
        # Check required fields
        if not form_data.get('bindingStatus'):
            errors.append("bindingStatus is required")
        
        if not form_data.get('dueDiligenceStructure'):
            errors.append("dueDiligenceStructure is required")
        
        # Validate binding status value
        binding = str(form_data.get('bindingStatus', '')).lower()
        if binding and binding not in ['binding', 'non-binding', 'true', 'false']:
            warnings.append(f"Unusual bindingStatus value: {binding}")
        
        # Validate DD structure value
        dd = str(form_data.get('dueDiligenceStructure', '')).lower()
        if dd and 'struct' not in dd and dd not in ['structured', 'unstructured']:
            warnings.append(f"Unusual dueDiligenceStructure value: {dd}")
        
        # Validate deposit amount
        try:
            deposit = form_data.get('depositAmount', 0)
            if deposit:
                float(deposit)
        except (ValueError, TypeError):
            errors.append(f"Invalid depositAmount: {deposit}")
        
        # Validate jurisdiction
        jurisdiction = str(form_data.get('jurisdiction', '')).lower()
        if jurisdiction and jurisdiction not in ['exclusive', 'non-exclusive']:
            warnings.append(f"Unusual jurisdiction value: {jurisdiction}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


# Convenience functions for easy import
def determine_term_sheet_option(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function - maps form data to Term Sheet option"""
    return TermSheetOptionSelector.determine_option(form_data)


def describe_option(option_number: int, binding_status: str) -> str:
    """Wrapper function - returns description of option"""
    return TermSheetOptionSelector.describe_option(option_number, binding_status)


def validate_form_data(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function - validates form data"""
    return TermSheetOptionSelector.validate_form_data(form_data)


# Main execution - for testing
if __name__ == '__main__':
    
    print("=" * 80)
    print("TERM SHEET OPTION SELECTOR - TEST CASES")
    print("=" * 80)
    
    # Test cases
    test_cases = [
        {
            'name': 'Option 9 - Standard Binding Deal',
            'data': {
                'bindingStatus': 'binding',
                'dueDiligenceStructure': 'unstructured',
                'depositAmount': 500000,
                'escrowRequired': True,
                'exclusivityRequired': True,
                'jurisdiction': 'exclusive'
            },
            'expected': 'BINDING_Option_9'
        },
        {
            'name': 'Option 1 - Structured, No Deposit',
            'data': {
                'bindingStatus': 'binding',
                'dueDiligenceStructure': 'structured',
                'depositAmount': 0,
                'escrowRequired': True,
                'exclusivityRequired': True,
                'jurisdiction': 'exclusive'
            },
            'expected': 'BINDING_Option_1'
        },
        {
            'name': 'Option 5 - No Escrow, No Deposit',
            'data': {
                'bindingStatus': 'binding',
                'dueDiligenceStructure': 'unstructured',
                'depositAmount': 0,
                'escrowRequired': False,
                'exclusivityRequired': True,
                'jurisdiction': 'exclusive'
            },
            'expected': 'BINDING_Option_5'
        },
        {
            'name': 'Option 8 - Non-Exclusive Jurisdiction',
            'data': {
                'bindingStatus': 'binding',
                'dueDiligenceStructure': 'unstructured',
                'depositAmount': 500000,
                'escrowRequired': True,
                'exclusivityRequired': True,
                'jurisdiction': 'non-exclusive'
            },
            'expected': 'BINDING_Option_8'
        },
        {
            'name': 'Option 7 - No Exclusivity',
            'data': {
                'bindingStatus': 'binding',
                'dueDiligenceStructure': 'unstructured',
                'depositAmount': 500000,
                'escrowRequired': True,
                'exclusivityRequired': False,
                'jurisdiction': 'exclusive'
            },
            'expected': 'BINDING_Option_7'
        },
        {
            'name': 'NON_BINDING_Option_4 - Non-Binding Standard',
            'data': {
                'bindingStatus': 'non-binding',
                'dueDiligenceStructure': 'unstructured',
                'depositAmount': 500000,
                'escrowRequired': True,
                'exclusivityRequired': True,
                'jurisdiction': 'exclusive'
            },
            'expected': 'NON_BINDING_Option_4'
        },
    ]
    
    # Run test cases
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 80)
        
        # Validate
        validation = validate_form_data(test_case['data'])
        if validation['errors']:
            print(f"❌ VALIDATION ERRORS: {validation['errors']}")
            failed += 1
            continue
        
        if validation['warnings']:
            print(f"⚠️  Warnings: {validation['warnings']}")
        
        # Determine option
        result = determine_term_sheet_option(test_case['data'])
        
        # Check result
        actual = result['template_variant']
        expected = test_case['expected']
        
        if actual == expected:
            print(f"✅ PASS")
            print(f"   Expected: {expected}")
            print(f"   Got:      {actual}")
            print(f"   Description: {result['description']}")
            passed += 1
        else:
            print(f"❌ FAIL")
            print(f"   Expected: {expected}")
            print(f"   Got:      {actual}")
            print(f"   Description: {result['description']}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    
    if failed == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ {failed} test(s) failed")
