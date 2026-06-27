MOUND
Monitoring Outdoor Urban Naturalist Device
A backyard sensor observatory — Central Ohio
Part of the Fisher project family alongside the Adena rover and Hopewell rockets.

================================================================================

WHAT IS MOUND?
MOUND is a small autonomous outdoor sensor station built on a Raspberry Pi Zero W,
powered by a USB battery bank with solar trickle charging. It quietly monitors the
backyard environment and logs data automatically — a personal naturalist's field
instrument inspired by unmanned space probes. Simple by design. The journey is the point.

================================================================================

HARDWARE
- Raspberry Pi Zero W (2017) — outdoor node
- BME280 — temperature, humidity, barometric pressure (I2C 0x76)
- TSL2591 — light / lux sensor (I2C 0x29)
- DS18B20 — waterproof soil temperature probe (1-Wire GPIO4)
- Capacitive soil moisture sensor (analog via ADS1115 A0)
- FC-37 rain sensor (analog via ADS1115 A1, digital GPIO17)
- ADS1115 — 16-bit 4-channel analog to digital converter (I2C 0x48)
- INA219 — battery/solar current and voltage monitor (I2C 0x40)
- Raspberry Pi Camera Rev 1.3 (CSI ribbon)
- Waveshare Solar Power Manager (D) with 4x 18650 Li-ion cells
- Waveshare 6V 5W solar panel

================================================================================

NETWORK
MOUND Pi Zero W:  ramblinray@192.168.1.49
Indoor Pi (botpi): botpi@192.168.1.33
Website:          yesteryearforever.xyz
MOUND data page:  yesteryearforever.xyz/mound/index.html
MOUND story page: yesteryearforever.xyz/sensing.html

================================================================================

DIRECTORY STRUCTURE

~/mound/
    README.txt              — this file
    SCRIPTS.txt             — script breakdown and documentation
    scripts/
        log_sensors.py      — reads all sensors, logs to data file
        update_site.py      — master publisher, calls graph + page generation
        generate_graphs.py  — generates gnuplot graph PNGs
        generate_graphs.gp  — gnuplot script (written by generate_graphs.py)
        generate_page.py    — builds the HTML data page + latest.json
        camera.py           — captures current.jpg and keeper shots
        tests/              — individual sensor test scripts (retired)
    data/
        YYYY-MM.txt         — monthly sensor logs
        latest.json         — latest reading for sensing.html teaser
        errors.txt          — sensor and script error log
    graphs/
        today.png           — current day graph
        7day.png            — rolling 7 day graph
        archive/            — daily archived graphs YYYY-MM-DD.png
    images/
        current.jpg         — current camera view
        dawn/               — dawn keeper shots YYYY-MM-DD.jpg
        afternoon/          — afternoon keeper shots YYYY-MM-DD.jpg
        dusk/               — dusk keeper shots YYYY-MM-DD.jpg
        midnight/           — midnight keeper shots YYYY-MM-DD.jpg
    page/
        index.html          — generated HTML page (SCP'd to botpi)

================================================================================

DATA FORMAT (monthly log)
# timestamp, temp_f, humidity_pct, pressure_hpa, lux, soil_temp_f, soil_moisture_raw, rain, voltage, current_ma
2026-06-01 00:00:02, 62.0, 59.5, 988.4, -1.1, 69.3, 16122, 0, 5.08, 212.4

Lux value of 99999 = sensor overflow (too much direct sunlight)
Rain value: 0 = dry, 1 = rain detected
Soil moisture: lower = wetter, higher = dryer

================================================================================

CRONTAB (runs every 30 minutes)
*/30 * * * * python /home/ramblinray/mound/scripts/log_sensors.py
*/30 * * * * python /home/ramblinray/mound/scripts/update_site.py
*/30 * * * * python /home/ramblinray/mound/scripts/camera.py

================================================================================

USEFUL COMMANDS

Check latest readings:
    tail -5 ~/mound/data/2026-06.txt

Check error log:
    cat ~/mound/data/errors.txt

Run sensor script manually:
    python ~/mound/scripts/log_sensors.py

Run full site update manually:
    python ~/mound/scripts/update_site.py

Run camera manually:
    python ~/mound/scripts/camera.py

Take a photo:
    rpicam-still --vflip --hflip -o ~/mound/test.jpg

Check WiFi signal:
    iwconfig wlan0

Check I2C devices:
    sudo i2cdetect -y 1

Check crontab:
    crontab -l

Check cron logs:
    journalctl -u cron --since "1 hour ago" | tail -30

View cron jobs running:
    journalctl -u cron | tail -20

Static IP config:
    /etc/NetworkManager/system-connections/preconfigured.nmconnection

================================================================================

I2C ADDRESS MAP
0x29  TSL2591  light sensor
0x40  INA219   power monitor
0x48  ADS1115  analog to digital converter
0x76  BME280   temp / humidity / pressure

================================================================================

PLANNED / FUTURE
- SPH0641LU4H-1 ultrasonic bat detection mic (ordered, shipping from Japan)
- RTL-SDR radio telescope / hydrogen line detection
- Basement flood sensor (NodeMCU + capacitive sensor)
- Wind speed anemometer
- Timelapse video generation script
- Diagnostics page for voltage/current data
- sensing.html written content and photos

================================================================================

"The cosmos is within us. We are made of star-stuff."
— Carl Sagan
