# FAQ

> This section addresses common questions and issues. If your question isn't answered here, please check the [documentation](README.md)

## General Questions

**Q: What's the difference between this and individual tools?**
A: The unified application combines all tools into a single interface with shared configuration, logging, and data management. It's more efficient and easier to maintain.

**Q: Can I still use the individual legacy tools?**
A: Yes, but they're deprecated. We recommend migrating to the unified application for the best experience and ongoing support.

**Q: Is this tool safe to use?**
A: Yes, the tool only reads system information and doesn't modify system files. It's open-source, so you can review the code.

## Installation Questions

**Q: Do I need administrator/root privileges?**
A: Generally no, but some hardware tests (especially on Linux) may require elevated privileges for hardware access.

**Q: Why does the Linux installation script ask for sudo?**
A: To install system dependencies and set up hardware access permissions. The application itself runs as a regular user.

**Q: Can I install this without internet access?**
A: No, you need internet to download Python dependencies. However, once installed, most features work offline.

## Usage Questions

**Q: Which interface should I use?**
A: CLI for automation and scripting, Web for visual monitoring and remote access, GUI (when available) for desktop integration.

**Q: Can I run this on a server?**
A: Yes, the CLI and web interfaces work well on headless servers. The web interface is particularly useful for remote monitoring.

**Q: How much system resources does it use?**
A: Very minimal - typically 20-50MB RAM and <1% CPU during idle. Resource usage is configurable.

## Technical Questions

**Q: What Python version do I need?**
A: Python 3.7 or higher. We recommend Python 3.9+ for the best experience.

**Q: Can I extend this with custom tools?**
A: Yes, the modular architecture makes it easy to add new tools. See the developer documentation in the repository and check out the existing tools in `src/aio_sdms/core/` for examples.

**Q: Does it work on ARM processors?**
A: Yes, it works on ARM64 systems including Raspberry Pi and Apple Silicon Macs (with manual installation).

**Q: How do I report bugs or request features?**
A: Use GitHub Issues for bugs and feature requests. Include system information and detailed reproduction steps.