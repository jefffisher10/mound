import os
import json
from datetime import datetime

month = datetime.now().strftime('%Y-%m')
today = datetime.now().strftime('%Y-%m-%d')
data_file = f'/home/ramblinray/mound/data/{month}.txt'
output_file = '/home/ramblinray/mound/page/index.html'
json_path = '/home/ramblinray/mound/data/latest.json'
os.makedirs('/home/ramblinray/mound/page', exist_ok=True)
os.makedirs('/var/www/html/mound/data', exist_ok=True)

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
    "condition": "Rain" if rain == "Yes" else soil_moisture
}
with open(json_path, 'w') as f:
    json.dump(latest_data, f)

# -- Build archive list -----------------------------------
archive_dir = '/home/ramblinray/mound/graphs/archive'
archive_links = ''
try:
    files = sorted(os.listdir(archive_dir), reverse=True)
    for f in files:
        if f.endswith('.png'):
            date = f.replace('.png', '')
            archive_links += f'<li><a href="graphs/archive/{f}">{date}</a></li>\n'
except:
    archive_links = '<li>No archive yet.</li>'

# -- Build HTML -------------------------------------------
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta http-equiv="refresh" content="1800">
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

      <p>Central Ohio &nbsp;·&nbsp; updated every 30 minutes<br>
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
      </table>

      <hr style="border:none; border-top: 1px solid #ccc; margin: 1rem 0;">

      <p><strong>Today -- {today}</strong></p>

      <figure>
        <img src="graphs/today.png"
             alt="Today's sensor readings"
             style="width:100%; max-width:900px; display:block; margin: 0.5rem auto;">
        <figcaption>Six sensor channels -- updated every 30 minutes</figcaption>
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
        <figcaption>Latest image -- updated up to 5 times daily</figcaption>
      </figure>

      <hr style="border:none; border-top: 1px solid #ccc; margin: 1rem 0;">

      <p><strong>Daily Archive</strong></p>
      <ul style="list-style:none; padding:0;">
{archive_links}
      </ul>

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
