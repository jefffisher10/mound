import os
import json
from datetime import datetime

month = datetime.now().strftime('%Y-%m')
today = datetime.now().strftime('%Y-%m-%d')
data_file = f'/home/ramblinray/mound/data/{month}.txt'
output_file = '/home/ramblinray/mound/page/data_archive.html'
json_path = '/home/ramblinray/mound/data/latest.json'
archive_page_dir = '/home/ramblinray/mound/page/archive'
os.makedirs('/home/ramblinray/mound/page', exist_ok=True)
os.makedirs(archive_page_dir, exist_ok=True)
os.makedirs('/var/www/html/mound/data', exist_ok=True)

MONTH_NAMES = {
    '01': 'January', '02': 'February', '03': 'March', '04': 'April',
    '05': 'May', '06': 'June', '07': 'July', '08': 'August',
    '09': 'September', '10': 'October', '11': 'November', '12': 'December'
}

# -- Get latest reading -----------------------------------
latest = None
try:
    with open(data_file, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            latest = line.strip()
except:
    pass

# -- Parse latest reading ---------------------------------
temp = humidity = pressure = lux = soil_temp = soil_moisture = rain = updated = 'N/A'
voltage = current_ma = 'N/A'

if latest:
    parts = latest.split(', ')
    updated = parts[0] if len(parts) > 0 else 'N/A'

    try:
        temp = f"{float(parts[1]):.1f} F"
    except:
        temp = 'N/A'

    try:
        humidity = f"{float(parts[2]):.1f}%"
    except:
        humidity = 'N/A'

    try:
        pressure = f"{float(parts[3]):.1f} hPa"
    except:
        pressure = 'N/A'

    try:
        lux_val = float(parts[4])
        if lux_val >= 99999:
            lux = 'Overload'
        else:
            lux = f"{max(0, lux_val):.0f} lux"
    except:
        lux = 'N/A'

    try:
        soil_temp = f"{float(parts[5]):.1f} F"
    except:
        soil_temp = 'N/A'

    try:
        raw = int(float(parts[6]))
        if raw < 13000:
            soil_moisture = "Saturated"
        elif raw < 15000:
            soil_moisture = "Moist"
        elif raw < 17000:
            soil_moisture = "Moderate"
        else:
            soil_moisture = "Dry"
    except:
        soil_moisture = 'N/A'

    try:
        rain = "Yes" if int(float(parts[7])) == 1 else "No"
    except:
        rain = 'N/A'

    try:
        voltage = f"{float(parts[8]):.2f} V"
    except:
        voltage = 'N/A'

    try:
        current_ma = f"{float(parts[9]):.1f} mA"
    except:
        current_ma = 'N/A'

# -- Write latest.json ------------------------------------
latest_data = {
    "updated": updated,
    "temp": temp,
    "humidity": humidity,
    "pressure": pressure,
    "lux": lux,
    "soil_temp": soil_temp,
    "soil_moisture": soil_moisture,
    "rain": rain,
    "voltage": voltage,
    "current_ma": current_ma,
    "condition": "Rain" if rain == "Yes" else soil_moisture
}
with open(json_path, 'w') as f:
    json.dump(latest_data, f)

# -- Build month-grouped archive pages ---------------------
archive_dir = '/home/ramblinray/mound/graphs/archive'
months = {}
try:
    files = sorted(os.listdir(archive_dir), reverse=True)
    for f in files:
        if f.endswith('.png'):
            date = f.replace('.png', '')
            ym = date[:7]  # YYYY-MM
            months.setdefault(ym, []).append(date)
except:
    pass

# Archive pages live two directories below site root (mound/archive/),
# so stylesheet, script, and nav links all need ../../ instead of the
# single ../ that mound/data_archive.html uses.
archive_topnav = """
  <nav id="topnav">
    <div id="topnav-inner">
      <a href="../../ABOUT.html">| about |</a>
      <span class="nav-sep">·</span>
      <a href="../../making.html">| making |</a>
      <span class="nav-sep">·</span>
      <a href="../../writing.html">| writing |</a>
      <span class="nav-sep">·</span>
      <a href="../../sensing.html">| sensing |</a>
      <span class="nav-sep">·</span>
      <button id="toggle-dark-mode">| dark mode |</button>
      <span class="nav-sep">·</span>
      <button onclick="goRandom()">| random |</button>
    </div>
  </nav>
"""

# -- archive/index.html: list of months --------------------
month_links = ''
for ym in sorted(months.keys(), reverse=True):
    y, m = ym.split('-')
    label = f"{MONTH_NAMES.get(m, m)} {y}"
    count = len(months[ym])
    month_links += f'<li><a href="{ym}.html">{label}</a> &nbsp;<span style="color:#999;">({count} day{"s" if count != 1 else ""})</span></li>\n'

if not month_links:
    month_links = '<li>No archive yet.</li>'

archive_index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>MOUND -- Archive | yesteryear forever</title>
  <link rel="stylesheet" href="../../style.css" />
  <script src="../../script.js" defer></script>
</head>
<body>
{archive_topnav}
  <div class="container">
    <h1><a href="../../index.html">| yesteryear forever |</a></h1>
    <blockquote>
      <p><strong>MOUND -- Archive</strong></p>
      <p><a href="../data_archive.html">&larr; back to live data</a></p>
      <hr style="border:none; border-top: 1px solid #ccc; margin: 1rem 0;">
      <p><strong>Browse by month</strong></p>
      <ul style="list-style:none; padding:0;">
{month_links}
      </ul>
    </blockquote>
  </div>

  <div class="lightbox" id="lightbox">
    <img id="lightbox-img" src="" alt="">
  </div>
</body>
</html>"""

with open(f'{archive_page_dir}/index.html', 'w') as f:
    f.write(archive_index_html)

# -- archive/YYYY-MM.html: one per month, daily links -------
for ym, dates in months.items():
    y, m = ym.split('-')
    label = f"{MONTH_NAMES.get(m, m)} {y}"
    day_links = ''
    for date in sorted(dates, reverse=True):
        day_links += f'<li><a href="../graphs/archive/{date}.png">{date}</a></li>\n'

    month_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>MOUND -- {label} Archive | yesteryear forever</title>
  <link rel="stylesheet" href="../../style.css" />
  <script src="../../script.js" defer></script>
</head>
<body>
{archive_topnav}
  <div class="container">
    <h1><a href="../../index.html">| yesteryear forever |</a></h1>
    <blockquote>
      <p><strong>MOUND -- {label}</strong></p>
      <p><a href="index.html">&larr; back to archive</a> &nbsp;·&nbsp; <a href="../data_archive.html">back to live data</a></p>
      <hr style="border:none; border-top: 1px solid #ccc; margin: 1rem 0;">
      <ul style="list-style:none; padding:0;">
{day_links}
      </ul>
    </blockquote>
  </div>

  <div class="lightbox" id="lightbox">
    <img id="lightbox-img" src="" alt="">
  </div>
</body>
</html>"""

    with open(f'{archive_page_dir}/{ym}.html', 'w') as f:
        f.write(month_html)

# -- Build main index HTML ---------------------------------
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta http-equiv="refresh" content="600">
  <title>MOUND -- Live Data | yesteryear forever</title>
  <link rel="stylesheet" href="../style.css" />
  <script src="../script.js" defer></script>
</head>
<body>

  <nav id="topnav">
    <div id="topnav-inner">
      <a href="../ABOUT.html">| about |</a>
      <span class="nav-sep">·</span>
      <a href="../making.html">| making |</a>
      <span class="nav-sep">·</span>
      <a href="../writing.html">| writing |</a>
      <span class="nav-sep">·</span>
      <a href="../sensing.html">| sensing |</a>
      <span class="nav-sep">·</span>
      <button id="toggle-dark-mode">| dark mode |</button>
      <span class="nav-sep">·</span>
      <button onclick="goRandom()">| random |</button>
    </div>
  </nav>

  <div class="container">
    <h1><a href="../index.html">| yesteryear forever |</a></h1>

    <blockquote>

      <p><strong>MOUND -- Live Sensor Data</strong></p>

      <p>Central Ohio &nbsp;·&nbsp; updated every 10 minutes<br>
      <a href="../sensing.html">&larr; about this project</a></p>

      <hr style="border:none; border-top: 1px solid #ccc; margin: 1rem 0;">

      <p><strong>Last reading:</strong> {updated}</p>

      <table style="border:none; border-collapse:collapse; font-family:inherit; font-size:inherit; color:inherit;">
        <tr><td style="padding: 0.2rem 1.5rem 0.2rem 0;">Air Temperature</td><td>{temp}</td></tr>
        <tr><td style="padding: 0.2rem 1.5rem 0.2rem 0;">Humidity</td><td>{humidity}</td></tr>
        <tr><td style="padding: 0.2rem 1.5rem 0.2rem 0;">Pressure</td><td>{pressure}</td></tr>
        <tr><td style="padding: 0.2rem 1.5rem 0.2rem 0;">Light</td><td>{lux}</td></tr>
        <tr><td style="padding: 0.2rem 1.5rem 0.2rem 0;">Soil Temperature</td><td>{soil_temp}</td></tr>
        <tr><td style="padding: 0.2rem 1.5rem 0.2rem 0;">Soil Moisture</td><td>{soil_moisture}</td></tr>
        <tr><td style="padding: 0.2rem 1.5rem 0.2rem 0;">Rain</td><td>{rain}</td></tr>
        <tr><td style="padding: 0.2rem 1.5rem 0.2rem 0;">Battery Voltage</td><td>{voltage}</td></tr>
        <tr><td style="padding: 0.2rem 1.5rem 0.2rem 0;">Battery Current</td><td>{current_ma}</td></tr>
      </table>

      <hr style="border:none; border-top: 1px solid #ccc; margin: 1rem 0;">

      <p><strong>Today -- {today}</strong></p>

      <figure>
        <img src="graphs/today.png"
             alt="Today's sensor readings"
             style="width:100%; max-width:900px; display:block; margin: 0.5rem auto;">
        <figcaption>Eight sensor channels -- updated every 10 minutes</figcaption>
      </figure>

      <hr style="border:none; border-top: 1px solid #ccc; margin: 1rem 0;">

      <p><strong>Last 7 Days</strong></p>

      <figure>
        <img src="graphs/7day.png"
             alt="Last 7 days of sensor readings"
             style="width:100%; max-width:900px; display:block; margin: 0.5rem auto;">
        <figcaption>Rolling 7-day view -- updated nightly</figcaption>
      </figure>

      <hr style="border:none; border-top: 1px solid #ccc; margin: 1rem 0;">

      <figure>
        <img src="images/latest.jpg"
             alt="Latest image from MOUND"
             style="width:100%; max-width:900px; display:block; margin: 0.5rem auto;">
        <figcaption>Live view -- updated every 30 minutes</figcaption>
      </figure>

      <hr style="border:none; border-top: 1px solid #ccc; margin: 1rem 0;">

      <p><strong>Archive</strong></p>
      <p><a href="archive/index.html">Browse the full daily archive by month &rarr;</a></p>

    </blockquote>

    <p style="font-size: 0.85rem; color: #999;">{today} · auto-generated</p>

  </div>

  <div class="lightbox" id="lightbox">
    <img id="lightbox-img" src="" alt="">
  </div>

</body>
</html>"""

with open(output_file, 'w') as f:
    f.write(html)

print("Page generated!")
