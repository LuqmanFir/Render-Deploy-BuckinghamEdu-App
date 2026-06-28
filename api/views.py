from django.shortcuts import render

# Create your views here.
import sympy as sp
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import PiGroupPayloadSerializer

class PiGroupCalculatorView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PiGroupPayloadSerializer(data=request.data)
        
        if serializer.is_valid():
            repeating_vars = serializer.validated_data['repeating']
            non_repeating_vars = serializer.validated_data['nonRepeating']
            
            try:
                pi_groups_result = self.calculate_pi_groups(repeating_vars, non_repeating_vars)
                return Response({
                    "success": True,
                    "pi_groups": pi_groups_result
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    "success": False,
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def calculate_pi_groups(self, repeating, non_repeating):
        if not repeating:
            raise ValueError("You must select at least one repeating variable.")
        if not non_repeating:
            raise ValueError("You must have at least one non-repeating variable.")

        # Allocate unique symbols for repeating variables (a, b, c, etc.)
        symbols_pool = ['a', 'b', 'c', 'd', 'e', 'f']
        symbols_letters = symbols_pool[:len(repeating)]
        symbols = [sp.Symbol(name) for name in symbols_letters]
        
        dimensions_keys = ['M', 'L', 'T', 'Theta']
        pi_groups = []

        # Process each non-repeating variable
        for idx, nr_var in enumerate(non_repeating):
            equations = []
            
            # Formulate algebraic dimensional balance equations
            for dim in dimensions_keys:
                eq_expr = sum(symbols[i] * repeating[i][dim] for i in range(len(repeating))) + nr_var[dim]
                if eq_expr != 0:
                    equations.append(sp.Eq(eq_expr, 0))

            # Solve system via SymPy
            solution = sp.solve(equations, symbols)

            # --- FIX: Robust parsing of SymPy output structures ---
            exp_map_source = {}
            
            if isinstance(solution, dict):
                # SymPy returned a direct dictionary: {a: -1, b: -2}
                exp_map_source = solution
            elif isinstance(solution, list) and len(solution) > 0:
                if isinstance(solution[0], dict):
                    # SymPy returned a list containing a dict: [{a: -1, b: -2}]
                    exp_map_source = solution[0]
                elif isinstance(solution[0], tuple):
                    # SymPy returned a list of tuples: [(-1, -2)]
                    # Map them back to their corresponding symbols manually
                    exp_map_source = {symbols[i]: solution[0][i] for i in range(len(symbols))}
            
            # If no explicit solution found but equations exist, it's an invalid combination
            if not exp_map_source and equations:
                raise ValueError(
                    f"Could not solve a valid linear combination for variable '{nr_var['varName']}' "
                    "with the chosen repeating variables. Make sure they are linearly independent."
                )

            formula_terms = [f"({nr_var['varName']})"]
            exponents_map = {}

            for i, rep_var in enumerate(repeating):
                sym = symbols[i]
                
                # Safely read from our normalized map source
                exp_value = exp_map_source.get(sym, 0)
                
                # Convert Rational fractions to strings/floats cleanly for JSON serialization
                if isinstance(exp_value, sp.Rational):
                    exponents_map[rep_var['varName']] = str(exp_value)
                else:
                    exponents_map[rep_var['varName']] = int(exp_value) if float(exp_value).is_integer() else float(exp_value)

                if exp_value == 0:
                    continue
                elif exp_value == 1:
                    formula_terms.append(f" * ({rep_var['varName']})")
                else:
                    formula_terms.append(f" * ({rep_var['varName']})^{exp_value}")

            formula_string = "".join(formula_terms)

            pi_groups.append({
                "group": f"Π{idx + 1}",
                "formula": formula_string,
                "details": {
                    "non_repeating": nr_var['varName'],
                    "repeating_exponents": exponents_map
                }
            })

        return pi_groups