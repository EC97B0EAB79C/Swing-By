import { CrossrefClient, QueryWorksParams, WorkSelectOptions, WorkSortOptions } from "@jamesgopsill/crossref-client"

import { BibTeXEntry, References } from "../bibtex";
import { Helper } from "../helper";

export class CrossRefProcessor {
    private client = new CrossrefClient();
    private helper = new Helper();

    async sendRequest(detail: BibTeXEntry | string, getReferences = false): Promise<BibTeXEntry | null> {
        if (typeof detail === 'string') {
            return this.sendRequestDOI(detail);
        }
        else {
            return this.sendRequestQuery(detail, getReferences);
        }
    }

    async sendRequestDOI(doi: string): Promise<BibTeXEntry | null> {
        let requestResults = null;
        try {
            console.log('CrossRef API Request by DOI:', doi);
            const response = await this.client.work(doi);
            if (!response.ok || response.status !== 200) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const content = response.content.message;
            requestResults = this.parseResponse([content]);
        } catch (error) {
            console.error('Error fetching from CrossRef API by DOI:', error);
            return null;
        }

        if (!requestResults || requestResults.length === 0) {
            console.log('CrossRef API Response by DOI: No results found');
            return null;
        }

        const selectedEntry = requestResults[0];
        console.log('CrossRef API Response by DOI:', selectedEntry.title);
        return selectedEntry;
    }

    async sendRequestQuery(entry: BibTeXEntry, getReferences = false): Promise<BibTeXEntry | null> {
        const selectOptions = [
            WorkSelectOptions.ABSTRACT,
            WorkSelectOptions.AUTHOR,
            WorkSelectOptions.DOI,
            WorkSelectOptions.TITLE,
            WorkSelectOptions.PUBLISHED,
        ];
        if (getReferences) {
            selectOptions.push(WorkSelectOptions.REFERENCE);
        }
        const query: QueryWorksParams = {
            queryTitle: entry.title,
            queryAuthor: entry.authors ? entry.authors[0] : undefined,
            sort: WorkSortOptions.RELEVANCE,
            select: selectOptions,
            rows: 5,
        }
        let requestResults = null;

        try {
            console.log('CrossRef API Request by Query:', query);
            const response = await this.client.works(query)
            if (!response.ok || response.status !== 200) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            requestResults = this.parseResponse(response.content.message.items);
        } catch (error) {
            console.error('Error fetching from CrossRef API:', error);
            return null;
        }

        if (!requestResults || requestResults.length === 0) {
            console.log('CrossRef API Response by Query: No results found');
            return null;
        }

        const selectedEntry = this.helper.fetchMostRelevant(requestResults, entry.title) || entry;
        console.log('CrossRef API Response by Query:', selectedEntry.title);
        return selectedEntry;
    }

    private parseResponse(response: any): BibTeXEntry[] {
        if (!response || !Array.isArray(response)) {
            return [];
        }
        return response.map((item: any) => ({
            title: Array.isArray(item.title) ? item.title[0] : item.title,
            authors: Array.isArray(item.author) ? item.author.map((author: any) => `${author["family"]}, ${author["given"]}`) : item.author ? [item.author] : [],
            year: item.year,
            doi: [item.DOI],
            references: this.getReferenceFromItem(item),
        }));
    }

    private getReferenceFromItem(item: any): References[] {
        if (!item || !Array.isArray(item.reference)) {
            return [];
        }
        return item.reference.map((ref: any) => ({
            sbkey: ref.articleTitle && ref.author && ref.year ? this.helper.generateSBKey({
                title: ref.articleTitle,
                authors: [ref.author],
                year: ref.year,
            }) : undefined,
            doi: ref.DOI,
            unstructured: ref.unstructured,
            proceedings: ref.volumeTitle ? {
                author: ref.author,
                volumeTitle: ref.volumeTitle,
                year: ref.year,
            } : undefined,
        }));
    }
}