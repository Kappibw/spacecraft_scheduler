# Endurance Scheduler

A comprehensive task scheduling system for robotic applications with support for complex constraints, resource management, and multiple scheduling algorithms.

## 🚀 Quick Start

### Run the Complete Demo
```bash
python endurance_scheduler_demo.py
```

### Run Algorithm Comparison
```bash
python endurance_scheduler.py
```

### Run Comprehensive Example
```bash
python endurance_scheduler_example.py
```

## 📁 Project Structure

```
/app/
├── spacecraft_scheduler/                # Main scheduler project
│   ├── endurance_scheduler_demo.py     # Complete demo and usage guide
│   ├── endurance_scheduler.py          # Main algorithm comparison script
│   ├── endurance_scheduler_example.py  # Comprehensive example with testing
│   ├── ENDURANCE_SCHEDULER_GUIDE.md   # Detailed usage guide
│   ├── requirements/                   # Python dependencies
│   ├── src/                           # Source code
│   │   ├── algorithms/                # Scheduling algorithms
│   │   ├── common/                    # Core models and managers
│   │   └── testing/                   # Testing framework
│   └── tests/                         # Unit tests
├── results/                           # Generated outputs (shared)
├── logs/                              # Log files (shared)
└── data/                              # Data files (shared)
```

## 🏗️ Architecture

### Core Models
- **`EnduranceTask`**: Tasks with time windows, duration ranges, and constraints
- **`EnduranceResource`**: Resources (integer or cumulative rate types)
- **`EnduranceScheduledTask`**: Scheduled tasks with start/end times
- **`EnduranceScheduleResult`**: Scheduling operation results

### Algorithms
- **`EnduranceSimpleScheduler`**: Priority-based greedy scheduler
- **`EnduranceMILPScheduler`**: MILP-based scheduler using OR-Tools

### Testing Framework
- **`EnduranceTestRunner`**: Runs test cases against schedulers
- **`EnduranceTestCase`**: Represents test scenarios

## 📋 Features

- ✅ Complex task constraints and dependencies
- ✅ Multiple resource types (integer and cumulative rate)
- ✅ Time window and duration range support
- ✅ Priority-based scheduling
- ✅ MILP optimization with OR-Tools
- ✅ Comprehensive testing framework
- ✅ Visualization and reporting
- ✅ Extensible algorithm architecture

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 📚 Documentation

See `ENDURANCE_SCHEDULER_GUIDE.md` for detailed usage instructions and examples.

## 🔧 Development

This project is developed in a containerized environment. The git repository is set up inside the container for seamless development workflow.

### Git Configuration
- Repository initialized in container
- User: Kappi Patterson (kappi.patterson@gmail.com)
- Branch: main

## 📄 License

This project is part of the Endurance robotic scheduling system.
