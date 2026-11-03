"""Experiment 1 through installed DSH, with an auditing loopback API gateway.

No target code is executed. Default is offline mock; --live makes four calls.
Credentials are read from the environment or Windows user environment, never logged.
"""
from pathlib import Path
import argparse, datetime, hashlib, http.server, json, os, re, subprocess, threading
import urllib.request, urllib.error

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / 'data/original/lm_understand-logs'
CLI = Path(os.environ['LOCALAPPDATA']) / 'Programs/DeepSeek Harness/resources/runtime/cli/bin/dsh.cmd'
SYSTEM = "Answer the user's request."
CASES = [('a9f535cc', 'breakout'), ('dfc6cb65', 'pong'), ('bdf99279', 'pacman'), ('0bbcc3ea', 'freeway')]

def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def text_blocks(value):
    if isinstance(value, str): return value
    return ''.join(x.get('text', '') for x in value or [] if x.get('type') == 'text')

def key_from_environment():
    value = os.environ.get('DEEPSEEK_API_KEY', '')
    if not value and os.name == 'nt':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as k:
                value = winreg.QueryValueEx(k, 'DEEPSEEK_API_KEY')[0]
        except FileNotFoundError: pass
    return value.strip()

def overlay(path, port, max_tokens):
    default = (ROOT / 'configs/dsh-headless-base.yml').read_text(encoding='utf-8-sig')
    ids = re.findall(r'^- id: (.+)$', default, re.M)
    keep = set('timer llm session typert agent agent-default-model jobs session-persistence-jsonl session-projection storage storage-json storage-domain session-projection-cache tools system-prompt agent-loop llm-deepseek headless-startup headless-runner'.split())
    rows = [f'- id: {i}\n  disabled: true\n' for i in ids if i not in keep]
    rows += [f'''- id: system-prompt
  config:
    includeHarnessIdentity: false
    includeRuntimeContext: false
    personaPrefix: "{SYSTEM}"
    personaSuffix: ""
- id: agent-default-model
  config:
    provider: deepseek-official
    model: deepseek-flash
- id: llm-deepseek
  config:
    baseURL: http://127.0.0.1:{port}
    thinking: enabled
    reasoningEffort: high
    maxTokens: {max_tokens}
    streamIdleTimeoutMs: 300000
    retryPolicy:
      mode: normal
      maxRetries: 0
    models:
      - id: deepseek-flash
        contextWindow: 1000000
        maxTokens: {max_tokens}
- id: session-persistence-jsonl
  config:
    compression: none
''']
    path.write_text('\n'.join(rows), encoding='utf-8')

def mock_events():
    message = {'id':'mock-exp1','type':'message','role':'assistant','model':'deepseek-flash','content':[], 'stop_reason':None,'stop_sequence':None,'usage':{'input_tokens':1,'output_tokens':0}}
    yield 'message_start', {'type':'message_start','message':message}
    for idx, kind, content in [(0,'thinking','MOCK reasoning; not a model result.'),(1,'text','Game: MOCK\nConfidence: 0%')]:
        yield 'content_block_start', {'type':'content_block_start','index':idx,'content_block':{'type':kind,kind:''}}
        yield 'content_block_delta', {'type':'content_block_delta','index':idx,'delta':{'type':kind+'_delta',kind:content}}
        yield 'content_block_stop', {'type':'content_block_stop','index':idx}
    yield 'message_delta', {'type':'message_delta','delta':{'stop_reason':'end_turn','stop_sequence':None},'usage':{'output_tokens':1}}
    yield 'message_stop', {'type':'message_stop'}

def parse_stream(path):
    reasoning, answer, usage, model, stop = [], [], {}, None, None
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.startswith('data: '): continue
        event = json.loads(line[6:])
        if event.get('type') == 'message_start':
            model = event['message'].get('model'); usage.update(event['message'].get('usage', {}))
        delta = event.get('delta', {})
        if delta.get('type') == 'thinking_delta': reasoning.append(delta.get('thinking', ''))
        if delta.get('type') == 'text_delta': answer.append(delta.get('text', ''))
        if event.get('type') == 'message_delta':
            usage.update(event.get('usage', {})); stop = delta.get('stop_reason')
    return ''.join(reasoning), ''.join(answer), usage, model, stop

