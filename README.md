# Paper-Relations
Process and connect relations of papers

This script:
- extracts BibTeX entry in Markdown file and creates Markdown metadata
- using ChatGPT-4o-mini, create keywords from Markdown file
- add metadata and keywords to given Markdown file

## Usage

```bash
$ paper_rel_gen.py -h
usage: paper_rel_gen [-h] [-vs] filename

Processes markdown notes with BibTeX to add metadata to paper notes.

positional arguments:
  filename             Markdown file to process.

options:
  -h, --help           show this help message and exit
  -vs, --vector-store  Creates embedding vector of the text.
```

### Quick Start
1. copy `paper_rel_gen.py` to `~/.local/bin` or other directory to use
2. install dependencies from `requirements.txt`
    - if using venv change `python` in [first line](https://github.com/EC97B0EAB79C/Paper-Relations/blob/main/paper_rel_gen.py#L1) to your venv location
3. apply and setup [Github Models Marketplace](https://github.com/marketplace/models)
4. run
    ```bash
    paper_rel_gen filename
    ```

## Acknowledgement
- Thank you to arXiv for use of its open access interoperability.