async (page) => {
  // Ouvre la carte d'automatisation dont la description contient KEY, puis MODE = 'dump' ou 'swap'
  const KEYS = __KEYS__;
  const MODE = '__MODE__';
  const out = {};
  for (const key of KEYS) {
    const has = await page.evaluate(() => !!document.querySelector('input[placeholder^="Rechercher des automatisations"]'));
    if (!has) { const p = await page.evaluate(() => { const b = [...document.querySelectorAll('[role=button]')].find(e => /Automatisations/.test(e.getAttribute('aria-label') || '')); const r = b.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }); await page.mouse.click(p[0], p[1]); await page.waitForTimeout(1500); }
    const pos = await page.evaluate((key) => { const els = [...document.querySelectorAll('div,span')].filter(e => e.textContent.includes(key)).sort((a, b) => a.textContent.length - b.textContent.length); const e = els[0]; if (!e) return null; e.scrollIntoView({block: 'center', behavior: 'instant'}); const r = e.getBoundingClientRect(); return [r.x + 20, r.y + r.height / 2]; }, key);
    if (!pos) { out[key] = 'NOTFOUND'; continue; }
    await page.waitForTimeout(500);
    await page.mouse.click(pos[0], pos[1]); await page.waitForTimeout(3000);
    out[key] = await page.evaluate(() => [...document.querySelectorAll('[role=dialog] [contenteditable=true]')].map(e => e.innerText).join('\n---\n'));
    await page.keyboard.press('Escape'); await page.waitForTimeout(900);
  }
  return out;
}
