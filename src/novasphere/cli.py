#!/usr/bin/env python3
"""
NovaSphere CLI Entry Point
Main command-line interface for the application
"""

import sys
import argparse
from pathlib import Path

from novasphere import __version__, config, logger
from novasphere.utils.dependency_checker import check_dependencies_startup
from novasphere.ui.cli.cli_interface import CLIInterface
from novasphere.ui.gui.gui_interface import GUIInterface
from web.backend.app import WebInterface


def main():
    """Main entry point for NovaSphere"""
    
    # Check dependencies first (unless skipped)
    if '--no-deps-check' not in sys.argv:
        print("Checking dependencies...")
        if not check_dependencies_startup():
            sys.exit(1)
        print("All dependencies OK!\n")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        prog='nova',
        description='NovaSphere: All-in-One System Diagnostic & Monitoring Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Available Tools:
  battery     - Battery monitoring and charging analysis
  diagnostics - Hardware component diagnostics
  monitoring  - System performance monitoring  

Interface Options:
  --cli       - Command Line Interface (default)
  --gui       - Graphical User Interface
  --web       - Web Browser Interface

Examples:
  nova --cli battery
  nova --gui
  nova --web --port 8080
  python -m novasphere --gui
        '''
    )
    
    # Interface selection
    interface_group = parser.add_mutually_exclusive_group()
    interface_group.add_argument('--cli', action='store_true',
                                help='Use Command Line Interface (default)')
    interface_group.add_argument('--gui', action='store_true',
                                help='Use Graphical User Interface')
    interface_group.add_argument('--web', action='store_true',
                                help='Use Web Browser Interface')
    
    # Web interface options
    parser.add_argument('--port', type=int, default=8080,
                       help='Port for web interface (default: 8080)')
    parser.add_argument('--host', default='localhost',
                       help='Host for web interface (default: localhost)')
    
    # Tool selection (for CLI)
    parser.add_argument('tool', nargs='?', 
                       choices=['battery', 'diagnostics', 'monitoring'],
                       help='Tool to run (CLI only)')
    
    # General options
    parser.add_argument('--config', 
                       help='Path to configuration file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--no-deps-check', action='store_true',
                       help='Skip dependency check on startup')
    parser.add_argument('--version', action='version', 
                       version=f'%(prog)s {__version__}')
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logger.set_level('DEBUG')
    
    # Load configuration
    if args.config:
        config.load_from_file(args.config)
    
    logger.info(f"Starting NovaSphere v{__version__}")
    
    try:
        # Launch appropriate interface
        if args.gui:
            logger.info("Launching GUI interface")
            interface = GUIInterface(config, logger)
            interface.run()
            
        elif args.web:
            logger.info(f"Launching web interface on {args.host}:{args.port}")
            interface = WebInterface(config, logger)
            interface.run(host=args.host, port=args.port)
            
        else:  # CLI (default)
            logger.info("Launching CLI interface")
            interface = CLIInterface(config, logger)
            interface.run(args.tool)
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Application error: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
