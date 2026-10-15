const fs=require('node:fs');
const path=require('node:path');
const {test,expect}=require('@playwright/test');
const URL='/mockups/facebook-reels-studio-v2.html';
const go=async(page,n)=>page.locator('.sidebar .nav button').nth(n).click();
const quick=async page=>{await go(page,3);await page.getByRole('button',{name:'Tiếp',exact:true}).click();};
const order=async(page,kind)=>page.evaluate(kind=>listData(kind).rows.map(x=>({id:x.id,date:kind==='activity'?x.scheduledAt:(x.createdAt||x.postedAt),createdAt:x.createdAt,filename:x.filename})),kind);
test.beforeEach(async({page})=>{await page.goto(URL);await page.evaluate(()=>{state.nowOverride=Date.parse('2026-10-15T09:00:00Z');});});
test('QP-01 all 45 ACTIVE Pages discoverable among complete 50',async({page})=>{
 await quick(page);
 await expect(page.locator('.quick-page-row')).toHaveCount(50);
 await expect(page.locator('.quick-page-row input[type=checkbox]:not(:disabled)')).toHaveCount(45);
 await expect(page.getByText('Đã chọn 2 / 45 Pages ACTIVE')).toBeVisible();
});
test('QP-02/03 p50 searchable via real UI and creates precisely one target',async({page})=>{
 await quick(page);
 await page.getByLabel('Tìm Page Quick').fill('p50');
 await expect(page.locator('.quick-page-row')).toHaveCount(1);
 await page.getByLabel('Chọn Page p50').check();
 await expect(page.getByText('Đã chọn 3 / 45 Pages ACTIVE')).toBeVisible();
 expect(await page.evaluate(()=>state.targets.filter(t=>t.pageId==='p50').length)).toBe(1);
 await page.getByRole('button',{name:/Review 3 target/}).click();
 await expect(page.getByLabel('Page quick:a2:p50')).toBeDisabled();
});
test('QP-04/05/06 hidden selections persist across filters, clearing and deselection',async({page})=>{
 await quick(page);await page.getByLabel('Tìm Page Quick').fill('p50');
 await page.getByLabel('Chọn Page p50').check();
 await page.getByLabel('Tìm Page Quick').fill('p40');
 expect(await page.evaluate(()=>state.composerPages.includes('p50'))).toBe(true);
 await page.getByLabel('Lọc trạng thái Page Quick').selectOption('unavailable');
 await expect(page.getByText('Đã chọn 3 / 45 Pages ACTIVE')).toBeVisible();
 await page.getByLabel('Lọc trạng thái Page Quick').selectOption('all');
 await page.getByLabel('Tìm Page Quick').fill('');
 await expect(page.locator('.quick-page-row')).toHaveCount(50);
 await expect(page.getByLabel('Chọn Page p50')).toBeChecked();
 await page.getByLabel('Chọn Page p50').uncheck();
 expect(await page.evaluate(()=>state.targets.map(t=>t.pageId).sort())).toEqual(['p2','p3']);
});
test('QP-07/08 bulk all 45 eligible with unauthorized disabled',async({page})=>{
 await quick(page);
 await page.getByLabel('Lọc trạng thái Page Quick').selectOption('eligible');
 await expect(page.locator('.quick-page-row')).toHaveCount(45);
 await page.getByRole('button',{name:'Chọn Pages ACTIVE đang lọc'}).click();
 await expect(page.getByText('Đã chọn 45 / 45 Pages ACTIVE')).toBeVisible();
 expect(await page.evaluate(()=>new Set(state.targets.map(t=>t.pageId)).size)).toBe(45);
 await page.getByLabel('Lọc trạng thái Page Quick').selectOption('unavailable');
 await expect(page.locator('.quick-page-row')).toHaveCount(5);
 await expect(page.locator('.quick-page-row input:disabled')).toHaveCount(5);
 await expect(page.getByRole('checkbox',{name:'Chọn Page p1',exact:true})).toBeDisabled();
 await expect(page.getByRole('checkbox',{name:'Chọn Page p20',exact:true})).toBeDisabled();
 await expect(page.getByText('Đã chọn 45 / 45 Pages ACTIVE')).toBeVisible();
});
test('QP-09/10 per target edits survive unrelated page selection, Quick identity immutable',async({page})=>{
 await quick(page);await page.getByRole('button',{name:/Review 2 target/}).click();
 await page.getByLabel('Caption quick:a2:p2').fill('copy must survive');
 await page.getByLabel('Title quick:a2:p2').fill('special title');
 await page.getByLabel('Schedule quick:a2:p2').fill('2026-10-21T19:30');
 await page.getByLabel('Schedule quick:a2:p2').press('Tab');
 await page.getByRole('button',{name:'Sửa assignments'}).click();
 await page.getByLabel('Tìm Page Quick').fill('p50');await page.getByLabel('Chọn Page p50').check();
 await page.getByRole('button',{name:/Review 3 target/}).click();
 await expect(page.getByLabel('Caption quick:a2:p2')).toHaveValue('copy must survive');
 await expect(page.getByLabel('Title quick:a2:p2')).toHaveValue('special title');
 await expect(page.getByLabel('Schedule quick:a2:p2')).toHaveValue('2026-10-21T19:30');
 await expect(page.getByLabel('Page quick:a2:p2')).toBeDisabled();
 expect(await page.evaluate(()=>state.targets.every(t=>state.composerPages.includes(t.pageId)))).toBe(true);
});
test('SORT-01/02/03 global Library newest, oldest, filename ordering across cursor',async({page})=>{
 await go(page,2);
 let first=await order(page,'library');expect(first[0].id).toBe('a1');
 await page.getByRole('button',{name:'Tiếp ›'}).click();let second=await order(page,'library');expect(second[0].id).toBe('a26');
 expect(Date.parse(first[24].date)).toBeGreaterThan(Date.parse(second[0].date));
 await page.getByLabel('Sắp xếp Library').selectOption('created_at_asc');
 first=await order(page,'library');expect(first[0].id).toBe('a10000');
 await page.getByRole('button',{name:'Tiếp ›'}).click();second=await order(page,'library');
 expect(Date.parse(first[24].date)).toBeLessThan(Date.parse(second[0].date));
 await page.getByLabel('Sắp xếp Library').selectOption('filename_asc');
 first=await order(page,'library');expect(first[0].filename).toBe('video-00000.mp4');
 await page.getByRole('button',{name:'Tiếp ›'}).click();second=await order(page,'library');
 expect(first[24].filename < second[0].filename).toBe(true);
 expect(new Set([...first,...second].map(x=>x.id)).size).toBe(50);
});
test('SORT-04/05 cursor reset, filters/search and IDs preserved on Library sort',async({page})=>{
 await go(page,2);
 await page.getByRole('button',{name:'Chọn trang hiện tại'}).click();
 await page.locator('#search').fill('Tập 0001');await expect(page.locator('.tbl tbody tr').first()).toBeVisible();
 await page.getByLabel('Sắp xếp Library').selectOption('filename_asc');
 expect(await page.evaluate(()=>({cursor:state.cursor,history:state.history.length,q:state.query,selected:state.selected.size}))).toMatchObject({cursor:0,history:0,q:'Tập 0001',selected:25});
});
test('SORT-06/07 Reel chronology global and metrics sorting disabled',async({page})=>{
 await go(page,5);const a=await order(page,'reels');
 await page.getByRole('button',{name:'Tiếp ›'}).click();const b=await order(page,'reels');
 expect(Date.parse(a[24].date)).toBeGreaterThan(Date.parse(b[0].date));
 await expect(page.getByLabel('Sắp xếp Reels')).toHaveValue('posted_at_desc');
 await expect(page.locator('select[aria-label="Sắp xếp Reels"] option[value="views_desc"]')).toHaveAttribute('disabled','');
 expect(await page.evaluate(()=>state.sortBy.reels)).toBe('posted_at_desc');
});
test('SORT-08/09 Activity chronological schedule and creation ordering across pages',async({page})=>{
 await go(page,7);let a=await order(page,'activity');await page.getByRole('button',{name:'Tiếp ›'}).click();let b=await order(page,'activity');
 expect(Date.parse(a[24].date)).toBeGreaterThan(Date.parse(b[0].date));
 await page.getByLabel('Sắp xếp Activity').selectOption('scheduled_at_asc');
 a=await order(page,'activity');await page.getByRole('button',{name:'Tiếp ›'}).click();b=await order(page,'activity');
 expect(Date.parse(a[24].date)).toBeLessThan(Date.parse(b[0].date));
 await page.getByLabel('Sắp xếp Activity').selectOption('created_at_desc');
 a=await order(page,'activity');await page.getByRole('button',{name:'Tiếp ›'}).click();b=await order(page,'activity');
 expect(Date.parse(a[24].createdAt)).toBeGreaterThan(Date.parse(b[0].createdAt));
 await expect(page.locator('.tbl thead')).toContainText('Đã tạo');
});
test('SORT-10/11/12 adjacent pages stable, unique IDs; incompatible sort never leaks',async({page})=>{
 await go(page,2);
 await page.getByLabel('Sắp xếp Library').selectOption('filename_asc');
 const start=await order(page,'library');await page.getByRole('button',{name:'Tiếp ›'}).click();const next=await order(page,'library');
 await page.getByRole('button',{name:'‹ Trước'}).click();expect(await order(page,'library')).toEqual(start);
 expect(new Set([...start,...next].map(x=>x.id)).size).toBe(50);
 await go(page,5);await expect(page.getByLabel('Sắp xếp Reels')).toHaveValue('posted_at_desc');
 await go(page,7);await page.getByLabel('Sắp xếp Activity').selectOption('scheduled_at_asc');
 await go(page,2);await expect(page.getByLabel('Sắp xếp Library')).toHaveValue('filename_asc');
 await go(page,7);await expect(page.getByLabel('Sắp xếp Activity')).toHaveValue('scheduled_at_asc');
});
test('NAV-01/02/03 Dashboard → Library → Reels → Back and Forward',async({page})=>{
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await go(page,2);await go(page,5);await page.goBack();
 await expect(page.locator('main h1')).toHaveText('Video Library');
 await expect(page.locator('.sidebar .nav button.active')).toHaveAttribute('aria-label','Video Library');
 await expect(page).toHaveURL(/#library$/);
 await page.goForward();await expect(page.locator('main h1')).toHaveText('Published Reels');
 await expect(page.locator('.sidebar .nav button.active')).toHaveAttribute('aria-label','Reels');
 expect(errors).toEqual([]);
});
test('NAV-04/05 direct hash and invalid hash fallback with replaceState',async({page})=>{
 await page.goto(URL+'#publish');await expect(page.locator('main h1')).toHaveText('Publish Composer');
 await page.goto(URL+'#bad-route');await expect(page.locator('main h1')).toHaveText('Tổng quan vận hành');
 await expect(page).toHaveURL(/#dashboard$/);
});
test('NAV-06 no duplicate same-route history and NAV-08 drawer closes on hash change',async({page})=>{
 await go(page,2);const before=await page.evaluate(()=>history.length);
 await go(page,2);await go(page,2);expect(await page.evaluate(()=>history.length)).toBe(before);
 await page.getByRole('button',{name:'Chi tiết'}).first().click();await expect(page.locator('[role=dialog]')).toBeVisible();
 await page.evaluate(()=>setScreen('reels'));await expect(page.locator('[role=dialog]')).toHaveCount(0);
 await expect(page.locator('.overlay')).toHaveCount(0);
});
test('NAV-07/09 Back Forward preserves actual unsent Publish drafts and all route state',async({page})=>{
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await quick(page);await page.getByLabel('Tìm Page Quick').fill('p50');await page.getByLabel('Chọn Page p50').check();
 await page.getByRole('button',{name:/Review 3 target/}).click();
 await page.getByLabel('Caption quick:a2:p50').fill('Saved despite history');
 await go(page,2);await page.goBack();
 await expect(page.locator('main h1')).toHaveText('Publish Composer');
 await expect(page.getByLabel('Caption quick:a2:p50')).toHaveValue('Saved despite history');
 await page.goForward();await expect(page.locator('main h1')).toHaveText('Video Library');
 await page.goBack();expect(await page.evaluate(()=>state.composerPages.includes('p50'))).toBe(true);
 expect(errors).toEqual([]);
});
test('VIS-01 seven targeted Chromium screenshots at 1440 and 1024',async({page})=>{
 const base='mockups/screenshots';fs.mkdirSync(base,{recursive:true});
 for(const [width,height] of [[1440,900],[1024,768]]){
  await page.setViewportSize({width,height});
  await quick(page);await page.screenshot({path:path.join(base,'quick-selector-'+width+'x'+height+'.png'),fullPage:false});
  await page.getByLabel('Tìm Page Quick').fill('p50');await page.getByLabel('Chọn Page p50').check();
  await page.screenshot({path:path.join(base,'quick-p50-'+width+'x'+height+'.png'),fullPage:false});
  await page.getByLabel('Tìm Page Quick').fill('');await page.getByRole('button',{name:'Chọn Pages ACTIVE đang lọc'}).click();
  await page.screenshot({path:path.join(base,'quick-45-pages-'+width+'x'+height+'.png'),fullPage:false});
  await go(page,2);await page.getByLabel('Sắp xếp Library').selectOption('filename_asc');
  await page.screenshot({path:path.join(base,'library-filename-sort-'+width+'x'+height+'.png'),fullPage:false});
  await go(page,5);await page.screenshot({path:path.join(base,'reels-sort-gated-'+width+'x'+height+'.png'),fullPage:false});
  await go(page,7);await page.getByLabel('Sắp xếp Activity').selectOption('scheduled_at_asc');
  await page.screenshot({path:path.join(base,'activity-schedule-sort-'+width+'x'+height+'.png'),fullPage:false});
  await go(page,2);await go(page,5);await page.goBack();await expect(page.locator('main h1')).toHaveText('Video Library');
  await page.screenshot({path:path.join(base,'back-restored-library-'+width+'x'+height+'.png'),fullPage:false});
  await page.goto(URL);
 }
});
