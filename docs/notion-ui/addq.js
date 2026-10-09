async (page) => {
  const QS = __QS__;
  const log = [];
  const heading = async (txt) => page.evaluate((txt) => {
    const els = [...document.querySelectorAll('[contenteditable], div, span')].filter(e => e.childElementCount === 0 && e.textContent.trim() === txt && parseFloat(getComputedStyle(e).fontSize) > 18);
    const e = els[els.length - 1]; if (!e) return null;
    e.scrollIntoView({block: 'center'});
    let c = e; while (c && c.getBoundingClientRect().width < 500) c = c.parentElement;
    const b = e.getBoundingClientRect(), cb = c.getBoundingClientRect();
    return {x: b.x, y: b.y + b.height / 2, right: cb.right, top: cb.top};
  }, txt);
  const menuSwitch = async (label) => {
    const p = await page.evaluate((l) => { const m = [...document.querySelectorAll('[role=menuitem]')].find(e => e.textContent.trim() === l); if (!m) return null; const b = m.getBoundingClientRect(); return [b.right - 20, b.y + b.height / 2]; }, label);
    if (!p) return false; await page.mouse.click(p[0], p[1]); await page.waitForTimeout(600); return true;
  };
  for (const q of QS) {
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.mouse.click(1300, 800); await page.waitForTimeout(400);
    const plus = await page.evaluate(() => {
      const c = [...document.querySelectorAll('[role=button]')].map(e => ({t: e.textContent.trim(), b: e.getBoundingClientRect()})).filter(o => o.t === '' && o.b.width >= 28 && o.b.width <= 40 && o.b.x > 780 && o.b.x < 880 && o.b.y > 150).sort((a, b) => b.b.y - a.b.y);
      return c.length ? [c[0].b.x + c[0].b.width / 2, c[0].b.y + c[0].b.height / 2] : null;
    });
    if (!plus) { log.push('noplus ' + q.prop); break; }
    await page.mouse.click(plus[0], plus[1]); await page.waitForTimeout(1000);
    const findItem = () => page.evaluate((prop) => { const m = [...document.querySelectorAll('[role=menuitem]')].find(e => e.textContent.trim().startsWith(prop) && e.textContent.trim() !== prop && !e.textContent.trim().startsWith(prop + ' ')); if (!m) return null; m.scrollIntoView({block: 'center'}); const b = m.getBoundingClientRect(); return [b.x + b.width / 2, b.y + b.height / 2]; }, q.prop);
    let item = await findItem();
    if (!item) {
      const more = await page.evaluate(() => { const m = [...document.querySelectorAll('[role=menuitem]')].find(e => e.textContent.trim().startsWith('Afficher ')); if (!m) return null; const b = m.getBoundingClientRect(); return [b.x + b.width / 2, b.y + b.height / 2]; });
      if (more) { await page.mouse.click(more[0], more[1]); await page.waitForTimeout(800); item = await findItem(); await page.waitForTimeout(300); item = await findItem(); }
    }
    if (!item) { log.push('noitem ' + q.prop); await page.keyboard.press('Escape'); continue; }
    await page.mouse.click(item[0], item[1]); await page.waitForTimeout(1300);
    await page.mouse.click(1300, 800); await page.waitForTimeout(400);
    let h = await heading(q.prop);
    if (!h) { log.push('nohead ' + q.prop); continue; }
    await page.waitForTimeout(300); h = await heading(q.prop);
    if (q.name && q.name !== q.prop) {
      await page.mouse.click(h.x + 5, h.y); await page.waitForTimeout(300);
      await page.evaluate((txt) => { const els = [...document.querySelectorAll('[contenteditable], div, span')].filter(e => e.childElementCount === 0 && e.textContent.trim() === txt && parseFloat(getComputedStyle(e).fontSize) > 18); const e = els[els.length - 1]; const r = document.createRange(); r.selectNodeContents(e); const s = getSelection(); s.removeAllRanges(); s.addRange(r); }, q.prop);
      await page.keyboard.press('Backspace'); await page.keyboard.type(q.name); await page.waitForTimeout(500);
      await page.mouse.click(1300, 800); await page.waitForTimeout(400);
      h = await heading(q.name);
    }
    await page.mouse.move(h.x + 50, h.y); await page.waitForTimeout(400);
    await page.mouse.click(h.right - 23, h.top + 22); await page.waitForTimeout(900);
    if (q.req) log.push(q.prop + ' req ' + await menuSwitch('Obligatoire'));
    if (q.desc) log.push(q.prop + ' desc ' + await menuSwitch('Description'));
    await page.keyboard.press('Escape'); await page.waitForTimeout(500);
    if (q.desc) {
      h = await heading(q.name || q.prop);
      await page.mouse.click(h.x + 5, h.y + 34); await page.waitForTimeout(400);
      await page.keyboard.type(q.desc); await page.waitForTimeout(500);
      await page.mouse.click(1300, 800); await page.waitForTimeout(400);
    }
    log.push('ok ' + q.prop);
  }
  return log;
}
