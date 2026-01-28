import re
import math
import cmath
from typing import Union, Dict, Any
from decimal import Decimal, InvalidOperation


class AdvancedMathSolver:
    """Advanced mathematical expression solver with extended capabilities."""
    
    def __init__(self):
        # Safe mathematical functions available for evaluation
        self.safe_functions = {
            # Basic math functions
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            
            # Math module functions
            'sqrt': math.sqrt,
            'pow': pow,
            'exp': math.exp,
            'log': math.log,
            'log10': math.log10,
            'log2': math.log2,
            
            # Trigonometric functions
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'atan2': math.atan2,
            'sinh': math.sinh,
            'cosh': math.cosh,
            'tanh': math.tanh,
            'asinh': math.asinh,
            'acosh': math.acosh,
            'atanh': math.atanh,
            
            # Angular conversion
            'degrees': math.degrees,
            'radians': math.radians,
            
            # Other functions
            'factorial': math.factorial,
            'gcd': math.gcd,
            'lcm': math.lcm,
            'floor': math.floor,
            'ceil': math.ceil,
            'trunc': math.trunc,
            'copysign': math.copysign,
            'fmod': math.fmod,
            
            # Constants
            'pi': math.pi,
            'e': math.e,
            'tau': math.tau,
            'inf': math.inf,
            'nan': math.nan,
        }
    
    def preprocess_expression(self, expression: str) -> str:
        """Preprocess the expression to handle special notations."""
        cleaned = expression.strip()
        
        # Replace common mathematical notations
        replacements = {
            '^': '**',  # Power operator
            '×': '*',   # Multiplication
            '÷': '/',   # Division
            '√': 'sqrt',  # Square root
            'π': 'pi',  # Pi constant
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        # Handle implicit multiplication (e.g., "2(3+4)" -> "2*(3+4)")
        cleaned = re.sub(r'(\d)(\()', r'\1*\2', cleaned)
        cleaned = re.sub(r'(\))(\d)', r'\1*\2', cleaned)
        cleaned = re.sub(r'(\))(\()', r'\1*\2', cleaned)
        
        # Handle numbers before functions (e.g., "2sin(x)" -> "2*sin(x)")
        cleaned = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', cleaned)
        
        return cleaned
    
    def validate_expression(self, expression: str) -> tuple[bool, str]:
        """Validate the expression for safety and correctness."""
        if not expression:
            return False, "Empty expression"
        
        # Check for balanced parentheses
        if expression.count('(') != expression.count(')'):
            return False, "Unbalanced parentheses"
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'__\w+__',  # Dunder methods
            r'import\s',  # Import statements
            r'exec\s*\(',  # Exec calls
            r'eval\s*\(',  # Nested eval
            r'open\s*\(',  # File operations
            r'compile\s*\(',  # Code compilation
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, expression, re.IGNORECASE):
                return False, "Potentially unsafe expression"
        
        return True, "Valid"
    
    def solve(self, expression: str, precision: int = 10) -> Union[float, int, complex, str]:
        """
        Solve a mathematical expression.
        
        Args:
            expression: The mathematical expression to solve
            precision: Number of decimal places for rounding (default: 10)
        
        Returns:
            The result of the evaluation or an error message
        """
        try:
            # Preprocess the expression
            processed = self.preprocess_expression(expression)
            
            # Validate the expression
            is_valid, message = self.validate_expression(processed)
            if not is_valid:
                return f"Error: {message}"
            
            # Evaluate the expression with safe functions only
            result = eval(processed, {"__builtins__": {}}, self.safe_functions)
            
            # Handle different result types
            if isinstance(result, complex):
                # Return complex numbers as-is if imaginary part exists
                if result.imag != 0:
                    return result
                else:
                    result = result.real
            
            # Round to specified precision to avoid floating point errors
            if isinstance(result, float):
                result = round(result, precision)
                # Convert to int if it's a whole number
                if result.is_integer():
                    return int(result)
            
            return result
            
        except ZeroDivisionError:
            return "Error: Division by zero"
        except ValueError as e:
            return f"Error: Invalid value - {str(e)}"
        except TypeError as e:
            return f"Error: Type error - {str(e)}"
        except SyntaxError:
            return "Error: Invalid syntax"
        except NameError as e:
            return f"Error: Unknown function or variable - {str(e)}"
        except OverflowError:
            return "Error: Result too large to compute"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def solve_with_steps(self, expression: str) -> Dict[str, Any]:
        """
        Solve an expression and return detailed information.
        
        Returns:
            Dictionary containing the original expression, processed expression,
            result, and any additional information
        """
        processed = self.preprocess_expression(expression)
        result = self.solve(expression)
        
        return {
            'original': expression,
            'processed': processed,
            'result': result,
            'is_error': isinstance(result, str) and result.startswith('Error:')
        }


# Convenience function for simple usage
def solve_math(expression: str, precision: int = 10) -> Union[float, int, complex, str]:
    """
    Solve a mathematical expression.
    
    Args:
        expression: The mathematical expression to solve
        precision: Number of decimal places for rounding (default: 10)
    
    Returns:
        The result of the evaluation or an error message
    """
    solver = AdvancedMathSolver()
    return solver.solve(expression, precision)


# Example usage and testing
if __name__ == "__main__":
    solver = AdvancedMathSolver()
    
    test_cases = [
        "2 + 2 * 3",
        "sqrt(16) + 4",
        "sin(pi/2)",
        "2^10",
        "factorial(5)",
        "log10(100)",
        "abs(-15)",
        "2(3+4)",
        "gcd(48, 18)",
        "ceil(4.3)",
        "floor(4.9)",
        "min(5, 3, 8, 1)",
        "max(5, 3, 8, 1)",
        "(2+3)*(4+5)",
        "e^2",
        "cos(0)",
    ]
    
    print("Advanced Math Solver - Test Cases")
    print("=" * 50)
    
    for expr in test_cases:
        result = solver.solve_with_steps(expr)
        print(f"\nExpression: {result['original']}")
        print(f"Processed:  {result['processed']}")
        print(f"Result:     {result['result']}")
    
    print("\n" + "=" * 50)
