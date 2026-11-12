import subprocess,json,pathlib,time
root=pathlib.Path(__file__).resolve().parent
script=root.parent.parent/'vietnamese-skill-v2/viet-ngu-toan-thu/scripts/viet_guard.py'
source='Theo bà Hạnh , chưa có bằng chứng cho thấy việc mở đường khiến giếng cạn; hai việc chỉ xảy ra trong cùng tháng. Không phải mọi hộ dân đều phản đối dự án.'
final=source.replace('Hạnh ,','Hạnh,')
(root/'nguon.txt').write_text(source)
(root/'ban-sua.txt').write_text(final)
(root/'de-bai.txt').write_text('Viết hai câu tả mặt trời mọc bên sông, có một âm thanh cụ thể.')
(root/'ban-cuoi.txt').write_text('Mặt trời vừa nhô khỏi rặng bần, ánh sáng trượt trên mặt sông. Tiếng mái chèo khua nước vọng từ chiếc xuồng đang rời bến.')
records=[]
def run(label,*args):
 t=time.monotonic();p=subprocess.run(['python3',str(script),*args],cwd=root,text=True,capture_output=True);records.append({'label':label,'args':args,'exit':p.returncode,'elapsed_ms':round((time.monotonic()-t)*1000),'stdout':p.stdout,'stderr':p.stderr});return p
run('edit-lint','lint','nguon.txt')
run('edit-diff','diff','nguon.txt','ban-sua.txt')
run('edit-check','check','nguon.txt','ban-sua.txt','--record','edit-record.json','--reviewer','Independent AI evaluator','--review','Removed only the space before comma; attribution, no-evidence-yet, temporal coincidence and not-all scope remain unchanged.')
run('edit-verify','verify','nguon.txt','ban-sua.txt','--record','edit-record.json')
run('compose-check','check','de-bai.txt','ban-cuoi.txt','--mode','compose','--record','compose-record.json','--reviewer','Independent AI evaluator','--review','Two sentences describe a fictional sunrise beside a river and a concrete rowing sound. Prompt is material, not a draft.')
run('compose-verify','verify','de-bai.txt','ban-cuoi.txt','--mode','compose','--record','compose-record.json')
(root/'ban-cuoi.txt').write_text((root/'ban-cuoi.txt').read_text()+' ')
run('compose-stale-rejected','verify','de-bai.txt','ban-cuoi.txt','--mode','compose','--record','compose-record.json')
(root/'results.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print(json.dumps([{k:r[k] for k in ['label','exit','elapsed_ms']} for r in records],indent=2))
