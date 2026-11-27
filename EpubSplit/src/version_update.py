#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2021, Jim Miller

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import codecs, sys, re

from tempfile import mkstemp
from os import replace, close
from pathlib import Path

#print(sys.argv[1:])

## Files that contain version numbers that will need to be updated.
version_files = [
#    'setup.py',
    '__init__.py',
    'epubsplit.py',
    ]

## save version from this file for index.html link.
# save_file='version_test.txt'
save_file='webservice/app.yaml'
saved_version = None

def main(args):
    # Complete upstream version followed by this repository's revision.
    '''
__version__ = (2, 3, 6)
    version="2.3.6",
version: 2-3-06a
version="2.3.6"
'''
    version_re = \
        r'^(?P<prefix>[ ]*(__)?)version(?P<infix>(__)?[ =:"\\(]+)' \
        r'(?P<numbers>[0-9]+(?P<separator>[, \\.-]+)[0-9]+(?:[, \\.-]+[0-9]+)*)' \
        r'(?P<suffix>[",\\)]*\r?\n)$'

    flag = args[0]

    if len(args) > 1 :
        version = [int(x) for x in args[1:]]
    else:
        prior_version = None
        with codecs.open(version_files[0], 'r', 'utf-8') as source_file:
            for line in source_file:
                m = re.match(version_re,line)
                if m:
                    prior_version = re.split(r'[, \\.-]+', m.group('numbers'))
                    print(prior_version)
                    break
        if prior_version is None:
            raise ValueError('找不到完整版本宣告。')
        version = [int(x) for x in prior_version]
        # This repository appends its own revision to the complete upstream version.
        version[-1] += 1

    print(version)
    def version_subs(match):
        return (match.group('prefix') + 'version' + match.group('infix') +
                match.group('separator').join(map(str, version)) + match.group('suffix'))

    do_loop(version_files, version_re, version_subs)

    index_files = []
    # index_files = ['webservice/index.html']
    # if saved_version:
    #     ## only do major/minor, always leave micro 0 in index.html.
    #     index_re = 'https://([0-9-]+[a-z]?)\\.fanficfare\\.appspot\\.com'
    #     index_subs = 'https://%s-%s-0.fanficfare.appspot.com'%saved_version[0:2]
    #     do_loop(index_files, index_re, index_subs)

    release = flag.capitalize()
    print('\ngit add %s'%(" ".join(version_files+index_files)))
    print('git commit -m "Bump %s Version %s"'%(release,'.'.join([str(x) for x in version])))

def do_loop(files, pattern, substring):
    global saved_version
    for source_file_path in files:
        print("src:"+source_file_path)
        fh, target_file_path = mkstemp(dir=Path(source_file_path).resolve().parent)
        with codecs.open(target_file_path, 'w', 'utf-8') as target_file:
            with codecs.open(source_file_path, 'r', 'utf-8') as source_file:
                for line in source_file:
                    repline = re.sub(pattern, substring, line)
                    if line != repline and source_file_path == save_file:
                        m = re.match(pattern,line)
                        saved_version = tuple(re.split(r'[, \\.-]+', m.group('numbers')))
                        print("<-%s->%s"%(line,repline))
                    target_file.write(repline)
        close(fh)
        replace(target_file_path,source_file_path)

if __name__ == '__main__':
    args = list(sys.argv[1:])

    if len(args) == 0:
        args.append('test')
    if args[0] in ('test', 'release') and (len(args) == 1 or
            (len(args) >= 3 and all(x.isdecimal() for x in args[1:]))):
        main(args)
    else:
        print("args: (test|release) [完整上游版號各段 本地修訂次數]")
#    print(saved_version)
