"""
Har bir metro yo'li uchun HTML sahifa yaratadi — bekatlar GORIZONTAL,
O'NGDAN CHAPGA tartibda joylashadi (birinchi bekat eng o'ngda). Bekatlar
orasida IKKITA poyezd — bir-biriga qarama-qarshi yo'nalishda — muntazam
harakatlanib turadi (taxminiy simulyatsiya).

DIQQAT: bu HAQIQIY GPS ma'lumoti EMAS — Toshkent metrosining ochiq
real-vaqt API'si yo'q. Bu shunchaki ishonarli ko'rinishdagi simulyatsiya.
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
    padding: 20px 0 40px;
    overflow-x: hidden;
  }}
  h1 {{
    font-size: 20px;
    margin: 0 0 4px;
    padding: 0 16px;
  }}
  .subtitle {{
    color: var(--tg-theme-hint-color, #8a8f98);
    font-size: 13px;
    margin-bottom: 12px;
    padding: 0 16px;
  }}
  .scroll-hint {{
    font-size: 11px;
    color: var(--tg-theme-hint-color, #8a8f98);
    padding: 0 16px 16px;
  }}
  .line-scroll {{
    overflow-x: auto;
    padding: 50px 24px 30px;
    -webkit-overflow-scrolling: touch;
  }}
  .line-wrap {{
    position: relative;
    display: flex;
    flex-direction: row-reverse;
    align-items: flex-start;
    width: max-content;
  }}
  .line-track {{
    position: absolute;
    left: 0;
    right: 0;
    top: 8px;
    height: 4px;
    background: {color};
    border-radius: 2px;
    opacity: 0.3;
  }}
  .station {{
    position: relative;
    flex: 0 0 auto;
    width: 84px;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 0;
  }}
  .dot {{
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: {color};
    border: 3px solid var(--tg-theme-bg-color, #0f1115);
    z-index: 2;
    margin-bottom: 10px;
  }}
  .station-name {{
    font-size: 12px;
    font-weight: 500;
    text-align: center;
    line-height: 1.3;
    max-width: 80px;
  }}
  .train {{
    position: absolute;
    top: -22px;
    width: 26px;
    height: 26px;
    margin-left: -13px;
    border-radius: 8px;
    background: {color};
    box-shadow: 0 0 12px {color};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    transition: left 1.4s cubic-bezier(.4,0,.2,1);
    z-index: 3;
  }}
  #train-b {{ top: 34px; }}
  .footer-note {{
    margin-top: 20px;
    font-size: 12px;
    color: var(--tg-theme-hint-color, #8a8f98);
    line-height: 1.5;
    border-top: 1px solid rgba(128,128,128,0.2);
    padding: 16px 16px 0;
  }}
</style>
</head>
<body>
  <h1>🚇 {title}</h1>
  <div class="subtitle">Poyezdlar harakati (taxminiy simulyatsiya)</div>
  <div class="scroll-hint">⬅️ Bekatlarni ko'rish uchun suring</div>

  <div class="line-scroll" id="scrollBox">
    <div class="line-wrap" id="lineWrap">
      <div class="line-track"></div>
      <div class="train" id="train-a">🚈</div>
      <div class="train" id="train-b">🚈</div>
      {stations_html}
    </div>
  </div>

  <div class="footer-note">
    Bu animatsiya haqiqiy GPS ma'lumotlariga asoslanmagan — Toshkent metrosining
    ochiq real-vaqt kuzatuv tizimi mavjud emas. Bu faqat taxminiy vizual ko'rinish.
  </div>

<script>
  const tg = window.Telegram?.WebApp;
  if (tg) {{ tg.ready(); tg.expand(); }}

  const stations = document.querySelectorAll('.station');
  const trainA = document.getElementById('train-a');
  const trainB = document.getElementById('train-b');
  const scrollBox = document.getElementById('scrollBox');

  let idxA = 0, dirA = 1;
  let idxB = stations.length - 1, dirB = -1;

  function centerOf(el) {{
    return el.offsetLeft + el.offsetWidth / 2;
  }}

  function place(train, idx) {{
    train.style.left = centerOf(stations[idx]) + 'px';
  }}

  function stepA() {{
    place(trainA, idxA);
    idxA += dirA;
    if (idxA >= stations.length - 1) {{ dirA = -1; idxA = stations.length - 1; }}
    if (idxA <= 0) {{ dirA = 1; idxA = 0; }}
  }}

  function stepB() {{
    place(trainB, idxB);
    idxB += dirB;
    if (idxB >= stations.length - 1) {{ dirB = -1; idxB = stations.length - 1; }}
    if (idxB <= 0) {{ dirB = 1; idxB = 0; }}
  }}

  window.addEventListener('load', () => {{
    place(trainA, idxA);
    place(trainB, idxB);
    // O'ngdan boshlab ko'rsatish (birinchi bekat eng o'ngda)
    scrollBox.scrollLeft = scrollBox.scrollWidth;
    setInterval(stepA, 3000);
    setInterval(stepB, 3000);
  }});
</script>
</body>
</html>
"""


def render_line_page(title: str, color: str, stations: list[str]) -> str:
    """Berilgan yo'l uchun to'liq HTML sahifani qaytaradi (o'ngdan-chapga)."""
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
