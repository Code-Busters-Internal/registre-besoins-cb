async (page) => {
  const TO = __TO__; const CC = __CC__; const FIRST = __FIRST__;
  await page.getByText(FIRST ? 'Nouvelle action' : 'Ajoutez une action', {exact:true}).last().click(); await page.waitForTimeout(800);
  await page.getByText('Envoyer un e-mail…', {exact:true}).click(); await page.waitForTimeout(1500);
  const dlg = page.locator('[role=dialog]').filter({hasText:'Envoyer un e-mail de'}).last();
  const pick = async (name) => { await page.waitForTimeout(600); const it = page.getByText(name, {exact:true}).last(); await it.scrollIntoViewIfNeeded(); await it.click(); await page.waitForTimeout(700); };
  const labelBox = (label) => page.evaluate((label) => { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n, best=null; while ((n = w.nextNode())) { if (n.data.trim() === label) { const rg = document.createRange(); rg.selectNode(n); const b = rg.getBoundingClientRect(); if (b.width) best = b.toJSON(); } } return best; }, label);
  let b = await labelBox('À');
  for (const n of TO) { await page.mouse.click(b.x + 150, b.y + 31); await page.waitForTimeout(500); await pick(n); await page.keyboard.press('Escape'); await page.waitForTimeout(400); }
  if (CC.length) {
    await dlg.getByText('CC/CCi', {exact:true}).click(); await page.waitForTimeout(800);
    for (const n of CC) { b = await labelBox('CC'); await page.mouse.click(b.x + 150, b.y + 31); await page.waitForTimeout(500); await pick(n); await page.keyboard.press('Escape'); await page.waitForTimeout(400); }
  }
  const t = await dlg.innerText(); return t.slice(t.indexOf('\nÀ\n'), t.indexOf('Objet'));
}
