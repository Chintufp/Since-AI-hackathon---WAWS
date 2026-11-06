"""Record a local silent product rehearsal; never a finished submission or live-AI demo."""
import argparse,asyncio,hashlib,json,re,subprocess,time
from pathlib import Path
from urllib.parse import urlparse
from playwright.async_api import async_playwright


async def record(a):
    for url in [a.planner,a.operator]:
        u=urlparse(url)
        if u.scheme!='http' or u.hostname not in {'localhost','127.0.0.1'}:
            raise ValueError('LOCAL_HTTP_ONLY')
    if a.output.exists() or a.receipt.exists():raise ValueError('OUTPUT_ALREADY_EXISTS')
    if a.speed<=0:raise ValueError('INVALID_SPEED')
    allowed={urlparse(a.planner).netloc,urlparse(a.operator).netloc}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.receipt.parent.mkdir(parents=True,exist_ok=True)
    scenes=[];errors=[];blocked=[]
    async with async_playwright() as p:
        options={'headless':True}
        if Path('/usr/bin/chromium').exists():options['executable_path']='/usr/bin/chromium'
        browser=await p.chromium.launch(**options)
        context=await browser.new_context(viewport={'width':1366,'height':768},
            record_video_dir=str(a.output.parent/'capture'),record_video_size={'width':1366,'height':768})
        async def route(r):
            if urlparse(r.request.url).netloc in allowed:return await r.continue_()
            blocked.append(urlparse(r.request.url).netloc)
            await r.abort()
        await context.route('**/*',route)
        page=await context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        video=page.video
        planner=a.planner.rstrip('/')+'/?release=e1-aura-001&view=routes&band=06-09&map=schematic'
        await page.goto(planner,wait_until='networkidle')
        await page.get_by_text('files verified',exact=False).wait_for()
        assert await page.locator('.shortlist .value strong').all_text_contents()==['5,491','4,565','4,183']
        start=time.monotonic()
        # Leave ~15 seconds for initial navigation and encoder tail within the 120-second cap.
        async def at(seconds,name):
            await asyncio.sleep(max(0,seconds*0.9/a.speed-(time.monotonic()-start)))
            scenes.append({'scene':name,'elapsed_seconds':round(time.monotonic()-start,2)})
            print(json.dumps(scenes[-1]),flush=True)
        await at(0,'morning shortlist; schematic map')
        await at(8,'row-risk evidence')
        await page.get_by_role('button',name='Is it safe?',exact=True).click()
        await page.get_by_role('heading',name=re.compile('Sharing rows')).wait_for()
        await at(17,'before-and-after comparison')
        await page.locator('.compare').scroll_into_view_if_needed()
        await at(24,'private operator inventory')
        await page.goto(a.operator.rstrip('/')+'/operator.html',wait_until='networkidle')
        assert '48' in await page.locator('.kpis-op').first.inner_text()
        await at(31,'per-field handling')
        await page.get_by_role('heading',name=re.compile('What happens to each column')).scroll_into_view_if_needed()
        await at(40,'row sharing is not offered')
        await page.get_by_role('radio',name='A consultancy',exact=False).click()
        await page.get_by_text('UNSUPPORTED_SHARING_SCENARIO',exact=True).wait_for()
        await at(46,'aggregate alternative')
        await page.get_by_role('radio',name='Anyone: open demand statistics',exact=True).click()
        await at(48,'fixed release policy and pending review')
        await page.get_by_role('heading',name=re.compile('What gets published')).scroll_into_view_if_needed()
        await at(56,'published morning shortlist')
        await page.goto(planner,wait_until='networkidle')
        await page.get_by_text('files verified',exact=False).wait_for()
        await at(64,'offline preset, not a live model')
        await page.get_by_role('button',name='Busiest morning routes?',exact=True).click()
        await page.locator('.answer').scroll_into_view_if_needed()
        assert '5,491' in await page.locator('.answer').inner_text()
        await at(80,'night warning')
        await page.get_by_role('radio',name=re.compile('^Night')).click()
        await page.locator('.kpis').scroll_into_view_if_needed()
        assert 'No clear busiest route' in await page.locator('.kpis').inner_text()
        await at(92,'utility limitation')
        await page.get_by_role('button',name='Is it safe?',exact=True).click()
        await page.get_by_role('heading',name='How close are the numbers?',exact=True).evaluate("node => node.scrollIntoView({block: 'start'})")
        await at(100,'card-level privacy explanation')
        await page.get_by_role('heading',name=re.compile('What ε = 1 means')).scroll_into_view_if_needed()
        await at(108,'downloadable protected files')
        await page.get_by_role('button',name="What's shared",exact=True).click()
        await page.get_by_role('heading',name='Download exactly what was shared',exact=True).scroll_into_view_if_needed()
        await at(116,'end')
        await context.close();await video.save_as(str(a.output));await browser.close()
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(a.output)],text=True))
    duration=float(probe['format']['duration']);streams=probe['streams']
    assert not errors,errors
    assert not any(s['codec_type']=='audio' for s in streams)
    if a.speed==1:assert duration<=120,duration
    report={'application_commit':a.application_commit,'video_file':a.output.name,'video_sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),
            'duration_seconds':duration,'width':1366,'height':768,'speed':a.speed,'silent':True,
            'scope':'Actual local product rehearsal using synthetic data, schematic map and deterministic presets. Not a narrated final submission video.',
            'external_and_model_requests_blocked':True,'blocked_hosts':sorted(set(blocked)),
            'model_calls':0,'uploaded':False,'submitted':False,'scenes':scenes,'page_errors':errors}
    a.receipt.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'video':str(a.output),'duration':duration,'silent':True,'receipt':str(a.receipt)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--planner',required=True);p.add_argument('--operator',required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('--application-commit',required=True);p.add_argument('--speed',type=float,default=1,help='Rehearsal speed multiplier; use 1 for timed footage')
    asyncio.run(record(p.parse_args()))
