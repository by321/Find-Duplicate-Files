import os,subprocess
import eel,json
import FindDuplicateFiles

@eel.expose
def GetDuplicateFiles():
    print("GetDuplicateFiles called")
    return json.dumps(results,ensure_ascii=False,default=vars)

@eel.expose
def OpenFileWithDefaultApp(fn:str):
    try:
        os.startfile(fn)
    except AttributeError:
        subprocess.call(['open', fn])

@eel.expose
def DeleteSelectedFiles(fns):
    for fn in fns:
        print(f"deleting {fn} ...");
        os.remove(fn);

###############################################

Folders_to_scan=[r"c:\DCIM\photos1",r"c:\DCIM\photos2"]

cfg=FindDuplicateFiles.FDFConfig()
cfg.hashFile=False
results=FindDuplicateFiles.FindDuplicateFiles(Folders_to_scan, cfg)

for group in results: #print out the results
    print(f"file length={group.length} MD5={group.md5_hash}")
    for f in group.filenames:
        print("  ",f)

if 0==len(results):
    print("Not startiong GUI because no potential duplicate files were found")
else:
    eel.init("web")
    eel.start('index.html')
