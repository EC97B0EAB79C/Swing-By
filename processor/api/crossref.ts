import { CrossrefClient, QueryWorksParams, WorkSortOptions } from "@jamesgopsill/crossref-client"

import { BibTeXEntry } from "../bibtex";
import { Helper } from "../helper";

export class CrossRefProcessor {
    private client = new CrossrefClient();
    private helper = new Helper();

    async fillEntry(entry: BibTeXEntry): Promise<BibTeXEntry[]> {
        let requestRelevant = null;
        const query: QueryWorksParams = {
            queryTitle: entry.title,
            queryAuthor: entry.authors ? entry.authors[0] : undefined,
            sort: WorkSortOptions.RELEVANCE,
            rows: 5
        }

        try {
            const response = await this.client.works(query)
            if (!response.ok || response.status !== 200) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            requestRelevant = this.helper.fetchMostRelevant(
                response.content.message.items, entry.title
            );
            console.log('CrossRef API entries:', requestRelevant);
        } catch (error) {
            console.error('Error fetching from CrossRef API:', error);
            return [];
        }

        return [];
    }

    private parseResponse(response: any): BibTeXEntry[] {
        if (!response || !Array.isArray(response.items)) {
            return [];
        }
        return response.items.map((item: any) => ({
            title: item.title,
            authors: item.author,
            year: item.year,
            doi: item.DOI,
            reference: item.reference
        }));
    }
}