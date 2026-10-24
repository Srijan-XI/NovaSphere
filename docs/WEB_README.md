# 🌐 Web Interface - NovaSphere

## Overview

The web interface provides a modern, responsive single-page application (SPA) for accessing all system tools through your web browser. Built with Flask, Bootstrap 5, and vanilla JavaScript, it offers real-time system monitoring, hardware diagnostics, battery management, and package management.

## 📁 File Structure

```
interfaces/web/
├── index.html              # Main SPA entry point
├── main.css                # Primary stylesheet with modern design
├── app.js                  # Main JavaScript application logic
├── standalone_server.py    # Standalone Flask server for testing
├── web_interface.py        # Integrated Flask interface class
├── templates/              # Individual page templates (legacy)
│   ├── dashboard.html
│   ├── battery.html
│   ├── diagnostics.html
│   ├── monitoring.html
│   └── packages.html
└── static/                 # Static assets
    ├── css/
    │   ├── dashboard.css
    │   └── battery.css
    └── js/
        ├── dashboard.js
        ├── battery.js
        ├── diagnostics.js
        ├── monitoring.js
        └── packages.js
```

## 🚀 Getting Started

### Prerequisites

Install required Python packages:

```bash
pip install flask flask-cors psutil
```

### Method 1: Standalone Server (Recommended for Testing)

The easiest way to run the web interface:

```bash
cd NovaSphere/interfaces/web
python standalone_server.py
```

This will:
- ✅ Start the Flask server on http://127.0.0.1:5000
- ✅ Automatically open your default browser
- ✅ Provide real system data where available
- ✅ Use mock data for demonstration purposes

### Method 2: Integrated with Main Application

```bash
cd NovaSphere
python main.py --interface web --port 5000
```

### Method 3: Direct Flask Run

```bash
cd NovaSphere/interfaces/web
flask --app standalone_server run --host=127.0.0.1 --port=5000
```

## 🎨 Features

### 🏠 Home Page
- **Hero Section**: Welcome message with call-to-action buttons
- **Feature Cards**: Interactive navigation to different tools
- **System Status**: Real-time overview of CPU, Memory, Disk, and Battery
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile

### 📊 Dashboard
- **System Overview**: Comprehensive metrics in chart format
- **System Information**: Platform, architecture, processor details
- **Top Processes**: Live list of most resource-intensive processes
- **Network Information**: Connection status and I/O statistics

### 🔋 Battery Monitor
- **Visual Battery Indicator**: Animated battery icon with percentage
- **Charging Information**: Real-time charging status and estimates
- **Power Management**: Detailed power source information
- **Health Monitoring**: Battery condition assessment

### 🔧 Hardware Diagnostics
- **Individual Tests**: Bluetooth, Wi-Fi, Camera, Microphone, Speaker, Keyboard
- **Batch Testing**: Run all tests with progress tracking
- **Results Export**: Download test results as JSON
- **Visual Feedback**: Color-coded pass/fail indicators

### 📈 System Monitoring
- **Real-time Charts**: Interactive CPU and memory usage graphs
- **Temperature Monitoring**: System temperature readings (where available)
- **Process Monitoring**: Detailed process information with resource usage
- **Performance Metrics**: Comprehensive system performance data

### 📦 Package Management
- **Package Discovery**: Search and install new packages
- **Update Management**: Check for and install updates
- **Inventory Tracking**: List all installed packages
- **Bulk Operations**: Upgrade all packages at once

## 🛠️ Technical Details

### Architecture

The web interface follows a modern SPA (Single Page Application) architecture:

- **Frontend**: Pure JavaScript ES6+ with Bootstrap 5
- **Backend**: Flask REST API with CORS support
- **Data Layer**: Real-time system data via psutil
- **Styling**: Custom CSS with CSS Grid and Flexbox
- **Charts**: Chart.js for interactive visualizations

### API Endpoints

#### System Monitoring
- `GET /api/monitoring/metrics` - Get comprehensive system metrics
- `GET /api/battery/info` - Get battery status and information

#### Hardware Diagnostics
- `POST /api/diagnostics/run` - Run specific hardware tests
  ```json
  {"test": "bluetooth|wifi|camera|microphone|speaker|keyboard"}
  ```

#### Package Management
- `GET /api/packages/status` - Check winget availability
- `GET /api/packages/list` - List installed packages
- `GET /api/packages/count` - Get package counts

### Real-time Updates

The interface supports real-time updates through:
- **Periodic Polling**: Automatic refresh every 30 seconds for home page
- **Manual Refresh**: User-triggered updates for all sections
- **Smart Caching**: Efficient data handling to minimize server load

## 🎯 Usage Examples

### Running System Diagnostics

1. Navigate to the diagnostics section
2. Click "Run All Tests" or select individual tests
3. View real-time results with pass/fail indicators
4. Export results for documentation

### Monitoring System Performance

1. Go to the monitoring section
2. Enable real-time monitoring
3. View live charts and metrics
4. Export performance data

### Managing Packages

1. Access the package management section
2. Search for new packages to install
3. Check for available updates
4. Perform bulk operations

## 🔧 Customization

### Styling

Modify `main.css` to customize the appearance:
- Change color scheme by updating CSS variables
- Adjust responsive breakpoints
- Modify animation and transition effects

### Functionality

Extend `app.js` to add new features:
- Add new navigation sections
- Implement additional API endpoints
- Create custom chart visualizations

### Configuration

Update the configuration in `standalone_server.py`:
```python
CONFIG = {
    'host': '127.0.0.1',    # Server host
    'port': 5000,           # Server port
    'debug': True,          # Debug mode
    'auto_open_browser': True  # Auto-open browser
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Use a different port
   python standalone_server.py --port 5001
   ```

2. **Missing Dependencies**
   ```bash
   pip install flask flask-cors psutil
   ```

3. **Permission Issues**
   - Run as administrator for full hardware access
   - Some diagnostic tests require elevated privileges

4. **Browser Compatibility**
   - Ensure you're using a modern browser (Chrome 90+, Firefox 88+, Edge 90+)
   - Enable JavaScript if disabled

### Debug Mode

Enable debug mode for detailed error information:
```python
CONFIG['debug'] = True
```

## 🔒 Security Notes

- The web interface is designed for local use only (127.0.0.1)
- No authentication is implemented - suitable for single-user systems
- CORS is enabled for development - configure appropriately for production
- Admin privileges may be required for some hardware diagnostics

## 📱 Mobile Support

The interface is fully responsive and supports:
- Touch-friendly navigation
- Mobile-optimized layouts
- Swipe gestures
- Responsive charts and tables

## 🚀 Performance

Optimizations included:
- Efficient polling intervals (30s for home, 5s for monitoring)
- Smart data caching
- Lazy loading of heavy components
- Compressed assets and minimal dependencies

## 🔄 Updates and Maintenance

To update the web interface:
1. Modify the relevant files (index.html, main.css, app.js)
2. Test with the standalone server
3. Restart the main application to see changes

## 📄 License

This web interface is part of the NovaSphere project and follows the same licensing terms.

---

**💡 Pro Tip**: For the best experience, use the standalone server during development and testing, then integrate with the main application for production use.