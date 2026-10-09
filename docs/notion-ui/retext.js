async (page) => {
  const REPS = __REPS__;
  const log = [];
  for (const r of REPS) {
    const pos = await page.evaluate((old) => {
      const norm = (t) => t.replace(/\s+/g, ' ').trim();
      const cands = [...document.querySelectorAll('[contenteditable=true]')].filter(e => norm(e.innerText) === norm(old));
      const e = cands[cands.length - 1];
      if (!e) return null;
      e.scrollIntoView({block: 'center'});
      const b = e.getBoundingClientRect();
      return [b.x + Math.min(30, b.width / 2), b.y + Math.min(12, b.height / 2)];
    }, r.old);
    if (!pos) { log.push('notfound: ' + r.old.slice(0, 40)); continue; }
    await page.waitForTimeout(400);
    await page.mouse.click(pos[0], pos[1]); await page.waitForTimeout(400);
    await page.keyboard.press('Meta+a'); await page.waitForTimeout(200);
    await page.keyboard.type(r.new); await page.waitForTimeout(800);
    await page.mouse.click(1150, 600); await page.waitForTimeout(1200);
    log.push('ok: ' + r.new.slice(0, 40));
  }
  return log;
}
