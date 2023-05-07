import FindDuplicateFiles

Folders_to_scan=[r"c:\DCIM\photos1",r"c:\DCIM\photos2"]

cfg=FindDuplicateFiles.FDFConfig()
results=FindDuplicateFiles.FindDuplicateFiles(Folders_to_scan, cfg)

for group in results: #print out the results
    print(f"length={group.length} MD5={group.md5_hash}")
    for f in group.filenames:
        print("  ",f)
