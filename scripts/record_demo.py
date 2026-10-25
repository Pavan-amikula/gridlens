"""Record actual browser interactions and encode a portable recruiter demo."""
from pathlib import Path
import subprocess
import imageio_ffmpeg
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
scratch=ROOT/'work'/'video';scratch.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch()
    context=browser.new_context(viewport={'width':1440,'height':1080},record_video_dir=str(scratch),record_video_size={'width':1440,'height':1080})
    page=context.new_page()
    page.goto('http://127.0.0.1:8000')
    page.wait_for_function("document.getElementById('status').textContent==='STUDY COMPLETE'")
    page.evaluate("""()=>{let e=document.createElement('div');e.id='demo-caption';e.style='position:fixed;bottom:15px;left:290px;right:30px;background:#172b35;color:white;padding:15px 22px;font:14px Arial;z-index:1000;border-left:4px solid #b5522f;box-shadow:0 4px 20px #172b3522';document.body.appendChild(e)}""")
    def caption(text,ms=3000):
        page.locator('#demo-caption').evaluate('(e,text)=>e.textContent=text',text)
        page.wait_for_timeout(ms)
    caption('GridLens | 100 MW data-center interconnection screening. Actual local dashboard recording.')
    page.locator('#mitigation').select_option('baseline');page.locator('#run').click()
    page.wait_for_function("document.getElementById('status').textContent==='STUDY COMPLETE'")
    caption('Unmitigated: voltage dip, frequency event and a 30 MW AI load ramp reveal IT-supply and power-quality risks.',4000)
    page.locator('#mitigation').select_option('coordinated');page.locator('#run').click()
    page.wait_for_function("document.getElementById('status').textContent==='STUDY COMPLETE'")
    page.locator('#play').click()
    caption('Coordinated BESS + STATCOM + UPS + filter. Replay shows selected support against the same unmitigated event.',12500)
    page.locator('#national').scroll_into_view_if_needed()
    caption('IT continuity improves, but grid-demand recovery remains a risk. Study targets and national recovery checks are separate.',4500)
    page.evaluate('window.scrollTo(0,0)')
    page.get_by_role('button',name='02 Power quality').click()
    caption('Power quality: harmonic voltage from an assumed spectrum and network impedance. This is not an EMT resonance study.',4000)
    page.get_by_role('button',name='03 Control interactions').click()
    page.locator('#gain').fill('450');page.locator('#gain').dispatch_event('change')
    page.wait_for_function("document.getElementById('status').textContent==='STUDY COMPLETE'")
    caption('Controller interaction: inspect local-loop poles and damping. Full converter and PLL stability require licensed-tool validation.',4000)
    page.locator('#compare').click()
    page.wait_for_function("document.getElementById('status').textContent==='COMPARISON COMPLETE'",timeout=60000)
    caption('Compare all six architectures. PM100 measured HPC data informs loading sensitivity; grid disturbances remain synthetic.',6000)
    page.get_by_role('button',name='01 Transient response').click()
    caption('Reproduce the study, export CSV, inspect all results and read the model limits. PSCAD / PowerFactory / PSS/E exchange is documented.',4000)
    video=page.video
    context.close();path=Path(video.path());browser.close()
ff=imageio_ffmpeg.get_ffmpeg_exe()
dest=ROOT/'results'/'gridlens-demo.mp4'
subprocess.run([ff,'-y','-i',str(path),'-c:v','libx264','-preset','fast','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(dest)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
gif=ROOT/'results'/'demo-preview.gif'
subprocess.run([ff,'-y','-ss','12','-t','6','-i',str(dest),'-vf','fps=6,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse','-loop','0',str(gif)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
print('Actual interface recording:',dest,'bytes:',dest.stat().st_size)
