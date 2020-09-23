import os
import sys
import setuptools
from setuptools import Extension
from setuptools.command.build_py import build_py as _build_py
import distutils.dir_util
import distutils.log

class build_py(_build_py):
    def run(self):
        self.run_command("build_ext")
        return super().run()

kaldi_root = os.getenv('KALDI_ROOT')
kaldi_mkl = os.getenv('KALDI_MKL')
source_path = os.getenv("VOSK_SOURCE", os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../src")))

if kaldi_root == None:
    print("Define KALDI_ROOT")
    exit(1)

distutils.log.set_verbosity(distutils.log.DEBUG)
distutils.dir_util.copy_tree(
    source_path,
    "vosk",
    update=1,
    verbose=1)

with open("README.md", "r") as fh:
    long_description = fh.read()

kaldi_static_libs = ['dist/lib/libkaldi-online2.a',
             'dist/lib/libkaldi-decoder.a',
             'dist/lib/libkaldi-ivector.a',
             'dist/lib/libkaldi-gmm.a',
             'dist/lib/libkaldi-nnet3.a',
             'dist/lib/libkaldi-tree.a',
             'dist/lib/libkaldi-feat.a',
             'dist/lib/libkaldi-lat.a',
             'dist/lib/libkaldi-lm.a',
             'dist/lib/libkaldi-hmm.a',
             'dist/lib/libkaldi-transform.a',
             'dist/lib/libkaldi-cudamatrix.a',
             'dist/lib/libkaldi-matrix.a',
             'dist/lib/libkaldi-fstext.a',
             'dist/lib/libkaldi-util.a',
             'dist/lib/libkaldi-base.a',
             'dist/lib/libfst.a',
             'dist/lib/libfstngram.a']
kaldi_link_args = ['-s']
kaldi_libraries = []

if sys.platform.startswith('darwin'):
    kaldi_link_args.extend(['-Wl,-undefined,dynamic_lookup', '-framework', 'Accelerate'])
elif kaldi_mkl == "1":
    kaldi_link_args.extend(['-L/opt/intel/mkl/lib/intel64', '-Wl,-rpath=/opt/intel/mkl/lib/intel64'])
    kaldi_libraries.extend(['mkl_rt', 'mkl_intel_lp64', 'mkl_core', 'mkl_sequential'])
else:
    kaldi_static_libs.append('tools/OpenBLAS/libopenblas.a')
    kaldi_libraries.append('gfortran')

sources = ['kaldi_recognizer.cc', 'model.cc', 'spk_model.cc', 'vosk_api.cc', 'vosk.i']

vosk_ext = Extension('vosk._vosk',
                    define_macros = [('FST_NO_DYNAMIC_LINKING', '1')],
                    include_dirs = [kaldi_root + '/dist/include/kaldi', kaldi_root + '/dist/include/openfst', 'vosk'],
                    swig_opts=['-outdir', 'vosk', '-c++'],
                    libraries = kaldi_libraries,
                    extra_objects = [kaldi_root + '/' + x for x in kaldi_static_libs],
                    sources = ['vosk/' + x for x in sources],
                    extra_link_args = kaldi_link_args,
                    extra_compile_args = ['-std=c++11', '-Wno-sign-compare', '-Wno-unused-variable', '-Wno-unused-local-typedefs'])

setuptools.setup(
    name="vosk",
    version="0.3.13",
    author="Alpha Cephei Inc",
    author_email="contact@alphacephei.com",
    description="Offline open source speech recognition API based on Kaldi and Vosk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alphacep/vosk-api",
    packages=setuptools.find_packages(),
    ext_modules=[vosk_ext],
    cmdclass = {'build_py' : build_py},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    python_requires='>=3.5',
)
