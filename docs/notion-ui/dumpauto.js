async (page) => {
  const NAMES = __NAMES__;
  const out = {};
  const openPanel = async () => {
    const has = await page.evaluate(() => !!document.querySelector('input[placeholder^="Rechercher des automatisations"]'));
    if (has) return;
    const pos = await page.evaluate(() => { const b = [...document.querySelectorAll('[role=button]')].find(e => /Automatisations/.test(e.getAttribute('aria-label') || '')); const r = b.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; });
    await page.mouse.click(pos[0], pos[1]); await page.waitForTimeout(1500);
  };
  for (const name of NAMES) {
    await openPanel();
    const inp = page.locator('input[placeholder^="Rechercher des automatisations"]');
    await inp.fill(name); await page.waitForTimeout(1000);
    const pos = await page.evaluate(() => { const i = document.querySelector('input[placeholder^="Rechercher des automatisations"]'); const r = i.getBoundingClientRect(); return [r.x + r.width / 2, r.y + 118]; });
    if (!pos) { out[name] = 'NOTFOUND'; continue; }
    await page.mouse.click(pos[0], pos[1]); await page.waitForTimeout(2500);
    out[name] = await page.evaluate(() => [...document.querySelectorAll('[contenteditable=true]')].filter(e => e.closest('[role=dialog]') || e.closest('.notion-overlay-container') || true).map(e => e.innerText).filter(t => t && t.length > 0).join('\n---\n'));
    await page.keyboard.press('Escape'); await page.waitForTimeout(800);
  }
  return out;
}
