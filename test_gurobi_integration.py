#!/usr/bin/env python3
"""
Test script to verify Gurobi integration works correctly.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.append('/app')

def test_gurobi_import():
    """Test that Gurobi can be imported."""
    try:
        import gurobipy as gp
        from gurobipy import GRB
        print("✅ Gurobi import successful")
        return True
    except ImportError as e:
        print(f"❌ Gurobi import failed: {e}")
        return False

def test_milp_scheduler_import():
    """Test that MILP scheduler can be imported."""
    try:
        from src.algorithms.milp.milp_scheduler import MILPScheduler
        print("✅ MILP Scheduler import successful")
        return True
    except ImportError as e:
        print(f"❌ MILP Scheduler import failed: {e}")
        return False

def test_simple_gurobi_model():
    """Test creating a simple Gurobi model."""
    try:
        import gurobipy as gp
        from gurobipy import GRB
        
        # Create a simple model
        model = gp.Model("test")
        model.setParam('OutputFlag', 0)  # Suppress output
        
        # Add a simple variable
        x = model.addVar(vtype=GRB.BINARY, name='x')
        
        # Add a simple constraint
        model.addConstr(x >= 0, name='constraint1')
        
        # Set objective
        model.setObjective(x, GRB.MAXIMIZE)
        
        # Optimize
        model.optimize()
        
        if model.status == GRB.OPTIMAL:
            print("✅ Simple Gurobi model solved successfully")
            return True
        else:
            print(f"❌ Simple Gurobi model failed with status: {model.status}")
            return False
            
    except Exception as e:
        print(f"❌ Simple Gurobi model failed: {e}")
        return False

def test_milp_scheduler_creation():
    """Test creating MILP scheduler instance."""
    try:
        from src.algorithms.milp.milp_scheduler import MILPScheduler
        
        scheduler = MILPScheduler(time_limit=60)
        print("✅ MILP Scheduler instance created successfully")
        return True
    except Exception as e:
        print(f"❌ MILP Scheduler creation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Gurobi Integration")
    print("=" * 40)
    print("Note: Make sure to install requirements with:")
    print("pip install -r requirements/commercial.txt")
    print()
    
    tests = [
        test_gurobi_import,
        test_milp_scheduler_import,
        test_simple_gurobi_model,
        test_milp_scheduler_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Gurobi integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
