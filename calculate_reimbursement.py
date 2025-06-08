#!/usr/bin/env python3

import sys
import math

def calculate_reimbursement(days, miles, receipts):
    """
    Calculate reimbursement using the best linear combination discovered.
    
    From my analysis, the best performing simple formula was:
    $75 * days + 0.50 * receipts + 0.50 * miles
    
    But with some adjustments for edge cases.
    """
    
    # Convert inputs to proper types
    days = int(days)
    miles = float(miles)
    receipts = float(receipts)
    
    # Base formula from analysis: the best linear combination I found
    base_calculation = 75 * days + 0.50 * receipts + 0.50 * miles
    
    # Adjustments based on patterns observed
    
    # 1. Efficiency bonus for high miles per day
    miles_per_day = miles / days if days > 0 else 0
    efficiency_bonus = 0
    if miles_per_day > 100:
        efficiency_bonus = (miles_per_day - 100) * 0.3
    
    # 2. Receipt processing adjustments
    receipt_multiplier = 0.5  # Base multiplier
    
    # Adjust receipt multiplier based on receipt amount and trip length
    receipts_per_day = receipts / days if days > 0 else 0
    
    if receipts_per_day > 300:
        # High spending per day - reduce receipt multiplier
        receipt_multiplier = 0.2
    elif receipts_per_day > 150:
        receipt_multiplier = 0.4
    elif receipts_per_day < 50:
        # Low spending - slightly better multiplier
        receipt_multiplier = 0.6
    
    # 3. Trip length adjustments
    days_multiplier = 75  # Base per day
    
    if days == 1:
        days_multiplier = 90  # 1-day trips get slight bonus
    elif days > 10:
        days_multiplier = 65  # Very long trips get reduced per-day rate
    
    # 4. Mileage adjustments
    miles_multiplier = 0.5  # Base mileage rate
    
    if miles > 500:
        # High mileage gets reduced rate for excess
        miles_component = 500 * 0.5 + (miles - 500) * 0.3
    else:
        miles_component = miles * miles_multiplier
    
    # Calculate final amount
    total = (days_multiplier * days + 
             receipt_multiplier * receipts + 
             miles_component + 
             efficiency_bonus)
    
    # Minimum floor based on days
    minimum = days * 60
    total = max(total, minimum)
    
    # Maximum reasonable cap to prevent extreme values
    reasonable_max = days * 300 + receipts * 1.5 + miles * 2
    total = min(total, reasonable_max)
    
    return round(total, 2)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 calculate_reimbursement.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
        sys.exit(1)
    
    days = sys.argv[1]
    miles = sys.argv[2]
    receipts = sys.argv[3]
    
    result = calculate_reimbursement(days, miles, receipts)
    print(result) 