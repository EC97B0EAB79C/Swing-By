import { requestUrl } from "obsidian";

import { BibTeXEntry, References } from "../bibtex";
import { Helper } from "../helper";

export class AdsProcessor {
    private helper = new Helper();
    private endpoint = "https://ui.adsabs.harvard.edu/v1/search/query";
    private apiKey = '';

    setApiKey(key: string) {
        this.apiKey = key;
    }

    async sendRequest(entry: BibTeXEntry | References, getReferences = false): Promise<BibTeXEntry | null> {
        const headers = {
            "Authorization": `Bearer ${this.apiKey}`,
        };
        const query = this.createQuery(entry);
        if (!query || query.length === 0) {
            return {} as BibTeXEntry;
        }
        const filter = "doi,abstract,title,first_author,bibcode,year" + (getReferences ? ",reference" : "");

        try {
            const response = await requestUrl({
                url: `${this.endpoint}?q=${encodeURIComponent(query)}&fl=${encodeURIComponent(filter)}&rows=5`,
                method: 'GET',
                headers: headers,
            });
            if (response.status !== 200) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const responseEntries = this.parseResponse(response.json.response.docs);
            if (responseEntries.length === 1) {
                return responseEntries[0];
            }
            if ('title' in entry && entry.title) {
                return this.helper.fetchMostRelevant(responseEntries, entry.title) || (entry as BibTeXEntry);
            }
        } catch (error) {
            console.error('Error fetching from ADS API:', error);
            return entry as BibTeXEntry;
        }
        return null;
    }

    private createQuery(detail: BibTeXEntry | References): string {
        let query: string[] = [];
        if ('bibcode' in detail && detail.bibcode) query.push(`bibcode:${detail.bibcode}`);
        if ('doi' in detail && detail.doi) {
            if (Array.isArray(detail.doi)) {
                detail.doi.forEach(doi => {
                    query.push(`doi:"${doi}"`);
                });
            } else {
                query.push(`doi:"${detail.doi}"`);
            }
        }
        if ('arxivId' in detail && detail.arxivId) query.push(`arXiv:"${detail.arxivId}"`);
        if ('title' in detail && detail.title) {
            let titleQuery = `title:"${detail.title}"`
            if ('authors' in detail && detail.authors && detail.authors.length > 0) {
                titleQuery += ` AND author:"${detail.authors[0]}"`;
            }
            query.push(titleQuery);
        }

        return query.join(' OR ');
    }

    private parseResponse(response: any): BibTeXEntry[] {
        if (!response || !Array.isArray(response)) {
            return [];
        }
        return response.map((item: any) => ({
            title: Array.isArray(item.title) ? item.title[0] : item.title,
            authors: item.first_author ? [item.first_author] : [],
            year: item.year,
            doi: Array.isArray(item.doi) ? item.doi : item.doi ? [item.doi] : [],
            bibcode: item.bibcode,
            summary: item.abstract,
            references: this.getReferencesFromItem(item),
            sbkey: item.first_author && item.year && item.title ? this.helper.generateSBKey({
                title: item.title[0],
                authors: [item.first_author],
                year: item.year,
            }) : undefined,
        }));
    }

    private getReferencesFromItem(item: any): References[] | undefined {
        if (!item.reference || !Array.isArray(item.reference)) {
            return undefined;
        }
        return item.reference.map((ref: any) => ({
            bibcode: ref,
        }));
    }
}