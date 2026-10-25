"""Exercise the real dashboard and capture a reviewable screenshot."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport={'width':1440,'height':1120},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8000')
    page.wait_for_function("document.getElementById('status').textContent==='STUDY COMPLETE'")
    page.screenshot(path=str(ROOT/'results'/'dashboard.png'),full_page=True)
    page.get_by_role('button',name='02 Power quality').click()
    assert page.locator('#harmonics').is_visible()
    page.get_by_role('button',name='03 Control interactions').click()
    assert 'Damping ratio' in page.locator('#mode-results').inner_text()
    page.locator('#gain').fill('450');page.locator('#gain').dispatch_event('change')
    page.wait_for_function("document.getElementById('status').textContent==='STUDY COMPLETE'")
    page.locator('#compare').click()
    page.wait_for_function("document.getElementById('status').textContent==='COMPARISON COMPLETE'",timeout=60000)
    assert page.locator('#comparison tbody tr').count()==6
    page.screenshot(path=str(ROOT/'results'/'comparison.png'),full_page=True)
    page.get_by_role('button',name='01 Transient response').click()
    with page.expect_download() as download:page.locator('#csv').click()
    assert download.value.suggested_filename=='gridlens-trace.csv'
    page.locator('#play').click();page.wait_for_timeout(700)
    assert float(page.locator('#timeline').input_value())<12
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path=str(ROOT/'results'/'mobile.png'),full_page=True)
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    assert not errors,errors
    browser.close()
print('Browser QA passed: run, tabs, gain, comparison, CSV, playback, mobile, zero JS errors')
