"""
Har bir metro yo'li uchun HTML sahifa yaratadi — bekatlar ro'yxati va
ular orasida "harakatlanadigan" poyezd animatsiyasi bilan.

DIQQAT: bu HAQIQIY GPS ma'lumoti EMAS — Toshkent metrosining ochiq
real-vaqt API'si yo'q. Bu shunchaki ishonarli ko'rinishdagi simulyatsiya:
poyezd belgisi bekatlar orasida muntazam ravishda oldinga-orqaga harakatlanadi.
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>{title}</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--tg-theme-bg-color, #0f1115);
    color: var(--tg-theme-text-color, #ffffff);
    padding: 20px 16px 40px;
  }}
  h1 {{
    font-size: 20px;
    margin: 0 0 4px;
  }}
  .subtitle {{
    color: var(--tg-theme-hint-color, #8a8f98);
    font-size: 13px;
    margin-bottom: 28px;
  }}
  .line-wrap {{
    position: relative;
    padding-left: 36px;
  }}
  .line-track {{
    position: absolute;
    left: 15px;
    top: 10px;
    bottom: 10px;
    width: 4px;
    background: {color};
    border-radius: 2px;
    opacity: 0.35;
  }}
  .station {{
    position: relative;
    padding: 14px 0;
    display: flex;
    align-items: center;
  }}
  .dot {{
    position: absolute;
    left: -36px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: {color};
    border: 3px solid var(--tg-theme-bg-color, #0f1115);
    z-index: 2;
  }}
  .station-name {{
    font-size: 15px;
    font-weight: 500;
  }}
  #train {{
    position: absolute;
    left: -42px;
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: {color};
    box-shadow: 0 0 12px {color};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    transition: top 1.4s cubic-bezier(.4,0,.2,1);
    z-index: 3;
  }}
  .footer-note {{
    margin-top: 32px;
    font-size: 12px;
    color: var(--tg-theme-hint-color, #8a8f98);
    line-height: 1.5;
    border-top: 1px solid rgba(128,128,128,0.2);
    padding-top: 16px;
  }}
</style>
</head>
<body>
  <h1>🚇 {title}</h1>
  <div class="subtitle">Poyezd harakati (taxminiy simulyatsiya)</div>

  <div class="line-wrap">
    <div class="line-track"></div>
    <div id="train">🚈</div>
    {stations_html}
  </div>

  <div class="footer-note">
    Bu animatsiya haqiqiy GPS ma'lumotlariga asoslanmagan — Toshkent metrosining
    ochiq real-vaqt kuzatuv tizimi mavjud emas. Bu faqat taxminiy vizual ko'rinish.
  </div>

<script>
  const tg = window.Telegram?.WebApp;
  if (tg) {{ tg.ready(); tg.expand(); }}

  const stations = document.querySelectorAll('.station');
  const train = document.getElementById('train');
  let index = 0;
  let direction = 1;

  function positionTrain() {{
    const el = stations[index];
    const top = el.offsetTop + el.offsetHeight / 2 - train.offsetHeight / 2;
    train.style.top = top + 'px';
  }}

  function step() {{
    positionTrain();
    index += direction;
    if (index >= stations.length - 1) {{ direction = -1; index = stations.length - 1; }}
    if (index <= 0) {{ direction = 1; index = 0; }}
  }}

  window.addEventListener('load', () => {{
    positionTrain();
    setInterval(step, 3000);
  }});
</script>
</body>
</html>
"""


def render_line_page(title: str, color: str, stations: list[str]) -> str:
    """Berilgan yo'l uchun to'liq HTML sahifani qaytaradi."""
    if not stations:
        stations_html = '<div class="station"><div class="station-name">Bekatlar hali kiritilmagan.</div></div>'
    else:
        stations_html = "\n".join(
            f'<div class="station"><div class="dot"></div>'
            f'<div class="station-name">{name}</div></div>'
            for name in stations
        )
    return PAGE_TEMPLATE.format(
        title=title, color=color, stations_html=stations_html
    )
