import { requestUrl } from "obsidian";

import { BibTeXEntry } from "../bibtex";
import { Helper } from "../helper";

export class ArxivProcessor {
    private helper = new Helper();

    async sendRequest(entry: BibTeXEntry): Promise<BibTeXEntry> {
        const url = this.requestUrl(entry);
        let requestResults = null;

        try {
            const response = await requestUrl({
                url: url,
                method: 'GET'
            });
            if (response.status !== 200) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const xmlText = response.text;
            requestResults = this.parseResponse(xmlText);
        } catch (error) {
            console.error('Error fetching from arXiv API:', error);
            return entry;
        }

        const requestRelevant = this.helper.fetchMostRelevant(requestResults, entry.title);
        entry = this.helper.mergeEntries(entry, requestRelevant);

        return entry;
    }

    private requestUrl(entry: BibTeXEntry): string {
        let baseUrl = "https://export.arxiv.org/api/query?search_query";
        baseUrl += "=ti:" + encodeURIComponent(entry.title);
        if (entry.authors && entry.authors.length > 0) {
            baseUrl += "+AND+au:" + encodeURIComponent(entry.authors[0]);
        }
        baseUrl += "&max_results=5&sortBy=relevance";
        return baseUrl;
    }

    private parseResponse(xmlText: string): BibTeXEntry[] {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlText, 'text/xml');

        // Check for parsing errors
        const parserError = xmlDoc.querySelector('parsererror');
        if (parserError) {
            console.error('XML parsing error:', parserError.textContent);
            return [];
        }

        const entries: BibTeXEntry[] = [];
        const entryElements = xmlDoc.querySelectorAll('entry');

        entryElements.forEach(entryElement => {
            const id = entryElement.querySelector('id')?.textContent || '';
            const title = entryElement.querySelector('title')?.textContent?.trim() || '';
            const published = entryElement.querySelector('published')?.textContent || '';
            const summary = entryElement.querySelector('summary')?.textContent?.trim() || '';
            const doiElement = entryElement.querySelector('arxiv\\:doi, doi');
            const doi = doiElement?.textContent?.trim();

            // Extract authors
            const authorElements = entryElement.querySelectorAll('author name');
            const authors: string[] = [];
            authorElements.forEach(authorElement => {
                const authorName = authorElement.textContent?.trim();
                if (authorName) {
                    authors.push(authorName);
                }
            });

            entries.push({
                title: title,
                authors: authors,
                year: published ? published.substring(0, 4) : undefined,
                arxivId: id.split('/abs/')[1] || undefined,
                doi: doi ? [doi] : undefined,
                summary: summary,
            });
        });

        return entries;
    }
}
