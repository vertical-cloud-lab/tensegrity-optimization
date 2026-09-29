import time, sys
from PIL import Image
from rembg import remove, new_session
src='/home/runner/work/tensegrity-optimization/tensegrity-optimization/figures/photos/printed-specimen.jpg'
im=Image.open(src).convert('RGB')
for model in ['isnet-general-use','u2net']:
    t=time.time()
    try:
        s=new_session(model)
        out=remove(im,session=s,only_mask=True)
        out.save(f'/tmp/rev2/agentB/work/mask_{model}.png')
        out2=remove(im,session=s,only_mask=True,post_process_mask=False,alpha_matting=True,alpha_matting_foreground_threshold=240,alpha_matting_background_threshold=10,alpha_matting_erode_size=5)
        out2.save(f'/tmp/rev2/agentB/work/mask_{model}_matting.png')
        print(model,'ok',round(time.time()-t,1),flush=True)
    except Exception as e:
        print(model,'ERR',repr(e)[:300],flush=True)
