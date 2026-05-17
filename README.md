MOUND
Monitoring Outdoor Urban Naturalist Device
A backyard sensor observatory by Jeffrey Fisher - West Mound St., Columbus, Ohio

================================================================================

WHAT IS MOUND?
MOUND is a small autonomous outdoor sensor station built on a Raspberry Pi Zero W,
powered by a USB battery bank with solar trickle charging. It quietly monitors the
backyard environment and logs data automatically - a personal naturalist's field
instrument inspired by unmanned space probes. Simple by design. The journey is the point.

Part of the Fisher backyard project family alongside the Adena rover and Hopewell rockets.

================================================================================

HARDWARE
- Raspberry Pi Zero W (2017) - outdoor node
- DHT11 - temperature and humidity sensor
- GA1A12S202 - analog light sensor (pending ADS1115 wiring)
- ADS1115 - 16-bit 4-channel analog to digital converter
- Capacitive soil moisture sensor x2
- INA219 - battery/solar current and voltage monitor
- Raspberry Pi Camera Rev 1.3 (pending ribbon cable adapter)
- Romoss Solo 5 10,000mAh battery bank
- Solar panel (trickle charging - experimental)

================================================================================

DIRECTORY STRUCTURE

~/mound/
    README.txt          - this file
    scripts/
        log_sensors.py  - main sensor logging script
    data/
        YYYY-MM.txt     - monthly sensor logs (one file per month)
        errors.txt      - sensor error log

================================================================================

HOW IT WORKS
A cronjob fires log_sensors.py every 30 minutes automatically.
The script reads the DHT11 sensor (temp + humidity), retries up to 3 times
on a failed read, then appends a timestamped line to the current month's
data file. If all 3 attempts fail, it logs the error to errors.txt instead.

Data format (monthly log):
    YYYY-MM-DD HH:MM:SS, 72.0F, 82%

Cronjob:
    */30 * * * * python /home/ramblinray/mound/scripts/log_sensors.py

================================================================================

USEFUL COMMANDS

Check latest readings:
    cat ~/mound/data/2026-05.txt

Check error log:
    cat ~/mound/data/errors.txt

Run script manually:
    python ~/mound/scripts/log_sensors.py

View cronjob:
    crontab -l

================================================================================

PLANNED SENSORS / FUTURE
- Light levels and dawn/dusk detection (GA1A12S202 + ADS1115)
- Soil moisture (capacitive sensor + ADS1115)
- Battery and solar monitoring (INA219)
- Wildlife camera (Pi Cam Rev 1.3)
- Ultrasonic bat detection (mic TBD)
- Wind speed / anemometer (future)
- Data pipeline to yesteryearforever.xyz dashboard

================================================================================

"The cosmos is within us. We are made of star-stuff."
- Carl Sagan
