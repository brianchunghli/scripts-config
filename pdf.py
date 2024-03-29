#!/usr/bin/env python3
"""PDF utility.

A python script for merging pdf files using pypdf

TODO:
  [ ] Add file sorting based on time of creation
  [ ] Add file sorting based on length of documents

"""

import argparse
import os
import subprocess

try:
    from pypdf import PdfMerger, PdfReader, PdfWriter, errors
except ImportError:
    import sys
    sys.exit("%s: pypdf module required." % (os.path.basename(sys.argv[0])))

from helper import prog_print


def parse_args() -> None:
    parser = argparse.ArgumentParser(
        description='A utility program for merging and slicing pdfs')
    # universal options to be inherited by subparsers
    options = argparse.ArgumentParser(add_help=False)
    options.add_argument('-n',
                         '--name',
                         nargs=1,
                         default=[None],
                         type=str,
                         metavar='file_name',
                         help='set a filename for the new pdf')
    # subparser for merging
    subp = parser.add_subparsers(dest='subcommand')
    pdfmerge = subp.add_parser('merge', parents=[
        options,
    ])
    # subparser for merging
    pdfcut = subp.add_parser('cut', parents=[
        options,
    ])

    pdfmerge.add_argument(dest='files', nargs='*')
    pdfcut.add_argument(dest='files', nargs=1)
    pdfcut.add_argument(dest='positions', nargs='*', type=int)

    pdfmerge.set_defaults(func=merge)
    pdfcut.set_defaults(func=cut)

    return parser.parse_args()


def all_files_exist(files: list) -> bool:
    """File validation."""
    all_exist = True
    for f in files:
        pdf_file = f'{os.getcwd()}/{f}'
        if not (os.path.exists(pdf_file)):
            prog_print(f'\'{f}\' is not found in the current directory.')
            all_exist = False
    return all_exist


def cut(file: str, pos: list, **kwargs):
    """Pdf cut functionality."""

    if not os.path.isfile(os.path.join(os.getcwd(), file)):
        prog_print(f'\'{file}\' is not a file.')
        return

    new_file = PdfWriter()
    with open(file, 'rb') as f:
        try:
            reader = PdfReader(f, strict=True)
        except errors.PdfReadError as exc:
            prog_print(f'\'{file}\' is not a pdf file.')
            return
        # invalid number of pages
        if not pos or len(pos) > 2:
            return
        # start only means we copy one page from
        # the page specified
        if len(pos) < 2:
            start = pos[0]
            end = start + 1
        # pages start ==> start + end
        else:
            start = pos[0]
            end = start + pos[1]
        for p in reader.pages[start:end]:
            new_file.add_page(p)

    filename = 'cut.pdf' if not kwargs.get(
        'name') else f'{kwargs.get("name")}.pdf'
    with open(filename, 'wb') as f:
        new_file.write(f)


def merge(files: list, **kwargs) -> None:
    """Pdf merge functionality."""
    pdf_merger = PdfMerger(strict=True)
    for file in files:
        if not os.path.isfile(os.path.join(os.getcwd(), file)):
            continue
        try:
            with open(os.path.join(os.getcwd(), file), 'rb') as f:
                pdf_merger.append(f)
        except errors.PdfReadError as e:
            prog_print(f'omitted file provided: \'{file}\'')
    # custom name
    filename = 'merged.pdf' if not kwargs.get(
        'name') else f'{kwargs.get("name")}.pdf'
    with open(filename, 'wb') as output:
        pdf_merger.write(output)


def main() -> None:
    args = parse_args()
    if not args.subcommand:
        subprocess.run(['pdf', '-h'])
        return
    # no merging for less than two files
    # check that files exist

    if not all_files_exist(args.files):
        return

    if not args.files:
        prog_print('no files provided.')
        return

    if args.subcommand == 'merge':
        args.func(args.files, name=args.name[0])

    if args.subcommand == 'cut':
        args.func(args.files[0], args.positions, name=args.name[0])


if __name__ == '__main__':
    main()
