#!/usr/bin/env python3

import json
import math

# Load the data
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

def find_simple_mathematical_relationships():
    """Look for simple mathematical patterns that might explain the data"""
    print("=== SEARCHING FOR MATHEMATICAL RELATIONSHIPS ===")
    
    # Test if it's a simple weighted sum
    # reimbursement = a*days + b*miles + c*receipts + d
    
    # Use least squares to find best coefficients
    import numpy as np
    
    # Prepare data matrices
    X = []
    y = []
    
    for case in cases:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        reimbursement = case['expected_output']
        
        # Add features: days, miles, receipts, constant term
        X.append([days, miles, receipts, 1])
        y.append(reimbursement)
    
    X = np.array(X)
    y = np.array(y)
    
    # Solve for coefficients using least squares
    coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
    
    print(f"Best linear fit: {coeffs[0]:.2f}*days + {coeffs[1]:.3f}*miles + {coeffs[2]:.3f}*receipts + {coeffs[3]:.2f}")
    
    # Test accuracy
    total_error = 0
    for i, case in enumerate(cases[:100]):
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = coeffs[0]*days + coeffs[1]*miles + coeffs[2]*receipts + coeffs[3]
        error = abs(predicted - expected)
        total_error += error
    
    avg_error = total_error / 100
    print(f"Average error on first 100 cases: ${avg_error:.2f}")
    
    return coeffs

def test_polynomial_relationships():
    """Test if there are polynomial relationships"""
    print("\n=== TESTING POLYNOMIAL RELATIONSHIPS ===")
    
    import numpy as np
    
    # Test quadratic terms
    X = []
    y = []
    
    for case in cases[:500]:  # Use subset for faster computation
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        reimbursement = case['expected_output']
        
        # Features: days, miles, receipts, days^2, miles^2, receipts^2, days*miles, etc.
        X.append([
            days, miles, receipts,
            days**2, miles**2, receipts**2,
            days*miles, days*receipts, miles*receipts,
            1  # constant term
        ])
        y.append(reimbursement)
    
    X = np.array(X)
    y = np.array(y)
    
    # Solve for coefficients
    coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
    
    print("Polynomial coefficients:")
    feature_names = ['days', 'miles', 'receipts', 'days^2', 'miles^2', 'receipts^2', 
                     'days*miles', 'days*receipts', 'miles*receipts', 'constant']
    
    for i, name in enumerate(feature_names):
        if abs(coeffs[i]) > 0.001:  # Only show significant coefficients
            print(f"  {name}: {coeffs[i]:.4f}")
    
    # Test accuracy
    total_error = 0
    test_cases = cases[500:600]  # Use different data for testing
    
    for case in test_cases:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        features = [
            days, miles, receipts,
            days**2, miles**2, receipts**2,
            days*miles, days*receipts, miles*receipts,
            1
        ]
        
        predicted = sum(coeffs[i] * features[i] for i in range(len(features)))
        error = abs(predicted - expected)
        total_error += error
    
    avg_error = total_error / len(test_cases)
    print(f"Average error on test cases: ${avg_error:.2f}")
    
    return coeffs

def analyze_ratio_patterns():
    """Look for patterns in ratios"""
    print("\n=== ANALYZING RATIO PATTERNS ===")
    
    ratios = []
    for case in cases[:200]:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        reimbursement = case['expected_output']
        
        # Calculate various ratios
        per_day = reimbursement / days
        per_mile = reimbursement / miles if miles > 0 else 0
        per_receipt_dollar = reimbursement / receipts if receipts > 0 else 0
        
        ratios.append({
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'reimbursement': reimbursement,
            'per_day': per_day,
            'per_mile': per_mile,
            'per_receipt_dollar': per_receipt_dollar,
            'miles_per_day': miles/days,
            'receipts_per_day': receipts/days
        })
    
    # Look for cases with similar ratios
    print("Cases with highest per-day rates:")
    sorted_by_per_day = sorted(ratios, key=lambda x: x['per_day'], reverse=True)
    for r in sorted_by_per_day[:10]:
        print(f"  {r['days']}d, {r['miles']:.0f}mi, ${r['receipts']:.2f} → ${r['reimbursement']:.2f} (${r['per_day']:.2f}/day)")
    
    print("\nCases with lowest per-day rates:")
    for r in sorted_by_per_day[-10:]:
        print(f"  {r['days']}d, {r['miles']:.0f}mi, ${r['receipts']:.2f} → ${r['reimbursement']:.2f} (${r['per_day']:.2f}/day)")

def look_for_discrete_rules():
    """Look for discrete thresholds or rules"""
    print("\n=== LOOKING FOR DISCRETE RULES ===")
    
    # Group by ranges and look for patterns
    by_days = {}
    for case in cases:
        days = case['input']['trip_duration_days']
        if days not in by_days:
            by_days[days] = []
        by_days[days].append(case)
    
    # Look at each day length separately
    for days in sorted(by_days.keys())[:5]:  # First 5 day lengths
        cases_for_days = by_days[days]
        print(f"\n{days}-day trips ({len(cases_for_days)} cases):")
        
        # Look for simple relationships
        simple_cases = [c for c in cases_for_days if c['input']['receipts'] < 100 and c['input']['miles'] < 200]
        if simple_cases:
            print(f"  Simple cases (low receipts & miles):")
            for case in simple_cases[:5]:
                r = case['expected_output']
                m = case['input']['miles']
                rec = case['input']['total_receipts_amount']
                print(f"    {m:.0f}mi, ${rec:.2f} → ${r:.2f}")

if __name__ == "__main__":
    try:
        import numpy as np
        coeffs = find_simple_mathematical_relationships()
        poly_coeffs = test_polynomial_relationships()
    except ImportError:
        print("NumPy not available, skipping mathematical optimization")
        coeffs = None
        poly_coeffs = None
    
    analyze_ratio_patterns()
    look_for_discrete_rules() 