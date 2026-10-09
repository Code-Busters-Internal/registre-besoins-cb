async (page) => {
  // OPS : [{url, set:[[nomLigne, niveau]], invite:[[recherche, libelléÀCliquer]]}]
  const OPS = __OPS__;
  const res = [];
  async function openShare() {
    await page.getByRole('button', {name:/^(Share|Partager)$/}).first().click(); await page.waitForTimeout(2000);
  }
  for (const op of OPS) {
    await page.goto(op.url); await page.waitForTimeout(5000);
    for (const [name, level] of (op.set || [])) {
      await openShare();
      const dlg = page.locator('[role=dialog]').last();
      const row = dlg.getByText(name, {exact:true}).first();
      if (!(await row.count())) { res.push(`absent: ${name}`); await page.keyboard.press('Escape'); continue; }
      const rb = await row.boundingBox();
      const lv = dlg.getByText(/^(Accès complet|Modifications autorisées|Modifications de contenu autorisées|Commentaires autorisés|Lecture seule)$/);
      const n = await lv.count(); let best = null, d = 1e9;
      for (let i = 0; i < n; i++) { const b = await lv.nth(i).boundingBox(); if (b && b.y > rb.y - 25 && Math.abs(b.y - rb.y) < d) { d = Math.abs(b.y - rb.y); best = lv.nth(i); } }
      await best.click(); await page.waitForTimeout(1000);
      await page.getByText(level, {exact:true}).last().click(); await page.waitForTimeout(1500);
      const conf = page.getByRole('button', {name:/^(Supprimer|Remove|Confirmer)$/});
      if (level === 'Supprimer' && await conf.count()) { await conf.last().click(); await page.waitForTimeout(1200); }
      res.push(`set ${name} → ${level}`);
      await page.keyboard.press('Escape'); await page.waitForTimeout(800);
    }
    for (const [q, label] of (op.invite || [])) {
      await openShare();
      await page.locator('[role=dialog]').last().getByText(/^(Inviter|Invite)$/).first().click(); await page.waitForTimeout(1200);
      await page.getByPlaceholder(/Adresses e-mail|Email/).first().click(); await page.waitForTimeout(300);
      await page.keyboard.type(q); await page.waitForTimeout(2000);
      await page.getByText(label, {exact:true}).last().click(); await page.waitForTimeout(1200);
      const body = await page.locator('[role=dialog]').last().innerText();
      await page.getByRole('button', {name:/^(Inviter|Invite)$/}).last().click(); await page.waitForTimeout(2500);
      const ok = page.getByRole('button', {name:'OK', exact:true});
      if (await ok.count()) { await ok.last().click(); await page.waitForTimeout(1000); }
      res.push(`invite ${label}`);
      await page.keyboard.press('Escape'); await page.waitForTimeout(800);
    }
    await page.reload(); await page.waitForTimeout(4000); await openShare();
    res.push(op.url.slice(-8) + ': ' + (await page.locator('[role=dialog]').last().innerText()).replace(/\n/g,' | '));
    await page.keyboard.press('Escape');
  }
  return res;
}
