async (page) => {
  const NAME = __NAME__; const TRIG = __TRIG__;
  const editorOpen = (await page.getByText('Nouveau déclencheur', {exact:true}).count()) > 0;
  if (!editorOpen && !(await page.getByText('Nouvelle automatisation', {exact:true}).count())) {
    const f = page.getByRole('button', {name:'Filtrer'}).first(); const fb = await f.boundingBox();
    await page.mouse.move(fb.x-40, fb.y+10); await page.waitForTimeout(500);
    await page.getByRole('button', {name:'Automatisations', exact:true}).first().click(); await page.waitForTimeout(1500);
  }
  if (!editorOpen) { await page.getByText('Nouvelle automatisation', {exact:true}).last().click(); await page.waitForTimeout(1500); }
  await page.mouse.click(510, 119); await page.waitForTimeout(300);
  await page.keyboard.press('Meta+A'); await page.keyboard.type(NAME); await page.keyboard.press('Enter'); await page.waitForTimeout(400);
  let first = true;
  for (const t of TRIG) {
    await page.getByText(first ? 'Nouveau déclencheur' : 'Ajoutez un déclencheur', {exact:true}).last().click(); await page.waitForTimeout(900);
    first = false;
    await page.keyboard.type(t.prop); await page.waitForTimeout(800);
    await page.getByText(t.prop, {exact:true}).last().click(); await page.waitForTimeout(900);
    const any = page.getByText('N’importe quelle option', {exact:true}).last(); const ab = await any.boundingBox();
    await page.mouse.click(ab.x - 18, ab.y + ab.height/2); await page.waitForTimeout(400);
    for (const v of t.values) { const o = page.getByText(v, {exact:true}).last(); await o.scrollIntoViewIfNeeded(); const ob = await o.boundingBox(); await page.mouse.click(ob.x - 24, ob.y + ob.height/2); await page.waitForTimeout(400); }
    await page.getByText('Terminé', {exact:true}).first().click(); await page.waitForTimeout(700);
  }
  return (await page.locator('[role=dialog]').last().innerText()).slice(0, 900);
}
