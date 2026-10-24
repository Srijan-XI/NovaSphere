# Web Interface Usage Guide

## Overview
The web interface provides a modern, responsive dashboard for accessing all system tools through your web browser.

## Starting the Web Interface

### Method 1: Using the unified entry point
```bash
cd NovaSphere
python main.py --interface web --port 5000
```

### Method 2: Direct web interface launch
```bash
cd NovaSphere/interfaces/web
python web_interface.py
```

The web interface will automatically:
- Start the Flask server on http://localhost:5000
- Open your default web browser
- Display the main dashboard

## Features

### 🏠 Dashboard (http://localhost:5000/)
- **System Overview**: Real-time display of CPU, memory, disk usage, and network status
- **Battery Status**: Current battery level and charging status
- **Quick Access**: Direct links to all tool interfaces
- **Real-time Updates**: Toggle automatic refresh of system metrics

### 🔋 Battery Monitor (http://localhost:5000/battery)
- **Battery Display**: Visual battery indicator with percentage and status
- **Charging Information**: Charging rate, time to full, estimated completion time
- **Settings**: Configurable charger wattage, battery capacity, and update intervals
- **Auto Refresh**: Automatic updates every 5 seconds (configurable)
- **Alerts**: Low battery and critical battery warnings

### 🔧 Hardware Diagnostics (http://localhost:5000/diagnostics)
- **Individual Tests**: Bluetooth, Wi-Fi, Camera, Microphone, Speaker, Keyboard
- **Batch Testing**: Run all tests with a single click
- **Test Results**: Pass/fail status with detailed information
- **Export Results**: Download test results as JSON file
- **Test Summary**: Overview of passed, failed, and error tests

### 📊 System Monitor (http://localhost:5000/monitoring)
- **Real-time Metrics**: CPU, memory, disk, and network usage
- **Interactive Charts**: Live graphs showing CPU and memory usage over time
- **System Information**: Detailed CPU and memory specifications
- **Process Monitor**: Top 10 processes by CPU and memory usage
- **Temperature**: System temperature readings (if available)

### 📦 Package Manager (http://localhost:5000/packages)
- **Installed Packages**: View all installed Windows packages
- **Available Updates**: Check for and install package upgrades
- **Package Search**: Find and install new packages
- **Bulk Operations**: Upgrade all packages at once
- **Operation Log**: History of package management actions

## API Endpoints

The web interface provides REST API endpoints for programmatic access:

### Battery API
- `GET /api/battery/info` - Get battery status and information

### Diagnostics API
- `POST /api/diagnostics/run` - Run specific hardware test
  ```json
  {"test": "bluetooth|wifi|camera|microphone|speaker|keyboard"}
  ```

### Monitoring API
- `GET /api/monitoring/metrics` - Get current system metrics

### Package Management API
- `GET /api/packages/status` - Check winget availability
- `GET /api/packages/list` - List installed packages
- `GET /api/packages/upgradable` - List upgradable packages
- `GET /api/packages/search?q=<query>` - Search for packages
- `POST /api/packages/install` - Install package
  ```json
  {"package_id": "Microsoft.WindowsTerminal"}
  ```
- `POST /api/packages/upgrade` - Upgrade specific package
- `POST /api/packages/upgrade-all` - Upgrade all packages
- `POST /api/packages/uninstall` - Uninstall package

## Configuration

### Web Server Settings
The web interface can be configured in `common/config.py`:

```python
WEB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5000,
    "debug": False,
    "auto_open_browser": True
}
```

### Environment Variables
- `FLASK_ENV`: Set to 'development' for debug mode
- `FLASK_PORT`: Override default port 5000
- `FLASK_HOST`: Override default host 127.0.0.1

## Browser Compatibility

The web interface is compatible with:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+

## Security Considerations

- The web interface runs on localhost by default (127.0.0.1)
- CORS is enabled for development but should be configured for production
- No authentication is implemented - suitable for local use only
- Admin privileges may be required for some hardware diagnostics

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```
   Error: [Errno 10048] Only one usage of each socket address is normally permitted
   ```
   - Solution: Use a different port with `--port 5001`

2. **Browser Doesn't Open Automatically**
   - Solution: Manually navigate to http://localhost:5000

3. **API Errors**
   - Check the terminal output for Flask error messages
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

4. **Hardware Tests Fail**
   - Some tests require hardware to be connected (camera, microphone, etc.)
   - Run as administrator for full hardware access

### Debug Mode
Start with debug mode for detailed error information:
```bash
python main.py --interface web --debug
```

## Mobile Support

The web interface is responsive and works on mobile devices:
- 📱 Touch-friendly interface
- 📊 Responsive charts and tables
- 🔄 Swipe gestures supported
- 📲 Mobile-optimized layouts

## Customization

### Themes
The interface uses Bootstrap 5 with custom CSS in `/static/css/`:
- `dashboard.css` - Dashboard styles
- `battery.css` - Battery monitor styles

### Adding New Features
1. Add routes in `web_interface.py`
2. Create HTML templates in `/templates/`
3. Add JavaScript in `/static/js/`
4. Update navigation in templates

## Performance Notes

- Real-time updates occur every 3-5 seconds
- Charts display the last 20 data points
- Process monitoring shows top 10 processes
- All data is fetched asynchronously for smooth performance

## Production Deployment

For production use:
1. Set `debug=False` in Flask configuration
2. Use a production WSGI server like Gunicorn
3. Configure proper CORS settings
4. Add authentication if needed
5. Use HTTPS with proper certificates