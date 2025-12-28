"""Sensor platform for ZTE Router integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfDataRate,
    UnitOfInformation,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN


@dataclass
class ZTESensorEntityDescription(SensorEntityDescription):
    """Describes ZTE Router sensor entity."""
    
    value_fn: Callable[[dict[str, Any]], Any] | None = None
    data_key: str | None = None


SENSORS: tuple[ZTESensorEntityDescription, ...] = (
    # Network signal sensors
    ZTESensorEntityDescription(
        key="network_type",
        name="Network Type",
        icon="mdi:network",
        value_fn=lambda data: data.get("network_info", {}).get("network_type"),
    ),
    ZTESensorEntityDescription(
        key="signal_strength",
        name="Signal Strength",
        icon="mdi:signal",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("network_info", {}).get("signalbar"),
    ),
    ZTESensorEntityDescription(
        key="lte_rsrp",
        name="LTE RSRP",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("network_info", {}).get("lte_rsrp"),
    ),
    ZTESensorEntityDescription(
        key="lte_rsrq",
        name="LTE RSRQ",
        native_unit_of_measurement="dB",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("network_info", {}).get("lte_rsrq"),
    ),
    ZTESensorEntityDescription(
        key="lte_rssi",
        name="LTE RSSI",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("network_info", {}).get("lte_rssi"),
    ),
    ZTESensorEntityDescription(
        key="lte_snr",
        name="LTE SNR",
        native_unit_of_measurement="dB",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("network_info", {}).get("lte_snr"),
    ),
    ZTESensorEntityDescription(
        key="nr5g_rsrp",
        name="5G RSRP",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("network_info", {}).get("nr5g_rsrp"),
    ),
    ZTESensorEntityDescription(
        key="nr5g_rssi",
        name="5G RSSI",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("network_info", {}).get("nr5g_rssi"),
    ),
    ZTESensorEntityDescription(
        key="nr5g_snr",
        name="5G SNR",
        native_unit_of_measurement="dB",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("network_info", {}).get("nr5g_snr"),
    ),
    # Network info
    ZTESensorEntityDescription(
        key="network_provider",
        name="Network Provider",
        icon="mdi:network-outline",
        value_fn=lambda data: data.get("network_info", {}).get("network_provider_fullname"),
    ),
    ZTESensorEntityDescription(
        key="wan_active_band",
        name="Active Band",
        icon="mdi:signal-variant",
        value_fn=lambda data: data.get("network_info", {}).get("wan_active_band"),
    ),
    ZTESensorEntityDescription(
        key="nr5g_action_band",
        name="5G Band",
        icon="mdi:signal-5g",
        value_fn=lambda data: data.get("network_info", {}).get("nr5g_action_band"),
    ),
    ZTESensorEntityDescription(
        key="cell_id",
        name="Cell ID",
        icon="mdi:tower-fire",
        value_fn=lambda data: data.get("network_info", {}).get("cell_id"),
    ),
    # Connection status
    ZTESensorEntityDescription(
        key="wireless_devices",
        name="Wireless Devices",
        icon="mdi:devices",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("device_info", {}).get("wireless_num"),
    ),
    ZTESensorEntityDescription(
        key="lan_devices",
        name="LAN Devices",
        icon="mdi:lan",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("device_info", {}).get("lan_num"),
    ),
    ZTESensorEntityDescription(
        key="wan_status",
        name="WAN Status",
        icon="mdi:wan",
        value_fn=lambda data: data.get("router_status", {}).get("current_wan_status"),
    ),
    # Data usage and speed
    ZTESensorEntityDescription(
        key="tx_speed",
        name="Upload Speed",
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:upload",
        value_fn=lambda data: data.get("data_usage", {}).get("real_tx_speed"),
    ),
    ZTESensorEntityDescription(
        key="rx_speed",
        name="Download Speed",
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:download",
        value_fn=lambda data: data.get("data_usage", {}).get("real_rx_speed"),
    ),
    ZTESensorEntityDescription(
        key="tx_bytes",
        name="Uploaded Data",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:upload",
        value_fn=lambda data: data.get("data_usage", {}).get("real_tx_bytes"),
    ),
    ZTESensorEntityDescription(
        key="rx_bytes",
        name="Downloaded Data",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:download",
        value_fn=lambda data: data.get("data_usage", {}).get("real_rx_bytes"),
    ),
    # WiFi
    ZTESensorEntityDescription(
        key="wifi_status",
        name="WiFi Status",
        icon="mdi:wifi",
        value_fn=lambda data: "On" if data.get("wlan_info", {}).get("wifi_onoff") == "1" else "Off",
    ),
    ZTESensorEntityDescription(
        key="ssid",
        name="SSID",
        icon="mdi:wifi-settings",
        value_fn=lambda data: data.get("wlan_info", {}).get("main2g_ssid"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ZTE Router sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    entities = [
        ZTERouterSensor(coordinator, entry, description)
        for description in SENSORS
    ]
    
    async_add_entities(entities)


class ZTERouterSensor(CoordinatorEntity, SensorEntity):
    """Representation of a ZTE Router sensor."""
    
    entity_description: ZTESensorEntityDescription
    
    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        description: ZTESensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "ZTE Router",
            "manufacturer": "ZTE",
            "model": "Mobile Router",
        }
    
    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.entity_description.value_fn:
            value = self.entity_description.value_fn(self.coordinator.data)
            
            # Skip if value is None, empty string, or 0 for optional sensors
            if value is None or value == "":
                return None
            
            # Convert string numbers to appropriate types
            if isinstance(value, str):
                # Try to convert to float for numeric values
                try:
                    return float(value)
                except ValueError:
                    return value
            
            return value
        
        return None
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Entity is available if coordinator has data and the value is not None
        return (
            super().available
            and self.native_value is not None
        )
