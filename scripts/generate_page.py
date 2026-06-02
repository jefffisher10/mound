import os
from datetime import datetime

month = datetime.now().strftime('%Y-%m')
today = datetime.now().strftime('%Y-%m-%d')
data_file = f'/home/ramblinray/mound/data/{month}.txt'
output_file = '/home/ramblinray/mound/page/index.html'
os.makedirs('/home/ramblinray/mound/page', exist_ok=True)

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
temp = humidity = pressure = lux = soil_temp = soil_moisture = rain = voltage = current = 'N/A'
updated = 'N/A'

if latest:
    try:
        try:
    		temp = f"{float(parts[1]):.1f}°F"
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
    		lux = f"{max(0, lux_val):.0f} lux"
	except:
    		lux = 'Overload'

	try:
    		soil_temp = f"{float(parts[5]):.1f}°F"
	except:
    		soil_temp = 'N/A'

try:
    soil_moisture_raw = int(float(parts[6]))
    if soil_moisture_raw < 13000:
        soil_moisture = "Saturated"
    elif soil_moisture_raw < 15000:
        soil_moisture = "Moist"
    elif soil_moisture_raw < 17000:
        soil_moisture = "Moderate"
    else:
        soil_moisture = "Dry"
except:
    soil_moisture = 'N/A'

try:
    rain_val = int(float(parts[7]))
    rain = "Yes 🌧" if rain_val == 1 else "No"
except:
    rain = 'N/A'

try:
    voltage = f"{float(parts[8]):.2f}V"
except:
    voltage = 'N/A'

try:
    current = f"{float(parts[9]):.0f} mA"
except:
    current = 'N/A'

        # Soil moisture as descriptive
        if soil_moisture_raw < 13000:
            soil_moisture = "Saturated"
        elif soil_moisture_raw < 15000:
            soil_moisture = "Moist"
        elif soil_moisture_raw < 17000:
            soil_moisture = "Moderate"
        else:
            soil_moisture = "Dry"

    except:
        pass

# -- Build archive list -----------------------------------
archive_dir = '/var/www/html/mound/graphs/archive'
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
  <title>MOUND — Live Data | yesteryear forever</title>
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

      <p><strong>MOUND — Live Sensor Data</strong></p>

      <p>West Mound St., Columbus, Ohio &nbsp;·&nbsp; updated every 30 minutes<br>
      <a href="../sensing.html">? about this project</a></p>

      <hr style="border:none; border-top: 1px solid #ccc; margin: 1rem 0;">

      <p>
        <strong>Last reading:</strong> {updated}<br><br>
        ?? &nbsp;Air Temperature &nbsp;&nbsp;&nbsp;&nbsp; {temp}<br>
        ?? &nbsp;Humidity &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {humidity}<br>
        ?? &nbsp;Pressure &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {pressure}<br>
        ?? &nbsp;Light &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {lux}<br>
        ?? &nbsp;Soil Temperature &nbsp; {soil_temp}<br>
        ?? &nbsp;Soil Moisture &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {soil_moisture}<br>
        ?? &nbsp;Rain &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {rain}<br>
      </p>

      <hr style="border:none; border-top: 1px solid #ccc; margin: 1rem 0;">

      <p><strong>Today — {today}</strong></p>

      <figure>
        <img src="graphs/today.png"
             alt="Today's sensor readings"
             style="width:100%; max-width:900px; display:block; margin: 0.5rem auto;">
        <figcaption>Six sensor channels — updated every 30 minutes</figcaption>
      </figure>

      <hr style="border:none; border-top: 1px solid #ccc; margin: 1rem 0;">

      <p><strong>Last 7 Days</strong></p>

      <figure>
        <img src="graphs/7day.png"
             alt="Last 7 days of sensor readings"
             style="width:100%; max-width:900px; display:block; margin: 0.5rem auto;">
        <figcaption>Rolling 7-day view — updated nightly</figcaption>
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
