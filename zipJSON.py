import zipfile
from constants import *

def main():
    zipname = f"{'.'.join(data_file_name.split('.')[:-1])}.zip"
    
    # create file and save zip-ed data
    #open(zipname, "a").close()
    zip = zipfile.ZipFile(zipname, mode='w')
    zip.write(data_file_name, compress_type=zipfile.ZIP_DEFLATED)
    zip.close()
    
    return

if __name__ == "__main__":
    main()