import { BibTeXEntry } from "../bibtex";

export class ArxivProcessor {
    async getReferences(entry: BibTeXEntry): Promise<BibTeXEntry[]> {
        return [];
    }

    async fillBibTeX(entry: BibTeXEntry): Promise<BibTeXEntry> {
        return entry;
    }
}
