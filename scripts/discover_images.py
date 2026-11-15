#!/usr/bin/env python3
"""Discover exhibition image candidates from source pages. Never auto-publish unlicensed images."""
import json, re, html, urllib.request, urllib.parse, pathlib, datetime
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.meta=[];self.images=[];self.title='';self.in_title=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='title':self.in_title=True
        if tag=='meta':
            key=(a.get('property') or a.get('name') or '').lower()
            if key in ('og:image','twitter:image','og:title','description','og:description'):self.meta.append((key,a.get('content','')))
        if tag=='img':
            src=a.get('src') or a.get('data-src') or ''
            if src:self.images.append({'src':src,'alt':a.get('alt','')})
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
    def handle_data(self,data):
        if self.in_title:self.title+=data
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'EXPOParisResearchBot/1.0 (editorial image discovery; contact repository owner)','Accept':'text/html'})
    with urllib.request.urlopen(req,timeout=15) as res:
        if 'text/html' not in res.headers.get('Content-Type',''):return None
        return res.read(1500000).decode('utf-8','replace')
def tokens(s):
    return set(re.findall(r'[a-z]{4,}',html.unescape(s).lower()))
def run():
    items=json.loads((ROOT/'expos.json').read_text())
    output=[]
    for x in items:
        candidates=[];urls=[]
        for url in (x.get('sourceUrl'),x.get('venueUrl')):
            if url and url.startswith('https://') and url not in urls:urls.append(url)
        for url in urls:
            try:
                content=fetch(url)
                if not content:continue
                page=Page();page.feed(content)
                titles=[v for k,v in page.meta if k=='og:title']+[page.title]
                artist=tokens(x.get('artist',''));subject=tokens(x.get('title',''))
                pagewords=tokens(' '.join(titles))
                relevance=len((artist|subject)&pagewords)
                is_exhibition_page=relevance>=2 or (len(subject& pagewords)>=1 and len(artist&pagewords)>=1)
                if not is_exhibition_page:continue
                imgs=[{'src':v,'alt':'','type':k} for k,v in page.meta if k in ('og:image','twitter:image')]
                imgs+= [{'src':i['src'],'alt':i['alt'],'type':'inline'} for i in page.images[:20]]
                for im in imgs:
                    src=urllib.parse.urljoin(url,html.unescape(im['src']))
                    if not src.startswith('https://'):continue
                    if src.lower().endswith(('.svg','.gif')):continue
                    alt_tokens=tokens(im['alt'])
                    score=relevance*2+len((artist|subject)&alt_tokens)*3+(5 if im['type']=='og:image' else 3 if im['type']=='twitter:image' else 0)
                    candidates.append({'url':src,'source_page':url,'alt':im['alt'][:250],'score':score,'rights':'unverified','approved':False})
            except Exception as exc:
                print('Skip',x['id'],url,type(exc).__name__)
        unique={c['url']:c for c in sorted(candidates,key=lambda c:-c['score'])}
        output.append({'id':x['id'],'title':x['title'],'venue':x['venue'],'candidates':list(unique.values())[:8]})
    result={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'notice':'Research candidates only. Rights and exact exhibition correspondence must be reviewed before publication.','exhibitions':output}
    (ROOT/'image-candidates.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Candidate groups:',sum(bool(x['candidates']) for x in output),'/',len(output))
if __name__=='__main__':run()
