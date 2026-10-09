async (page) => {
  const NAMES = __NAMES__;
  const LITERALS = [
    ["vient de déposer un besoin interne", "vient de proposer un projet"],
    ["a crée une demande de besoin interne:", "a proposé un projet :"],
  ];
  const log = [];
  const find = ([LITERALS, doSelect]) => {
    const re = /(B|b)esoin(s?)( internes?)?(?! de contributeurs)/;
    for (const e of document.querySelectorAll('[role=dialog] [contenteditable=true]')) {
      const w = document.createTreeWalker(e, NodeFilter.SHOW_TEXT); let n;
      while ((n = w.nextNode())) {
        if (n.parentElement.closest('[contenteditable=false]')) continue;
        let i = -1, len = 0, out = null;
        for (const [a, b] of LITERALS) { const k = n.data.indexOf(a); if (k >= 0) { i = k; len = a.length; out = b; break; } }
        if (i < 0) { const m = re.exec(n.data); if (m) { i = m.index; len = m[0].length; out = (m[1] === 'B' ? 'P' : 'p') + 'rojet' + m[2]; } }
        if (i < 0) continue;
        const rg = document.createRange(); rg.setStart(n, i); rg.setEnd(n, i + len);
        if (doSelect === true) { const s = getSelection(); s.removeAllRanges(); s.addRange(rg); return {out, sel: s.toString(), want: n.data.substr(i, len)}; }
        if (doSelect === 'scroll') { n.parentElement.scrollIntoView({block: 'center', behavior: 'instant'}); return {out}; }
        // Point de clic sûr dans le même éditeur : un caractère de texte réellement visible
        const w2 = document.createTreeWalker(e, NodeFilter.SHOW_TEXT); let t;
        while ((t = w2.nextNode())) {
          if (t.parentElement.closest('[contenteditable=false]') || !t.data.trim()) continue;
          for (let c = 0; c < t.data.length; c++) {
            if (!t.data[c].trim()) continue;
            const r2 = document.createRange(); r2.setStart(t, c); r2.setEnd(t, c + 1);
            const bb = r2.getClientRects()[0]; if (!bb) continue;
            const x = bb.left + bb.width / 2, y = bb.top + bb.height / 2;
            const hitEl = document.elementFromPoint(x, y);
            if (hitEl && e.contains(hitEl) && !hitEl.closest('[contenteditable=false]')) return {out, x, y};
          }
        }
        return {out, x: null};
      }
    }
    return null;
  };
  for (const name of NAMES) {
    const has = await page.evaluate(() => !!document.querySelector('input[placeholder^="Rechercher des automatisations"]'));
    if (!has) { const p = await page.evaluate(() => { const b = [...document.querySelectorAll('[role=button]')].find(e => /Automatisations/.test(e.getAttribute('aria-label') || '')); const r = b.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }); await page.mouse.click(p[0], p[1]); await page.waitForTimeout(1500); }
    await page.locator('input[placeholder^="Rechercher des automatisations"]').fill(name); await page.waitForTimeout(1200);
    const pos = await page.evaluate(() => { const i = document.querySelector('input[placeholder^="Rechercher des automatisations"]'); const r = i.getBoundingClientRect(); return [r.x + r.width / 2, r.y + 118]; });
    await page.mouse.click(pos[0], pos[1]); await page.waitForTimeout(3000);
    const nd = await page.evaluate(() => document.querySelectorAll('[role=dialog] [contenteditable=true]').length);
    if (!nd) { log.push(name + ' : pas de dialogue'); continue; }
    let count = 0, fails = 0;
    for (let guard = 0; guard < 30 && fails < 3; guard++) {
      const h = await page.evaluate(find, [LITERALS, 'scroll']);
      if (!h) break;
      await page.waitForTimeout(1000);
      const h2 = await page.evaluate(find, [LITERALS, false]);
      if (!h2 || h2.x === null) { fails++; log.push(name + ' : pas de point de clic'); continue; }
      await page.mouse.click(h2.x, h2.y); await page.waitForTimeout(900);
      const s = await page.evaluate(find, [LITERALS, true]);
      await page.waitForTimeout(500);
      if (!s || s.sel !== s.want) { fails++; log.push(name + ' : sélection ratée'); await page.waitForTimeout(1000); continue; }
      await page.keyboard.type(s.out); await page.waitForTimeout(1500); count++;
    }
    // Filet de sécurité : un « projet » collé en fin de champ (frappe partie au mauvais endroit)
    const TAIL = /([.:!?»”]|déclenchement |projet)projet\s*$/;
    const tails = [];
    for (let pass = 0; pass < 5; pass++) {
      const idx = await page.evaluate((src) => { const re = new RegExp(src); return [...document.querySelectorAll('[role=dialog] [contenteditable=true]')].findIndex(e => re.test(e.innerText)); }, TAIL.source);
      if (idx < 0) break;
      await page.evaluate((i) => { const e = [...document.querySelectorAll('[role=dialog] [contenteditable=true]')][i]; e.focus(); const r = document.createRange(); r.selectNodeContents(e); r.collapse(false); const s = getSelection(); s.removeAllRanges(); s.addRange(r); }, idx);
      await page.waitForTimeout(700);
      for (let k = 0; k < 6; k++) { await page.keyboard.press('Backspace'); await page.waitForTimeout(150); }
      await page.waitForTimeout(500);
      tails.push(idx); log.push(name + ' : « projet » parasite retiré du champ ' + idx);
    }
    if (count || tails.length) { await page.getByRole('button', { name: /^(Terminé|Enregistrer)$/ }).last().click(); await page.waitForTimeout(2500); }
    log.push(name + ' : ' + count + ' remplacement(s)');
    await page.keyboard.press('Escape'); await page.waitForTimeout(900);
    await page.keyboard.press('Escape'); await page.waitForTimeout(700);
  }
  return log;
}
