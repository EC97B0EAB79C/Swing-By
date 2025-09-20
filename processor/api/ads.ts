import { BibTeXEntry } from "../bibtex";

export class AdsProcessor {
    async getReferences(entry: BibTeXEntry): Promise<BibTeXEntry[]> {
        return [];
    }

    async fillBibTeX(entry: BibTeXEntry): Promise<BibTeXEntry> {
        return entry;
    }
}
