报错信息：
Collecting cffi==1.11.5 (from -r requirements.txt (line 4))
  Downloading https://files.pythonhosted.org/packages/e7/a7/4cd50e57cc6f436f1cc3a7e8fa700ff9b8b4d471620629074913e3735fb2/cffi-1.11.5.tar.gz (438kB)
    Complete output from command python setup.py egg_info:
    
        No working compiler found, or bogus compiler options passed to
        the compiler from Python's standard "distutils" module.  See
        the error messages above.  Likely, the problem is not related
        to CFFI but generic to the setup.py of any Python package that
        tries to compile C code.  (Hints: on OS/X 10.8, for errors about
        -mno-fused-madd see http://stackoverflow.com/questions/22313407/
        Otherwise, see https://wiki.python.org/moin/CompLangPython or
        the IRC channel #python on irc.freenode.net.)
    
    ----------------------------------------
Command "python setup.py egg_info" failed with error code 1 in /tmp/pip-install-1p74ronb/cffi/
The command '/bin/sh -c pip install -r requirements.txt' returned a non-zero code: 1
ERROR: Job failed: exit code 1


解决方案：
You need a working compiler, the easiest way around this is to install the build-base package like so:

```apk add --no-cache --virtual .pynacl_deps build-base python3-dev libffi-dev```
This will install various tools that are required to compile pynacl and  pip install pynacl will now succeed.

Note it is optional to use the --virtual flag but it makes it easy to trim the image because you can run apk del .pynacl_deps later in your Dockerfile as they are not needed any more and would reduce the overall size of the image.
