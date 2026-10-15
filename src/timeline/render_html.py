"""Self-contained 1200×675 Canvas timeline renderer."""
from __future__ import annotations

import base64
import html
import json
from pathlib import Path

from .models import ScheduleDocument

CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 675


def build_render_model(doc: ScheduleDocument, featured_sequences: list[int] | None = None) -> dict:
    all_rows = [
        {
            "seq": m.seq, "dateText": m.date_text,
            "startDate": m.start_date.isoformat(),
            "endDate": m.end_date.isoformat() if m.end_date else None,
            "owner": m.owner, "group": m.group, "description": m.description,
            "sourcePage": m.source_page,
        }
        for m in doc.sorted_milestones()
    ]
    selected = ([m for m in all_rows if m["seq"] in set(featured_sequences)]
                if featured_sequences is not None else all_rows)
    return {
        "title": doc.title or f"ปฏิทินงบประมาณ พ.ศ. {doc.fiscal_year_be}",
        "fiscalYearBE": doc.fiscal_year_be,
        "canvas": {"width": CANVAS_WIDTH, "height": CANVAS_HEIGHT},
        "milestones": selected, "allMilestones": all_rows,
    }


_HTML_TEMPLATE = '''<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
@font-face{font-family:"Sarabun Embedded";src:url(data:font/ttf;base64,__FONT_REGULAR__) format("truetype");font-weight:400}
@font-face{font-family:"Sarabun Embedded";src:url(data:font/ttf;base64,__FONT_BOLD__) format("truetype");font-weight:700}
html,body{margin:0;min-height:100%;background:#e8e3df}
body{display:grid;place-items:center;font-family:"Sarabun Embedded",Thonburi,Tahoma,sans-serif}
canvas{display:block;width:min(100vw,1200px);height:auto;background:#f6f2ef;box-shadow:0 8px 32px #19305224}
</style></head><body>
<canvas id="timeline" width="1200" height="675" role="img" aria-label="__TITLE__">เบราว์เซอร์นี้ไม่รองรับ Canvas</canvas>
<script>
const DATA=__DATA__;
const canvas=document.getElementById('timeline'),ctx=canvas.getContext('2d');
const W=1200,H=675,font='"Sarabun Embedded", Thonburi, Tahoma, sans-serif';
const C={bg:'#f6f2ef',navy:'#2e4b80',ink:'#292b32',muted:'#65616a',axis:'#a59e9b',review:'#b59682',prepare:'#605a67',approve:'#a7333b'};
function arabicDigits(value){return String(value).replace(/[๐-๙]/g,d=>String(d.charCodeAt(0)-0x0E50))}
function txt(s,x,y,size=13,color=C.ink,weight='normal',align='left',maxWidth=1200){
  ctx.font=weight+' '+size+'px '+font;ctx.fillStyle=color;ctx.textAlign=align;
  ctx.fillText(arabicDigits(s),x,y,maxWidth);
}
function rect(x,y,w,h,r,color){ctx.fillStyle=color;ctx.beginPath();ctx.roundRect(x,y,w,h,r);ctx.fill()}
function lines(value,width,size,maxLines){
  ctx.font=size+'px '+font;
  const parts=[...new Intl.Segmenter('th',{granularity:'word'}).segment(arabicDigits(value))].map(x=>x.segment);
  const out=[];let line='';
  for(const part of parts){const next=line+part;if(ctx.measureText(next).width<=width||!line)line=next;
    else{out.push(line.trim());line=part.trimStart()}}
  if(line)out.push(line.trim());
  if(out.length>maxLines){out.length=maxLines;let last=out[maxLines-1];
    while(last&&ctx.measureText(last+'…').width>width)last=last.slice(0,-1);
    out[maxLines-1]=last+'…'}
  return out;
}
function phase(group){return group.includes('อนุมัติ')?C.approve:group.includes('จัดทำ')?C.prepare:C.review}
function header(){
  ctx.fillStyle=C.navy;ctx.fillRect(0,0,W,70);
  ctx.strokeStyle='#ddc7a7';ctx.lineWidth=2;ctx.beginPath();ctx.arc(38,35,25,0,Math.PI*2);ctx.stroke();
  txt('งป.',38,41,15,'#eedcc3','bold','center');
  txt(DATA.title,W/2,46,30,'#fff','normal','center',1050);
  [[125,C.review,'ทบทวนและวางแผน'],[497,C.prepare,'จัดทำงบประมาณ'],[918,C.approve,'อนุมัติงบประมาณ']]
    .forEach(([x,c,label])=>{rect(x,84,14,14,7,c);txt(label,x+24,96,14,c,'bold')});
}
function axis(){
  const labels=['ต.ค. ๖๘','พ.ย. ๖๘','ธ.ค. ๖๘','ม.ค. ๖๙','ก.พ. ๖๙','มี.ค. ๖๙',
    'เม.ย. ๖๙','พ.ค. ๖๙','มิ.ย. ๖๙','ก.ค. ๖๙','ส.ค. ๖๙','ก.ย. ๖๙','ต.ค. ๖๙','พ.ย. ๖๙','ธ.ค. ๖๙'];
  const left=24,width=(W-48)/labels.length;
  labels.forEach((label,i)=>{const x=left+i*width;ctx.fillStyle=C.axis;ctx.fillRect(x,338,width-2,35);
    txt(label,x+width/2,361,11,'#fff','bold','center',width-5)});
}
function card(m,i){
  const isOdd=m.seq%2===1;
  const sameSide=DATA.milestones.filter(item=>(item.seq%2===1)===isOdd)
    .sort((a,b)=>a.seq-b.seq);
  const rank=sameSide.findIndex(item=>item.seq===m.seq);
  const cx=95+rank*1010/Math.max(sameSide.length-1,1);
  const lane=(isOdd?0:2)+rank%2,top=[111,220,387,501][lane],h=100,w=174;
  const x=Math.max(5,Math.min(W-w-5,cx-w/2)),color=phase(m.group);
  ctx.strokeStyle=color;ctx.lineWidth=1.4;ctx.beginPath();
  ctx.moveTo(cx,lane<2?338:373);ctx.lineTo(cx,lane<2?top+h:top);ctx.stroke();
  rect(x,top,w,h,6,'#ffffffea');rect(x,top,w,24,6,color+'30');
  rect(x-5,top-1,29,29,15,color);txt(m.seq,x+9.5,top+19,15,'#fff','bold','center');
  txt(m.dateText,x+33,top+17,12,color,'bold','left',w-39);
  const owners=lines(m.owner,w-12,11,2);
  owners.forEach((line,j)=>txt(line,x+6,top+40+j*13,11,C.ink,'bold','left',w-12));
  const y=top+43+owners.length*13;
  lines(m.description,w-12,10.5,3).forEach((line,j)=>txt(line,x+6,y+j*13,10.5,C.muted,'normal','left',w-12));
}
function draw(){
  ctx.fillStyle=C.bg;ctx.fillRect(0,0,W,H);header();axis();DATA.milestones.forEach(card);
  txt('แสดง '+DATA.milestones.length+' เหตุการณ์สำคัญจาก '+DATA.allMilestones.length+' ลำดับ • ข้อมูลจาก PDF ต้นฉบับ พ.ศ. '+DATA.fiscalYearBE,
      25,650,12,C.muted);
  txt('เลขคี่ด้านบน • เลขคู่ด้านล่าง • ตำแหน่งไม่ใช่มาตราส่วนเวลา',1175,650,11,C.muted,'normal','right');
}
if(ctx)Promise.all([
  document.fonts.load('16px "Sarabun Embedded"'),
  document.fonts.load('bold 16px "Sarabun Embedded"')
]).then(draw,draw);
</script></body></html>'''


def render_html(model: dict) -> str:
    safe_data = json.dumps(model, ensure_ascii=False).replace("<", "\\u003c")
    font_dir = Path(__file__).with_name("fonts")
    regular = base64.b64encode((font_dir / "Sarabun-Regular.ttf").read_bytes()).decode("ascii")
    bold = base64.b64encode((font_dir / "Sarabun-Bold.ttf").read_bytes()).decode("ascii")
    return (_HTML_TEMPLATE.replace("__TITLE__", html.escape(model["title"]))
            .replace("__DATA__", safe_data)
            .replace("__FONT_REGULAR__", regular)
            .replace("__FONT_BOLD__", bold))