def main():
    p=argparse.ArgumentParser(); p.add_argument('--live', action='store_true')
    p.add_argument('--max-output-tokens', type=int, choices=[32768,393216], default=32768)
    p.add_argument('--case', choices=[g for _, g in CASES], help='Run one case in a fresh batch')
    args=p.parse_args()
    cases = [(n, g) for n, g in CASES if args.case is None or g == args.case]
    upstream_commit=subprocess.check_output(['git','-C',str(UPSTREAM),'rev-parse','HEAD'],text=True).strip()
    if upstream_commit != '4d09ba6d6a7e891dd8063974dfe81b3d78e3494f':
        raise SystemExit('Unexpected upstream commit')
    if subprocess.check_output([str(CLI),'--version'],text=True).strip() != '0.2.1-rc.5':
        raise SystemExit('DSH version changed; repeat offline configuration audit')
    key = key_from_environment() if args.live else 'sk-mock-not-a-real-key'
    if not key: raise SystemExit('MISSING_DEEPSEEK_API_KEY: configure Windows user environment, then retry.')
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    batch=ROOT / 'runs/exp01' / (('live_' if args.live else 'mock_')+str(args.max_output_tokens)+'_'+stamp)
    batch.mkdir(parents=True, exist_ok=False)
    dump(batch/'manifest.json',{'upstream_commit':upstream_commit,'model':'deepseek-flash','effort':'high','max_output_tokens':args.max_output_tokens,'live':args.live,'max_inference_calls':len(cases),'cases':[g for _, g in cases],'automatic_retries':0,'client':'DSH 0.2.1-rc.5','transport':'Anthropic Messages through audited loopback gateway','sampling':'provider default; no top_p override in installed transport','cost_estimate_ceiling_usd':3.0 if args.max_output_tokens>32768 else 1.0,'wall_time_limit_seconds':None if args.max_output_tokens>32768 else 1200,'timestamp_utc':stamp})
    state={'count':0, 'case':None, 'error':None}
    class Gate(http.server.BaseHTTPRequestHandler):
        def log_message(self,*a): pass
        def do_POST(self):
            body=self.rfile.read(int(self.headers['Content-Length']))
            payload=json.loads(body); folder=state['case']; state['count']+=1
            dump(folder/'request.json',payload)
            try:
                assert self.path == '/v1/messages', 'Unexpected API route'
                assert state['count'] == 1, 'More than one inference call'
                assert len(body) < 200000, 'Request exceeds predeclared input bound'
                assert payload.get('model') == 'deepseek-flash', 'Wrong model'
                assert payload.get('max_tokens') == args.max_output_tokens, 'Wrong output budget'
                assert text_blocks(payload.get('system')).strip() == SYSTEM, 'System prompt contamination'
                assert not payload.get('tools'), 'Tools must be absent'
                assert payload.get('output_config',{}).get('effort') == 'high', 'Wrong effort'
                assert payload.get('thinking',{}).get('type') in ('enabled','adaptive'), 'Thinking not enabled'
                msgs=payload['messages']; assert len(msgs)==1 and msgs[0]['role']=='user', 'Extra messages'
                assert text_blocks(msgs[0]['content']) == state['prompt'], 'User prompt contamination'
            except AssertionError as e:
                state['error']=str(e); self.send_error(400,str(e)); return
            dump(folder/'audit.json',{'passed':True,'one_call':True,'tools':0,'exact_prompt':True,'live':args.live})
            if args.live:
                request=urllib.request.Request('https://api.deepseek.com/anthropic/v1/messages',data=body,headers={'Content-Type':'application/json','x-api-key':key,'anthropic-version':'2023-06-01'})
                try: response=urllib.request.urlopen(request,timeout=300)
                except urllib.error.HTTPError as e:
                    (folder/'provider_error.txt').write_bytes(e.read()); self.send_error(e.code); state['error']=f'HTTP {e.code}'; return
                self.send_response(200); self.send_header('Content-Type','text/event-stream'); self.end_headers()
                with response, (folder/'response.sse').open('wb') as out:
                    for line in response:
                        out.write(line); out.flush(); self.wfile.write(line); self.wfile.flush()
            else:
                raw=''.join(f'event: {name}\ndata: {json.dumps(event)}\n\n' for name,event in mock_events()).encode()
                (folder/'response.sse').write_bytes(raw)
                self.send_response(200); self.send_header('Content-Type','text/event-stream'); self.end_headers(); self.wfile.write(raw)
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Gate)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    patch=batch/'replication.patch.yml'; overlay(patch,server.server_port,args.max_output_tokens)
    results=[]
    try:
        for network_id, game in cases:
            folder=batch/network_id; folder.mkdir()
            prompt=(UPSTREAM/f'exp1_which_game/runs/{game}/prompt.txt').read_text(encoding='utf-8')
            dump(folder/'source.json',{'source_file':f'exp1_which_game/runs/{game}/prompt.txt','normalized_prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'source_bytes_sha256':hashlib.sha256((UPSTREAM/f'exp1_which_game/runs/{game}/prompt.txt').read_bytes()).hexdigest()})
            state.update(count=0,case=folder,error=None,prompt=prompt)
            (folder/'prompt.txt').write_text(prompt,encoding='utf-8')
            env=os.environ.copy(); env.update(DSH_HOME=str(folder/'dsh-home'),DEEPSEEK_API_KEY='sk-gateway-placeholder',DSH_TELEMETRY_MODE='OFF')
            start=datetime.datetime.now(datetime.timezone.utc)
            with (folder/'events.jsonl').open('wb') as stdout, (folder/'stderr.log').open('wb') as stderr:
                proc=subprocess.run([str(CLI),'headless','--patch',str(patch),'--json','-'],input=prompt.encode(),stdout=stdout,stderr=stderr,env=env,cwd=folder,timeout=None if args.max_output_tokens>32768 else 1200)
            elapsed=(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds()
            if state['error'] or not (folder/'response.sse').exists():
                print(json.dumps({'id':network_id,'returncode':proc.returncode,'error':state['error'],'folder':str(folder)}),flush=True)
                raise RuntimeError('Run did not pass audit; inspect local stderr/request; no automatic retries.')
            reasoning,answer,usage,model,stop=parse_stream(folder/'response.sse')
            (folder/'reasoning.md').write_text(reasoning,encoding='utf-8'); (folder/'answer.md').write_text(answer,encoding='utf-8')
            row={'id':network_id,'true':game,'returned_model':model,'stop_reason':stop,'usage':usage,'wall_seconds':elapsed,'exit_code':proc.returncode,'reasoning_chars':len(reasoning),'live':args.live}
            m=re.search(r'^\s*(?:\*\*)?Game:\s*(?:\*\*)?\s*(.+)',answer,re.M|re.I); game_line=m.group(1) if m else ''
            candidates=[label for label,pattern in [('breakout',r'breakout|brick.break'),('pong',r'\bpong\b'),('pacman',r'pac[ -]?man'),('freeway',r'freeway|frogger')] if re.search(pattern,game_line,re.I)]
            row.update(game_line=game_line,guess=candidates[0] if len(candidates)==1 else None,correct=len(candidates)==1 and candidates[0]==game)
            confidence=re.search(r'Confidence:\s*(?:\*\*)?\s*(\d+(?:\.\d+)?)\s*%',answer,re.I)
            row['confidence']=float(confidence.group(1)) if confidence else None
            dump(folder/'result.json',row); results.append(row); dump(batch/'summary.json',results)
            print(json.dumps(row,ensure_ascii=False),flush=True)
            if stop not in ('end_turn','max_tokens'): raise RuntimeError('Unexpected stop; batch stopped.')
    finally: server.shutdown()
    print('BATCH='+str(batch),flush=True)

if __name__=='__main__': main()
