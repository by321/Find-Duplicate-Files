import os, hashlib

class FileGroup:
    # a FileGroup contains two or more files that have the same length and MD5 hash
    def __init__(self,length:int=0,md5_hash:str=''):
        self.length = length # file length
        self.md5_hash = md5_hash # file MD5 hash, optional, '' if not computed
        self.filenames = [] # list of filenames

class FDFConfig:
    '''This class contains options on how we search for files.

    Data members:
        ignoreSmallerThan (int): Ignore files smaller than this. Default is 0.
        ignoreBiggerThan (int): Ignore files bigger than this. Default is -1, meaning no upper limit.
        dontHashIfBiggerThan (int): Don't compute MD5 hash if file is bigger than this size, default is 256 MB.
                                    This is to let you skip hashing big files and check them manually.
        hashFile(bool): Set this to False to skip MD5 hashing entirely, files will be grouped by file length only.
                        Default is True.
        hashReadBufferKB(int): read buffer size in KB when computing MD5 hash. Default is 1024.
    '''

    def __init__(self):
        self.ignoreSmallerThan:int = 0 #ignore files smaller than this size
        self.ignoreBiggerThan:int=-1 #ignore files bigger than this size
        self.dontHashIfBiggerThan:int=256*1024*1024 #don't compute MD5 for files bigger than this size
        self.hashFile:bool=True, #when True, will compute MD5 for files of same size
        self.hashReadBufferKB:int=1024 #when hashing file, read buffer in KB


def GetFileLengthsAndNames(scan_dirs, cfg):
# get a list of files and their lengths in the input directory or directories:
# return [ [file0_len,file0_path] , [file1_len,file1_path] , [file2_len,file2_path] ... ]
    len_name=[]
    for sd in scan_dirs:
        print(f"scanning input directory {sd} ...")
        for (root, dirs, files) in os.walk(sd, topdown=True):
            print(f"  {root}, ",end='')
            len0= len(len_name);
            for f in files:
                #print(root,f)
                fn=os.path.join(root,f)
                flen=os.stat(fn).st_size
                if flen<cfg.ignoreSmallerThan:
                    #print(f"smaller {fn} {flen}")
                    continue
                if cfg.ignoreBiggerThan!=-1 and flen>cfg.ignoreBiggerThan:
                    #print(f"bigger {fn} {flen}")
                    continue
                #print(flen,fn)
                len_name.append([flen,fn])
            print(f"files found: {len(len_name)-len0}")
    print(f"total files found: {len(len_name)}")
    return len_name


def GetMD5(fname, bufLen):
    hash_obj=hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(bufLen), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


""" inputList:
[
  [value, file_path], [value, file_path], [value, file_path] ...
]

value is either file length or file's MD5 hash.
Group inputList by duplicated values and return the result like this:

[
    [   [value1, file_path], [value1, file_path], [value1, file_path] ... ],
    [   [value2, file_path], [value2, file_path], [value2, file_path] ... ],
    [   [value3, file_path], [value3, file_path], [value3, file_path] ... ],
    ...
]
"""
def GroupItemsByDuplicatedFirstValues(inputList):

    inputList.sort(key=lambda x: x[0]) #sort the list by item's first value
    output=[]

    inputListLen=len(inputList)
    idx0:int=0; value0=inputList[0][0]
    idx1:int=1
    nFiles:int=0
    while idx1<inputListLen:
        value1=inputList[idx1][0]
        #if value1==1690293: print(value1,inputList[idx1][1]) #for debugging
        if (value1!=value0): #different first value encountered
            if idx1!=idx0+1:
                output.append(inputList[idx0:idx1])
                nFiles+=idx1-idx0
            idx0=idx1
            value0=value1
        idx1+=1
    if (idx1-idx0>1):
        output.append(inputList[idx0:idx1])
        nFiles += idx1 - idx0
    return output,nFiles


def FindDuplicateFiles(scan_dirs, cfg=None):
    if cfg is None:
        cfg=FDFConfig()
    else:
        if (cfg.hashReadBufferKB<1): cfg.hashReadBufferKB=1024

    len_name=GetFileLengthsAndNames(scan_dirs, cfg)
    lnlen=len(len_name)
    if lnlen<2: return []

    results=[]

    len_groups,nLenFiles=GroupItemsByDuplicatedFirstValues(len_name) #first value is file length here
    print(f"potential duplicate files due to same file length: {nLenFiles}")
    if cfg.hashFile: print("computing MD5 hash ...")
    nHashFiles:int=0
    for lg in len_groups:
        filelen=lg[0][0] # all files in this group have this length
        #print(f"size={filelen}")
        if cfg.hashFile and filelen<=cfg.dontHashIfBiggerThan: #group by MD5 signature
            for f in lg: #replace length with MD5 signature
                f[0]=GetMD5(f[1], cfg.hashReadBufferKB * 1024)
            hash_groups,nLenFiles=GroupItemsByDuplicatedFirstValues(lg)
            for hg in hash_groups:
                g = FileGroup(filelen, hg[0][0]) # all files in this group have this hash signature
                g.filenames=[f[1] for f in hg]
                results.append(g)
                nHashFiles+=len(hg)
        else: #not hashing file, just add filenames
            g = FileGroup(filelen,'');
            g.filenames = [f[1] for f in lg]
            results.append(g)
            nHashFiles+=len(lg)
    if cfg.hashFile:
        print(f"potential duplicate files after checking MD5 hash: {nHashFiles}")
    return results
