# MOUND
### Monitoring Outdoor Urban Naturalist Device
*A solar-powered backyard sensor observatory — Central Ohio*

Part of the Fisher project family alongside the Adena rover and Hopewell rockets.

---

## What is MOUND?

MOUND is a small autonomous outdoor sensor station built on a Raspberry Pi Zero W, powered by a solar panel and battery pack. It quietly monitors the backyard environment and logs data automatically every 30 minutes — a personal naturalist's field instrument inspired by unmanned space probes. Simple by design. The journey is the point.

Data is published automatically to [yesteryearforever.xyz/mound](https://yesteryearforever.xyz/mound/index.html)

---

## Hardware

| Component | Purpose | Interface |
|-----------|---------|-----------|
| Raspberry Pi Zero W (2017) | Outdoor node | — |
| BME280 | Temperature, humidity, barometric pressure | I2C 0x76 |
| TSL2591 | Light / lux sensor | I2C 0x29 |
| DS18B20 | Waterproof soil temperature probe | 1-Wire GPIO4 |
| Capacitive soil moisture sensor | Soil moisture | Analog via ADS1115 A0 |
| FC-37 rain sensor | Rain detection | Analog ADS1115 A1 + GPIO17 |
| ADS1115 | 16-bit 4-channel ADC | I2C 0x48 |
| INA219 | Battery/solar current and voltage monitor | I2C 0x40 |
| Raspberry Pi Camera Rev 1.3 | Photography | CSI ribbon |
| Waveshare Solar Power Manager (D) | Power management | — |
| Waveshare 6V 5W solar panel | Solar charging | — |
| 3x 18650 Li-ion cells | Battery storage | — |

---

## I2C Address Map

| Address | Device | Purpose |
|---------|--------|---------|
| 0x29 | TSL2591 | Light sensor |
| 0x40 | INA219 | Power monitor |
| 0x48 | ADS1115 | Analog to digital converter |
| 0x76 | BME280 | Temp / humidity / pressure |

---

## Directory Structure

```
~/mound/
├── README.md               — this file
├── SCRIPTS.txt             — script breakdown and documentation
├── scripts/
│   ├── log_sensors.py      — reads all sensors, logs to data file
│   ├── update_site.py      — master publisher, calls graph + page generation
│   ├── generate_graphs.py  — generates gnuplot graph PNGs
│   ├── generate_graphs.gp  — gnuplot script (written by generate_graphs.py)
│   ├── generate_page.py    — builds the HTML data page + latest.json
│   ├── camera.py           — captures keeper shots (4 per day)
│   └── tests/              — individual sensor test scripts
├── data/
│   ├── YYYY-MM.txt         — monthly sensor logs
│   ├── latest.json         — latest reading for website live teaser
│   └── errors.txt          — sensor and script error log
├── graphs/
│   ├── today.png           — current day graph
│   ├── 7day.png            — rolling 7 day graph
│   └── archive/            — daily archived graphs (YYYY-MM-DD.png)
└── images/
    ├── latest.jpg          — most recent keeper photo
    ├── dawn/               — dawn keeper shots (YYYY-MM-DD.jpg)
    ├── afternoon/          — afternoon keeper shots
    ├── dusk/               — dusk keeper shots
    └── midnight/           — midnight keeper shots
```

---

## Data Format

Monthly log files (`data/YYYY-MM.txt`):

```
# timestamp, temp_f, humidity_pct, pressure_hpa, lux, soil_temp_f, soil_moisture_raw, rain, voltage, current_ma
2026-06-01 00:00:02, 62.0, 59.5, 988.4, 123.2, 69.3, 16122, 0, 5.08, 212.4
```

| Field | Notes |
|-------|-------|
| lux = 99999 | Sensor overflow — too much direct sunlight |
| rain = 0 | Dry |
| rain = 1 | Rain detected |
| soil moisture | Lower = wetter, higher = dryer |

---

## Crontab

Runs every 30 minutes:

```
*/30 * * * * python /home/ramblinray/mound/scripts/log_sensors.py
*/30 * * * * python /home/ramblinray/mound/scripts/update_site.py
*/30 * * * * python /home/ramblinray/mound/scripts/camera.py
```

---

## Useful Commands

```bash
# Check latest readings
tail -5 ~/mound/data/2026-06.txt

# Check error log
cat ~/mound/data/errors.txt

# Run sensor script manually
python ~/mound/scripts/log_sensors.py

# Run full site update manually
python ~/mound/scripts/update_site.py

# Take a photo
rpicam-still --vflip --hflip -o ~/mound/test.jpg

# Check WiFi signal
iwconfig wlan0

# Check I2C devices
sudo i2cdetect -y 1

# Check crontab
crontab -l

# Check cron logs
journalctl -u cron --since "1 hour ago" | tail -30
```

---

## Planned / Future

- [ ] SPH0641LU4H-1 ultrasonic bat detection mic (ordered, en route)
- [ ] RTL-SDR radio telescope / hydrogen line detection
- [ ] Basement flood sensor
- [ ] Wind speed anemometer
- [ ] Timelapse video generation script
- [ ] Power diagnostics page (voltage/current data)
- [ ] sensing.html written content and photos

---

*"The cosmos is within us. We are made of star-stuff."*
*— Carl Sagan*
