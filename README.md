# Scheduler

A comprehensive task scheduling system for space robotic applications with support for complex constraints, resource management, and multiple scheduling algorithms.

## Development - Important!

This project is developed in a containerized environment. It should be run as a submodule inside the
`spacecraft_scheduler_config` repo, which can be found [here](https://github.com/Kappibw/spacecraft_scheduler_config).

The config wrapper repo will take care of building the docker container with all necessary dependencies as well
as the licensing for the Gurobi solver.

## Documentation

See `SCHEDULER_GUIDE.md` for detailed usage instructions and examples.

## Project Structure

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
