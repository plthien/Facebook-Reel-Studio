// Playwright UI v2 regression suite. Design fixture only; never calls Meta.
const fs=require('node:fs');
const path=require('node:path');
const {test,expect}=require('@playwright/test');
const ROOT='/mockups/facebook-reels-studio-v2.html';
const SCREENS=['dashboard','pages','library','publish','calendar','reels','analytics','activity','settings'];
const nav=async(page,index)=>{await page.locator('.sidebar .nav button').nth(index).click();};
async function sample60(page){
 await nav(page,3);
 await page.getByRole('button',{name:/Nạp demo: 20 videos/}).click();
 await page.getByRole('button',{name:/Review 60 target/}).click();
}
test.beforeEach(async({page})=>{
 await page.goto(ROOT);
 await page.evaluate(()=>{state.nowOverride=Date.parse('2026-10-15T09:00:00Z');});
});
test('01 nine screens navigate and no uncaught JS error',async({page})=>{
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(let i=0;i<9;i++){await nav(page,i);await expect(page.locator('main h1')).toBeVisible();await expect(page).toHaveURL(new RegExp('#'+SCREENS[i]+'$'));}
 expect(errors).toEqual([]);
});
test('02 library list/grid and search empty-state',async({page})=>{
 await nav(page,2);await expect(page.locator('.tbl')).toBeVisible();
 await page.getByLabel('Chế độ hiển thị').selectOption('grid');await expect(page.locator('.vcard')).toHaveCount(25);
 await page.getByLabel('Chế độ hiển thị').selectOption('list');await expect(page.locator('.tbl tbody tr')).toHaveCount(25);
 await page.locator('#search').fill('NO_MATCH_VIDEO_ABC_123');await expect(page.getByText('Không có dữ liệu phù hợp')).toBeVisible();
});
test('03 cursor forward/back and selection across pages and filters',async({page})=>{
 await nav(page,2);await page.getByRole('button',{name:'Chọn trang hiện tại'}).click();
 await expect(page.getByText('Đã chọn 25 ID')).toBeVisible();
 await page.getByRole('button',{name:'Tiếp ›'}).click();await page.getByRole('button',{name:'Chọn trang hiện tại'}).click();
 await expect(page.getByText('Đã chọn 50 ID')).toBeVisible();
 await page.getByRole('button',{name:'‹ Trước'}).click();
 await expect(page.getByText('Đã chọn 50 ID')).toBeVisible();
 await page.locator('#search').fill('Chuyện công sở');await expect(page.getByText('Đã chọn 50 ID')).toBeVisible();
});
test('04 50 and 100 transfer fully; 105 blocked without truncation',async({page})=>{
 await nav(page,2);
 for(const n of [50,100,105]){
  await page.evaluate(n=>{state.selected=new Set(Array.from({length:n},(_,i)=>'a'+(i+1)));state.composerAssets=['a2'];state.transferError='';draw();},n);
  await page.getByRole('button',{name:'Tạo batch từ lựa chọn'}).click();
  if(n<=100){await expect(page.getByText('Video đang chọn: '+n,{exact:false})).toBeVisible();await page.evaluate(()=>setScreen('library'));}
  else{await expect(page.getByRole('alert')).toContainText('105 video');await expect(page.getByText('Đã chọn 105 ID')).toBeVisible();expect(await page.evaluate(()=>state.selected.size)).toBe(105);}
 }
});
test('05 Quick canonical Page selection, edits persist, no reassignment from Review',async({page})=>{
 await nav(page,3);await page.getByRole('button',{name:'Tiếp',exact:true}).click();
 await expect(page.locator('input[type=checkbox]:checked')).toHaveCount(2);
 await page.getByRole('button',{name:/Review 2 target/}).click();
 const pageField=page.getByLabel('Page quick:a2:p2');await expect(pageField).toBeDisabled();
 await page.getByLabel('Caption quick:a2:p2').fill('caption remembered');
 await page.getByLabel('Schedule quick:a2:p2').fill('2026-10-21T19:30');await page.getByLabel('Schedule quick:a2:p2').press('Tab');
 await page.getByRole('button',{name:'Sửa assignments'}).click();
 await page.getByRole('button',{name:/Review 2 target/}).click();
 await expect(page.getByLabel('Caption quick:a2:p2')).toHaveValue('caption remembered');
 await expect(page.getByLabel('Schedule quick:a2:p2')).toHaveValue('2026-10-21T19:30');
 expect(await page.evaluate(()=>state.composerPages.slice().sort().join(',')===state.targets.map(x=>x.pageId).sort().join(','))).toBe(true);
});
test('06 Quick add/remove Pages and switch mode without stale targets',async({page})=>{
 await nav(page,3);await page.getByRole('button',{name:'Tiếp',exact:true}).click();
 await page.evaluate(()=>toggleQuickPage('p4'));expect(await page.evaluate(()=>state.targets.length)).toBe(3);
 await page.evaluate(()=>toggleQuickPage('p3'));expect(await page.evaluate(()=>state.targets.length)).toBe(2);
 await page.getByRole('button',{name:'Quay lại'}).click();
 await page.getByRole('button',{name:'Batch Publish'}).click();expect(await page.evaluate(()=>state.targets.length)).toBe(0);
 await page.getByRole('button',{name:'Quick Publish'}).click();expect(await page.evaluate(()=>state.targets.every(x=>x.pageId===x.id.split(':').slice(-1)[0]))).toBe(true);
});
test('07 sample 20 assets / 10 Pages / exactly 60 targets all reviewed',async({page})=>{
 await sample60(page);
 await expect(page.locator('.kpi').filter({hasText:'Target jobs'})).toContainText('60');
 for(const [index,rows] of [[0,25],[1,25],[2,10]]){
  if(index)await page.getByRole('button',{name:'Tiếp',exact:true}).click();
  await expect(page.locator('.matrix tbody tr')).toHaveCount(rows);
 }
 await expect(page.getByText('Targets 51–60 / 60')).toBeVisible();
});
test('08 target 51 caption, title, schedule retained across pages and steps',async({page})=>{
 await sample60(page);
 await page.getByRole('button',{name:'Tiếp',exact:true}).click();await page.getByRole('button',{name:'Tiếp',exact:true}).click();
 await page.getByLabel('Caption target-00051').fill('Long caption '.repeat(20));
 await page.getByLabel('Title target-00051').fill('title over');
 await page.getByLabel('Schedule target-00051').fill('2026-10-22T19:30');await page.getByLabel('Schedule target-00051').press('Tab');
 await page.getByRole('button',{name:'Sửa assignments'}).click();
 await page.getByRole('button',{name:/Review 60 target/}).click();
 await page.getByRole('button',{name:'Tiếp',exact:true}).click();await page.getByRole('button',{name:'Tiếp',exact:true}).click();
 await expect(page.getByLabel('Caption target-00051')).toHaveValue('Long caption '.repeat(20));
 await expect(page.getByLabel('Title target-00051')).toHaveValue('title over');
 await expect(page.getByLabel('Schedule target-00051')).toHaveValue('2026-10-22T19:30');
});
test('09 strict schedule boundaries, bad calendar and UTC convert',async({page})=>{
 const v=await page.evaluate(()=>{
  const now=Date.parse('2026-10-15T09:00:00Z');
  return ['2020-01-01T09:00','2026-10-15T16:00','2026-10-15T16:05','2026-10-15T16:10','2026-02-30T09:00','2026-10-20T19:30','invalid'].map(s=>({s,v:validateSchedule(s,now,10)}));
 });
 expect(v.map(x=>x.v.errors[0]||'PASS')).toEqual(['SCHEDULE_IN_PAST','SCHEDULE_IN_PAST','SCHEDULE_TOO_SOON','PASS','SCHEDULE_INVALID','PASS','SCHEDULE_INVALID']);
 expect(v[5].v.utc).toBe('2026-10-20T12:30:00.000Z');
});
test('10 exact duplicate blocked, legitimate occurrences allowed, late-page duplicate',async({page})=>{
 await sample60(page);
 await page.evaluate(()=>{state.targets[59].assetId=state.targets[0].assetId;state.targets[59].pageId=state.targets[0].pageId;state.targets[59].localTime=state.targets[0].localTime;draw();});
 await expect(page.getByRole('button',{name:'Xác nhận intent (DEMO)'})).toBeDisabled();
 const result=await page.evaluate(()=>({last:checkTargets()[59].errors,total:counts(checkTargets()).invalid}));
 expect(result.last).toContain('DUPLICATE_INTENT');expect(result.total).toBe(1);
 await page.evaluate(()=>{state.targets[59].localTime='2026-10-21T19:30';draw();});
 expect(await page.evaluate(()=>counts(checkTargets()).invalid)).toBe(0);
});
test('11 invalid Page/media and 100 target limit',async({page})=>{
 await sample60(page);
 await page.evaluate(()=>{state.targets[20].pageId='p1';draw();});
 await expect(page.getByRole('button',{name:'Xác nhận intent (DEMO)'})).toBeDisabled();
 await page.evaluate(()=>{state.targets[20].pageId='p2';state.targets[20].assetId='a1';draw();});
 expect((await page.evaluate(()=>checkTargets()[20].errors)).join(',')).toContain('ASSET_INVALID');
 await page.evaluate(()=>{state.targets=[];for(let i=0;i<100;i++)state.targets.push(newTarget('a2','p2'));state.step=2;draw();});
 await page.getByRole('button',{name:'Thêm target'}).click();
 expect(await page.evaluate(()=>state.targets.length)).toBe(100);
 await expect(page.getByText('Giới hạn tối đa 100 target',{exact:false})).toBeVisible();
});
test('12 stale validated intent never confirms, demo never creates real jobs',async({page})=>{
 await sample60(page);await page.getByRole('button',{name:'Validate tất cả (demo)'}).click();
 const confirm=page.getByRole('button',{name:'Xác nhận intent (DEMO)'});
 await expect(confirm).toBeEnabled();
 await page.getByLabel('Caption target-00001').fill('Changed after preview');
 await expect(confirm).toBeDisabled();
 await page.evaluate(()=>confirmDemo());await expect(page.getByRole('status')).toContainText('DEMO BLOCKED');
 await page.getByRole('button',{name:'Validate tất cả (demo)'}).click();await page.getByRole('button',{name:'Xác nhận intent (DEMO)'}).click();
 await expect(page.getByRole('status')).toContainText('0 jobs');
});
test('13 409 and 422 error demos visible, settings includes 401/403/429/503',async({page})=>{
 await sample60(page);await page.getByRole('button',{name:'Mock API 409'}).click();await expect(page.getByRole('alert')).toContainText('409');
 await page.getByRole('button',{name:'Mock API 422'}).click();await expect(page.getByRole('alert')).toContainText('422');
 await nav(page,8);
 for(const label of ['401','403','409','422','429','503']){await page.getByRole('button',{name:new RegExp(label)}).click();await expect(page.getByRole('status')).toContainText(label);}
});
test('14 queue UNCERTAIN reconciliation has no blind retry',async({page})=>{
 await nav(page,7);await page.getByRole('button',{name:'Chi tiết'}).nth(4).click();
 await expect(page.locator('[role=dialog]')).toContainText('Không retry');await expect(page.locator('[role=dialog]')).not.toContainText('Retry ngay');
 await page.keyboard.press('Escape');await expect(page.locator('[role=dialog]')).toHaveCount(0);
});
test('15 Imported Reel unlinked; unavailable/zero distinct',async({page})=>{
 await nav(page,5);await expect(page.locator('tbody tr').first()).toContainText('Imported · asset chưa xác định');
 await expect(page.getByText('N/A',{exact:true}).first()).toBeVisible();
 await page.getByRole('button',{name:'Snapshot'}).first().click();await expect(page.locator('[role=dialog]')).toContainText('không liên kết asset tự động');
});
test('16 calendar modes read-only, no drag reschedule',async({page})=>{
 await nav(page,4);await expect(page.locator('table')).toBeVisible();
 await page.getByRole('button',{name:'WEEK'}).click();await expect(page.locator('.day')).toHaveCount(7);
 await page.getByRole('button',{name:'MONTH'}).click();await expect(page.locator('.day')).toHaveCount(28);
 await expect(page.getByText('PATCH reschedule = DEFER',{exact:false})).toBeVisible();
});
test('17 no app-level horizontal overflow on tablet/desktop; drawers scroll',async({page})=>{
 for(const width of [1440,1024]){await page.setViewportSize({width,height:width===1440?900:768});for(let i=0;i<9;i++){await nav(page,i);expect(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth+2)).toBe(true);}}
 await nav(page,2);await page.getByRole('button',{name:'Chi tiết'}).first().click();await expect(page.locator('.detail')).toHaveCSS('overflow-y','auto');
});
test('18 screenshot evidence: 9 views each at 2 resolutions + critical workflows',async({page})=>{
 const root='mockups/screenshots';fs.mkdirSync(root,{recursive:true});
 for(const [width,height] of [[1440,900],[1024,768]]){
  await page.setViewportSize({width,height});
  for(let i=0;i<9;i++){await nav(page,i);await page.screenshot({path:path.join(root,SCREENS[i]+'-'+width+'x'+height+'.png'),fullPage:true});}
 }
 await page.setViewportSize({width:1440,height:900});await nav(page,2);
 await page.getByLabel('Chế độ hiển thị').selectOption('grid');await page.screenshot({path:path.join(root,'library-grid.png'),fullPage:true});
 await sample60(page);await page.screenshot({path:path.join(root,'publish-review-60.png'),fullPage:true});
 await page.evaluate(()=>{state.targets[59].localTime='2020-01-01T09:00';draw();});await page.screenshot({path:path.join(root,'publish-invalid.png'),fullPage:true});
 await nav(page,5);await page.getByRole('button',{name:'Snapshot'}).first().click();await page.screenshot({path:path.join(root,'reel-detail.png'),fullPage:true});
 await page.keyboard.press('Escape');
 await nav(page,7);await page.getByRole('button',{name:'Chi tiết'}).nth(4).click();await page.screenshot({path:path.join(root,'uncertain-detail.png'),fullPage:true});
});
