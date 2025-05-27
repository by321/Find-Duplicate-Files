import os, sys, argparse

def valid_directory(path):
    """Validate that the provided path is a directory."""
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"'{path}' is not a valid directory")
    return path

def parse_command_line():
    parser = argparse.ArgumentParser(description="Find duplicate files in one or more directories.")

    parser.add_argument(
        '-d', '--dir',  type=valid_directory, action='append',  # collects occurrences into a list
        help="a directory path (can be specified multiple times)"
    )
    parser.add_argument('-wb', '--win-batch', type=str, dest='output_wb', default='',
        help='output a Windows batch file to delete duplicate files (optional)')
    parser.add_argument('-ss', '--shell-script', type=str, dest='output_ss', default='',
        help='output a shell script file to delete duplicate files (optional)')

    args=parser.parse_args()
    if args.dir is None:
        parser.error("At least one directory must be provided with -d or --dir")
        quit()
    return args

def normalize_input_paths(input_dirs):
    print("specified directories:", input_dirs)
    dirs=[os.path.abspath(os.path.normpath(x)) for x in input_dirs]
    if sys.platform.startswith("win"):
        dirs=[x.lower() for x in dirs]
    # remove duplicates by converting list to set
    dirs = list(dict.fromkeys(dirs))  # preserves order
    print("Normalized and duplicate removed:", dirs)
    return dirs

def get_key_nameonly_then_fullpath(file_path):
    # extract filename without extension
    filename = os.path.splitext(os.path.basename(file_path))[0]
    # return tuple for sorting: (filename_without_extension, full_path)
    return (filename, file_path)

def escape_filename_for_single_quotes(filename): # for unix shell scripts
    return filename.replace("\'", "\'\\\'\'") # file'name -> file'\''name

if __name__ == "__main__":
    args=parse_command_line()

    dirs_to_scan=normalize_input_paths(args.dir)

    import FindDuplicateFiles
    cfg=FindDuplicateFiles.FDFConfig()
    #cfg.hashFile=False #skip hashing
    results=FindDuplicateFiles.FindDuplicateFiles(dirs_to_scan, cfg)

    printToScr=True
    print("output Windows batch file:", args.output_wb)
    print("output Unix shell script:", args.output_ss)
    fWB=fSS=None
    if args.output_wb!='':
        fWB=open(args.output_wb,'wt',encoding='utf-8')
        printToScr=False
    if args.output_ss!='':
        fSS=open(args.output_ss,'wt',encoding='utf-8')
        printToScr=False
    if printToScr==True:
        print("no output file specified, printing to screen ...")

    for group in results: #print out the results
        min_index = 0
        min_key = get_key_nameonly_then_fullpath(group.filenames[0])
        for i, path in enumerate(group.filenames[1:], 1):
            current_key = get_key_nameonly_then_fullpath(path)
            if current_key < min_key:
                min_index = i
                min_key = current_key
        groupInfoStr=f"length={group.length} MD5={group.md5_hash}"
        if printToScr==True:
            print(groupInfoStr)
            print(" *",group.filenames[min_index]) #print min filename first
        if fWB is not None:
            fWB.write("rem "+groupInfoStr+'\n')
            fWB.write("rem keep "+group.filenames[min_index]+'\n')
        if fSS is not None:
            fSS.write("# "+groupInfoStr+'\n')
            fSS.write("#keep "+group.filenames[min_index]+'\n')
        for i, path in enumerate(group.filenames):
            if i==min_index: continue
            if printToScr==True: print("  ",path)
            if fWB is not None: fWB.write(f'del "{path}"\n')
            if fSS is not None: fSS.write(f"rm '{escape_filename_for_single_quotes(path)}'\n")

    if fWB is not None: fWB.close()
    if fSS is not None: fSS.close()
