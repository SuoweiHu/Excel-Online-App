import uuid
import hashlib

def hash_id(filename, hash_method=None):
    """
    Generate unique _id in the collection for a given file name 
    filename :: string
    hash_method :: None | "MD5" | "SHA1"
    """
    # # Using uuid method
    # if(hash_method == "MD5"):     return uuid.uuid3(b_filename)
    # elif(hash_method == "SHA1"):  return uuid.uuid5(b_filename)
    # else:                         return uuid.uuid(b_filename)

    # Using hashlib method 
    if(hash_method == "MD5"):       c = hashlib.md5(filename.encode("utf-8"))
    elif(hash_method == "SHA1"):    c = hashlib.sha1(filename.encode("utf-8"))
    else:                           c = hashlib.sha256(filename.encode("utf-8"))
    return c.hexdigest()
