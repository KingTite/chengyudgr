# -*- coding=utf-8  -*-

from freetime5.util import ftlog, ftstr
import base64
from Crypto.Cipher import AES


KEY = 'mRzEAlhF0QTE4KfW'
IV = 'mRzEAlhF0QTE4KfW'


def encrypt(instr):
    mystr = _pad(instr)
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    ret = base64.b64encode(cipher.encrypt(mystr))
    return ret


def decrypt(encryptedData):
    encryptedData = base64.b64decode(encryptedData)
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    ret = _unpad(cipher.decrypt(encryptedData))
    ret = ret.decode(encoding="utf-8")
    return ret


def _pad(s):
    BS = AES.block_size
    s = s.encode("utf-8")
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS).encode("utf-8")


def _unpad(s):
    return s[:-ord(s[len(s) - 1:])]



#encrypt(mystr)
#decrypt("O8ctNXJ7KMSc2lFjkWFZ6PtCLMSRVsHNu1NHYmqKuLDLsMetiEDd00aslukX7i9EUnlAI4gvF7P6+9m4q5JLx8uBgdwLEHn80JAhVNPLlRKUc9GcMfLC/EEhJLjdNEx3KDa3cZOfu6b+2CWZX/Q2kttSq8YFfcQAo2K+xOwoRWS229Y5PgEcWGCL829XkAUoqJDXqVkVWOGMzpOfRy7nki00lKoshjAIEzoHUT0rUibez+faKIHiAMyG3Eu5raEd3d8Mt5b9pY13hNzUJUxYnp2n7hzCWxIgSmutqsdFbmsZgIn6qfn1lOAHc6DRznuA")
