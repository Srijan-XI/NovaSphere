# 🤝 Contributing

We welcome contributions from the community! Here's how to get started:

## Quick Start for Contributors

1. **Fork the repository**
   ```bash
   git clone https://github.com/Srijan-XI/NovaSphere.git
   cd NovaSphere
   cd NovaSphere
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install pytest black isort  # Development tools
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

4. **Make your changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

5. **Test your changes**
   ```bash
   python main.py --verbose  # Test the application
   pytest tests/             # Run unit tests (if available)
   black .                   # Format code
   isort .                   # Sort imports
   ```

6. **Commit and push**
   ```bash
   git add .
   git commit -m "Add amazing feature"
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**
   - Provide a clear description of your changes
   - Reference any related issues
   - Include screenshots for UI changes

## Contribution Guidelines

- **Code Quality**: Follow PEP 8 and use Black for formatting
- **Testing**: Add tests for new features and bug fixes
- **Documentation**: Update README and inline documentation
- **Compatibility**: Ensure changes work on both Windows and Linux
- **Performance**: Consider performance impact of changes
- **Security**: Follow security best practices

## Types of Contributions Welcome

- 🐛 **Bug Fixes**: Fix existing issues and improve stability
- ✨ **New Features**: Add new tools or enhance existing ones
- 📚 **Documentation**: Improve documentation and examples
- 🎨 **UI/UX**: Enhance user interfaces and experience
- 🔧 **Infrastructure**: Improve build, test, and deployment processes
- 🌐 **Internationalization**: Add support for more languages
- 📱 **Platform Support**: Add support for additional platforms