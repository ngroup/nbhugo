"""
nbhugo
~~~~~~

Lazily convert Jupyter notebook file to Hugo-compatible Markdown file

:copyright: 2019 by Chun Nien
:license: BSD, see LICENSE for more details.
"""

import argparse
import os
import re
import nbformat
from nbconvert import MarkdownExporter
import nbconvert.exporters as exporters


def to_hugo_safe_markdown(fpath):
    notebook = nbformat.read(fpath, as_version=4)

    pattern_display = re.compile(r"(?:(?P<begin>\$\$)(?P<content>(?:.*?\r?\n?)*)(?P<end>\$\$))")
    pattern_inline = re.compile(r"(?:(?P<begin>\$)(?P<content>(?:.*?\r?\n?)*)(?P<end>\$))")
    clean_newline = lambda x: re.sub(r"\\\\", r"\\newline", x.group())
    clean_underline = lambda x: re.sub(r"\_", r"\\_", x.group())

    for cell in notebook.cells:
        if cell.cell_type == "markdown":
            # clean display math
            raw_s = cell.source
            res = re.sub(pattern_display, clean_newline, raw_s)
            res = re.sub(pattern_display, clean_underline, res)
            res = re.sub(pattern_display, r"\\\[\g<content>\\\]", res)

            # clean inline math
            res = re.sub(pattern_inline, clean_underline, res)

            cell.source = res

    out_str, res = exporters.export(MarkdownExporter, notebook)

    return out_str


def remove_title(md_str):
    pattern_title = re.compile(r"^\#.*[\r\n]")
    res = re.sub(pattern_title, "", md_str)
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('root_input', type=str)
    parser.add_argument('-o', type=str)
    parser.add_argument('--with-title', action='store_true')
    cmd_args = parser.parse_args()

    if cmd_args.o is None:
        cmd_args.o = cmd_args.root_input

    for fname in os.listdir(cmd_args.root_input):
        if fname.endswith(".nbmeta"):
            fname_prefix = os.path.splitext(fname)[0]
            path_ipynb = os.path.join(cmd_args.root_input, "{0}.ipynb".format(fname_prefix))

            with open(os.path.join(cmd_args.root_input, fname), "r") as fh:
                meta_str = fh.read()

            md_str = to_hugo_safe_markdown(path_ipynb)

            if not cmd_args.with_title:
                md_str = remove_title(md_str.strip())

            md_str = "\n".join([meta_str, md_str])

            path_md = os.path.join(cmd_args.o, "{0}.md".format(fname_prefix))

            with open(path_md, "w") as fh:
                fh.write(md_str)
