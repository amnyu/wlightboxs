# Blebox wLightBoxS for HA

Home assistant custom component for Blebox wLightBoxS.

Usage:
  * Copy wlightboxs folder into config/custom_components
  * Add to configuration.yaml:
  ```
  light:
  - platform: wlightboxs
    host: <ip_address of your wlightboxs>
    name: <device_name>
  ```
 * Restart home assistant and it should work :D
