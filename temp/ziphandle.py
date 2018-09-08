import zipfile


def make_archive(fileList, archive):
    '''
    Creates a zip file (archive) of all the files in fileList.
        fileList is a list of file names - full path each name
        archive is the file name for the archive with a full path
    '''
    try:
        a = zipfile.ZipFile(archive, 'w', zipfile.ZIP_STORED)
        a.pwd='123'
        zd = zipfile._ZipDecrypter(mypwd)
        plain_bytes = zd(cypher_bytes)
        for f in fileList:
            a.write(f)
        a.close()
        return True
    # except Exception, Argument:
    except Exception:
        # log_message('MSG: %s\n' % str(e))
        return False
