# FindDuplicateFiles with Simple GUI

This is a Python program I wrote years ago to help me find duplicates in my photo files. Recently I added a simple GUI in HTML/javascript, using Eel package for Python-web interop.

## Usage
Basica usage is very simple, as shown in demo.py:

	import FindDuplicateFiles

	Folders_to_scan=[r"c:\dcim\photos1", r"c:\dcim\photos2", r"c:\dcim\photos3"]

	cfg=FindDuplicateFiles.SearchConfig()
	results=FindDuplicateFiles.FindDuplicateFiles(Folders_to_scan, cfg)

	for group in results: #print out the results
		print(f"length={group.length} MD5={group.md5_hash}")
		for f in group.filenames:
			print("  ",f)

**FindDuplicateFiles.FindDuplicateFiles()** is the main function, it takes a list of one or more folder paths as input, and returns a list of **FileGroup** objects. Each FileGroup contains paths of multiple files that have the same file length and MD5 signature (optional):

	class FileGroup:
		# a FileGroup contains two or more files that have the same length and MD5 hash
		def __init__(self,length:int=0,md5_hash:str=''):
			self.length = length # file length
			self.md5_hash = md5_hash # file MD5 hash, optional, '' if not computed
			self.filenames = [] # a list of filenames

You can control how FindDuplicateFiles.FindDuplicateFiles() behaves by using a **FDFConfig** object, which has the following data members:

- **ignoreSmallerThan** (int): Ignore files smaller than this. Default is 0.
- **ignoreBiggerThan** (int): Ignore files bigger than this. Default is -1, meaning no upper limit.
- **dontHashIfBiggerThan** (int): Don't compute MD5 hash if file is bigger than this size, default is 256 MB. This is to let you skip hashing big files and check them manually.
- **hashFile**(bool): Set this to False to skip MD5 hashing entirely, files will be grouped by file length only. Default is True.
- **hashReadBufferKB**(int): read buffer size in KB when computing MD5 hash. Default is 1024.

for example:

	cfg=FindDuplicateFiles.SearchConfig()
	cfg.ignoreSmallerThan=10*1024 #ignore files smaller than 10 KB
	cfg.ignoreBiggerThan=1024*1024*1024 #ignore files bigger than 1 GB
	cfg.dontHashIfBiggerThan=512*1024*1024 #don't compute MD5 for files bigger than 512 MB
	#cfg.hashFile=False #set to False to skip MD5 hashing for all files
	results=FindDuplicateFiles.FindDuplicateFiles(Folders_to_scan, cfg)

## GUI

Run "**python demo_gui.py**" from project directory. It still does the file scanning and grouping in the console, but after that is finished, it will shows a simple GUI that let you:

- Open files using system's default applications for file types.
- Select and delete files.

GUI is written in HTML & javascript. Web-to-python interface is done using [the Eel library](https://github.com/python-eel/Eel "the Eel library").

## What It Does Behind the Scene

FindDuplicateFiles.FindDuplicateFiles() scans its input folder(s) and builds a list of all files found, it then groups them by file length. Groups that have only one file in them are discarded since no duplicate is possible. The remaining groups are further grouped by file's MD5 signature, unless the hashFile configuration parameter is set to False. Again, group that have only one file in them are discarded. The groups that still remain are returned to the caller.

