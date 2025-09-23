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
        try {
            const response = await this.client.work(doi);
            if (!response.ok || response.status !== 200) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const content = response.content.message;
            return this.parseResponse([content])[0];
        } catch (error) {
            console.error('Error fetching from CrossRef API by DOI:', error);
            return null;
        }
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
            // select: selectOptions,
            rows: 5,
        }

        try {
            const response = await this.client.works(query)
            if (!response.ok || response.status !== 200) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const responseEntries = this.parseResponse(response.content.message.items);
            return this.helper.fetchMostRelevant(responseEntries, entry.title);
        } catch (error) {
            console.error('Error fetching from CrossRef API:', error);
            return null;
        }
    }

    private parseResponse(response: any): BibTeXEntry[] {
        if (!response || !Array.isArray(response)) {
            return [];
        }
        console.log(response[0]);
        return response.map((item: any) => ({
            title: Array.isArray(item.title) ? item.title[0] : item.title,
            authors: Array.isArray(item.author) ? item.author.map((author: any) => `${author["family"]}, ${author["given"]}`) : item.author ? [item.author] : [],
            year: item.year,
            doi: [item.DOI],
            references: Array.isArray(item.reference) ? item.reference.map((ref: any) => ({
                sbkey: ref.title && ref.author && ref.year ? this.helper.generateSBKey({
                    title: ref.title,
                    authors: ref.author,
                    year: ref.year
                }) : undefined,
                doi: ref.DOI,
                unstructured: ref.unstructured
            })) : [],
        }));
    }
}