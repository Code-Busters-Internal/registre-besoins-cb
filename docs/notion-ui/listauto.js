async (page) => {
  const pos = await page.evaluate(() => { const b = [...document.querySelectorAll('[role=button]')].find(e => /Automatisations/.test(e.getAttribute('aria-label') || '')); if (!b) return null; const r = b.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; });
  if (!pos) return 'no automation button';
  await page.mouse.click(pos[0], pos[1]); await page.waitForTimeout(1500);
  const names = await page.evaluate(() => [...document.querySelectorAll('[role=menuitem],[role=option]')].map(e => e.innerText.split('\n')[0].trim()).filter(Boolean));
  await page.keyboard.press('Escape');
  return names;
}
