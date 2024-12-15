



    



##
# Test Code
load_db()

# Process input file
markdown = read_file(args.filename)
metadata_yaml, body = extract_yaml(markdown)
metadata_bibtex = extract_bibtex(body)
metadata = metadata_yaml | metadata_bibtex
metadata["key"] = ".".join(os.path.basename(args.filename).split('.')[:-1])

# Get summary
summary = None
id_arxiv = None
if args.article:
    summary, doi, id_arxiv = query_arxiv(metadata["title"], metadata["author"][0])

# Get references
ref_doi = None
if args.article:
    doi, ref_doi = query_crossref(metadata["title"], metadata["author"][0], doi)
    if not ref_doi:
        process_warning(REF_WARNING_TEXT, abort = True)

# Get ADS references
ads_ref = None
if args.article and id_arxiv:
    ads_ref, bibcode = query_ads(id_arxiv)
    if not ads_ref:
        process_warning(REF_WARNING_TEXT, abort = True)

# Create embeddings
embeddings = create_embedding(
    {
        "title": metadata["title"],
        "summary": summary,
        "body" : body
    }
)

# Create keywords
keyword_example = None
if type(paper_db) == pandas.DataFrame:
    keyword_example = get_keyword_example(embeddings)
keywords = create_keywords(metadata["title"], summary, body, keyword_example)
metadata["keywords"] = keywords
metadata["tags"] = ["Paper"] + keywords
metadata["category"] = keywords[0]

# If keyword only mode
if args.keyword_only:
    for keyword in keywords:
        print(f"- {keyword}")
    exit()

# Write MD file
md_metadata = organize_md_metadata(metadata)
md_content = create_md_content(md_metadata, body)
write_file(args.filename, md_content)

# Update references
append_reference(doi, ref_doi)

# Add entry to DB
new_entry = organize_db_entry(doi, id_arxiv, metadata, embeddings)
append_entry(new_entry)
save_db()