# Scheduler

A comprehensive task scheduling system for robotic applications with support for complex constraints, resource management, and multiple scheduling algorithms.

## 🚀 Quick Start

### Run the Complete Demo
```bash
python scheduler_demo.py
```

### Run Algorithm Comparison
```bash
python scheduler.py
```

### Run Comprehensive Example
```bash
python scheduler_example.py
```

## 📁 Project Structure

```
/app/
├── spacecraft_scheduler/                # Main scheduler project
│   ├── scheduler_demo.py               # Complete demo and usage guide
│   ├── scheduler.py                    # Main algorithm comparison script
│   ├── scheduler_example.py            # Comprehensive example with testing
│   ├── SCHEDULER_GUIDE.md              # Detailed usage guide
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
- **`Task`**: Tasks with time windows, duration ranges, and constraints
- **`Resource`**: Resources (integer or cumulative rate types)
- **`ScheduledTask`**: Scheduled tasks with start/end times
- **`ScheduleResult`**: Scheduling operation results

### Algorithms
- **`SimpleScheduler`**: Priority-based greedy scheduler
- **`MILPScheduler`**: MILP-based scheduler using Gurobi

### Testing Framework
- **`TestRunner`**: Runs test cases against schedulers
- **`TestCase`**: Represents test scenarios

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

This project is part of the Scheduler robotic scheduling system.
