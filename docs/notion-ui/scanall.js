async (page) => {
  const out = [];
  const openPanel = async () => {
    const has = await page.evaluate(() => !!document.querySelector('input[placeholder^="Rechercher des automatisations"]'));
    if (has) return;
    const p = await page.evaluate(() => { const b = [...document.querySelectorAll('[role=button]')].find(e => /Automatisations/.test(e.getAttribute('aria-label') || '')); const r = b.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; });
    await page.mouse.click(p[0], p[1]); await page.waitForTimeout(1500);
  };
  await openPanel();
  const titles = await page.evaluate(() => { const inp = document.querySelector('input[placeholder^="Rechercher des automatisations"]'); let q = inp; for (let k = 0; k < 8 && q; k++) { q = q.parentElement; if (q.innerText.length > 200) break; } return q.innerText.split('\n').filter(l => l.trim() && !/^Quand |^Automatisations$|^Nouvelle automatisation$/.test(l.trim())); });
  for (const t of titles) {
    await openPanel();
    await page.locator('input[placeholder^="Rechercher des automatisations"]').fill(t); await page.waitForTimeout(1200);
    const pos = await page.evaluate(() => { const i = document.querySelector('input[placeholder^="Rechercher des automatisations"]'); const r = i.getBoundingClientRect(); return [r.x + r.width / 2, r.y + 118]; });
    await page.mouse.click(pos[0], pos[1]); await page.waitForTimeout(2500);
    const txt = await page.evaluate(() => [...document.querySelectorAll('[role=dialog] [contenteditable=true]')].map(e => e.innerText).join(' | '));
    const hits = (txt.match(/[^.\n|]*besoin[^.\n|]*/gi) || []);
    out.push(t + ' → ' + (hits.length ? hits.join(' ¶ ') : 'ok'));
    await page.keyboard.press('Escape'); await page.waitForTimeout(800);
  }
  return out;
}
