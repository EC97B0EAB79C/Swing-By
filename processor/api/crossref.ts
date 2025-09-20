import { BibTeXEntry } from "../bibtex";

export class CrossRefProcessor {
    async getReferences(entry: BibTeXEntry): Promise<BibTeXEntry[]> {
        return [];
    }

    async fillBibTeX(entry: BibTeXEntry): Promise<BibTeXEntry> {
        return entry;
    }
}
