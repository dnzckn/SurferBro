# Contributing to SurferBro

Thank you for your interest in contributing to SurferBro!

## Development Setup

1. Clone the repository
```bash
git clone <repository-url>
cd SurferBro
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode
```bash
pip install -e ".[dev]"
```

## Code Style

We use the following tools for code quality:
- `black` for formatting
- `flake8` for linting
- `mypy` for type checking
- `isort` for import sorting

Run before committing:
```bash
black surferbro/
isort surferbro/
flake8 surferbro/
mypy surferbro/
```

## Testing

Run tests with pytest:
```bash
pytest tests/
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Areas for Contribution

- Improving wave physics realism
- Adding more obstacle types
- Enhancing visualization
- Optimizing RL training
- Adding new RL algorithms
- Improving documentation
- Creating tutorials and examples

## Questions?

Open an issue for any questions or suggestions!
