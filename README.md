# 📡 ZTE Router Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square)](https://hacs.xyz/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

A Home Assistant integration for **ZTE mobile routers** (tested with ALDI TALK edition G5TS). Monitor signal strength, network status, data usage, and WiFi information directly from Home Assistant.

*If this integration saves you time, consider to [buy me a ☕](https://buymeacoffee.com/antondaubert).*

### Disclaimer
This is a **community-developed integration** for interoperability with Home Assistant. It is not affiliated with or supported by ZTE Corporation.

Provided "as-is" under the MIT License for personal, non-commercial use with devices you own. Use at your own risk.

---

## Current Features

- **Signal Monitoring** - Real-time LTE and 5G signal quality (RSRP, RSRQ, RSSI, SNR)
- **Network Information** - Connection type, provider, band, cell ID
- **Connection Status** - WAN status and connection mode
- **Data Usage** - Upload/download speeds and data transfer totals
- **Device Tracking** - Connected devices count (LAN and WiFi)
- **WiFi Information** - Status and SSID

*Have suggestions? Check out [Discussions](https://github.com/antondaubert/zte-router/discussions)*

---

## Installation

### Prerequisites
- Home Assistant 2023.1 or newer
- ZTE router accessible on your network (typically at `192.168.0.1`)
- Router password (optional, but required for speed sensors and device counts)

### HACS Installation

1. Ensure [HACS](https://hacs.xyz/) is installed
2. Navigate to HACS → Integrations
3. Click ⋮ → Custom repositories  
4. Add: `https://github.com/antondaubert/zte-router`
5. Category: Integration
6. Search for "ZTE Router" and install
7. Restart Home Assistant
8. Settings → Devices & Services → Add Integration → "ZTE Router"

### Manual Installation

1. Download the latest release
2. Copy `custom_components/zte_router` to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Settings → Devices & Services → Add Integration → "ZTE Router"

---

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **ZTE Router**
4. Enter your router's IP address (default: `192.168.0.1`)
5. Optionally enter the router password (required for speed and device count sensors)

The integration will create sensors for all available metrics.

---

## Available Sensors

### Network Signal
- LTE RSRP (Signal strength)
- LTE RSRQ (Signal quality)
- LTE RSSI (Signal power)
- LTE SNR (Signal-to-noise ratio)
- 5G RSRP/RSRQ/RSSI/SNR (when connected to 5G)

### Connection Info
- Network Type (e.g., ENDC for 5G NSA)
- Network Provider
- LTE Band
- 5G Band
- Cell ID

### Data Usage
- Upload Speed (bytes/sec)
- Download Speed (bytes/sec)
- Uploaded Data (total bytes)
- Downloaded Data (total bytes)

### Device Tracking
- LAN Devices (count)
- Wireless Devices (count)

### WiFi
- WiFi Status (On/Off)
- SSID (Network name)

### Connection Status
- WAN Status
- Connection Mode

---

## Technical Details

### API Communication
The integration uses the router's built-in JSON-RPC 2.0 API:
- **Endpoint**: `http://192.168.0.1/ubus/`
- **Protocol**: JSON-RPC 2.0 over HTTP
- **Authentication**: SHA256 double-hashed password (when provided)
- **Update Interval**: 30 seconds

### Supported API Methods
- `router_get_status` / `router_get_status_no_auth` - Connection status
- `nwinfo_get_netinfo` - Network and signal information
- `get_wwandst` - Data usage statistics (requires authentication)
- `router_get_user_list_num` - Connected devices (requires authentication)
- `zwrt_wlan.report` - WiFi information (requires authentication)

---

## Troubleshooting

### Authentication Fails
- The router may lock login attempts after 5 failed tries (5-minute lockout)
- Verify the password is correct by logging into the web interface
- Wait 5 minutes if locked out, then reload the integration

---

## Community & Support

- **Discussions**: Questions and ideas → [GitHub Discussions](https://github.com/antondaubert/zte-router/discussions)
- **Issues**: Bug reports and feature requests → [GitHub Issues](https://github.com/antondaubert/zte-router/issues)

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

*Stay connected! 📶*
