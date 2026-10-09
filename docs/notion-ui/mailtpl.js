async (page) => {
  const SUBJ = __SUBJ__; const BODY = __BODY__; const ANCHOR = __ANCHOR__;
  const dlg = page.locator('[role=dialog]').filter({hasText:'Envoyer un e-mail de'}).last();
  const eds = dlg.locator('[contenteditable=true]');
  async function insertVar(idx, prop) {
    if (prop === null) {
      await page.keyboard.type('@'); await page.waitForTimeout(800);
      await page.keyboard.type('Page de décl'); await page.waitForTimeout(1800);
      const hits = page.getByText('Page de déclenchement', {exact:true});
      const n = await hits.count(); let best = null, by = -1;
      for (let i = 0; i < n; i++) { const b = await hits.nth(i).boundingBox(); if (b && b.y > by) { by = b.y; best = b; } }
      await page.mouse.click(best.x + 20, best.y + best.height/2); await page.waitForTimeout(600); return;
    }
    await dlg.locator('[aria-label="Mentions"]').nth(idx).click(); await page.waitForTimeout(700);
    const row = page.getByRole('option').filter({hasText:'Page de déclenchement'}).first();
    const rb = await row.boundingBox();
    await page.mouse.click(rb.x + rb.width - 15, rb.y + rb.height/2); await page.waitForTimeout(700);
    const hdr = page.getByText('Propriété de Page de déclenchement', {exact:true}).last();
    const menu = hdr.locator(`xpath=ancestor::*[.//text()[normalize-space()="${ANCHOR}"]][1]`);
    const it = menu.getByText(prop, {exact:true}).first();
    await it.scrollIntoViewIfNeeded(); await it.click(); await page.waitForTimeout(500);
  }
  async function write(idx, segs) {
    const ed = eds.nth(idx);
    await ed.click(); await page.keyboard.press('Meta+A'); await page.keyboard.press('Backspace');
    for (const s of segs) {
      if (s === '\n') { await page.waitForTimeout(150); await page.keyboard.press('Shift+Enter'); await page.waitForTimeout(150); }
      else if (typeof s === 'string') { await page.keyboard.type(s); }
      else { await insertVar(idx, s.v); }
    }
  }
  await write(0, SUBJ); await write(1, BODY);
  const toks = await eds.nth(1).evaluate(e=>[...e.querySelectorAll('.notion-text-mention-token')].map(t=>(t.querySelector('svg')?.getAttribute('class')||'').split(' ')[0]+':'+t.innerText));
  return [await eds.nth(0).evaluate(e=>e.innerText), toks, await eds.nth(1).evaluate(e=>e.innerText)];
}
