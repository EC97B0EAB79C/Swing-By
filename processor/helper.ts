import { BibTeXEntry } from "./bibtex";
import levenshtein from "fast-levenshtein";

export class Helper {
    // ----------------------------- SB Key Generation -----------------------------
    generateSBKey(entry: BibTeXEntry): string {
        // Get author last name
        const author = this.getAuthor(entry.authors);
        let authorLastName = this.getLastName(author);
        authorLastName = this.formatEntry(authorLastName, 6);

        // Process year
        let year = entry.year || "";
        year = this.isDigit(year) ? year : ".";
        year = this.formatEntry(year, 4);

        // Process title
        const titleWords = this.clean(entry.title).split(/\s+/);
        const titleFirstWord = this.formatEntry(titleWords[0] || "", 6);
        const titleFirstChar = this.formatEntry(
            titleWords.map(word => word[0] || "").join(""),
            16
        );

        // Generate SB key
        const sbkey = `${authorLastName}${year}${titleFirstWord}${titleFirstChar}`;
        return sbkey;
    }

    // ----------------------------- BibTeX Helpers -----------------------------
    fetchMostRelevant(entries: BibTeXEntry[], title: string): BibTeXEntry | null {
        if (entries.length === 0) {
            return null;
        }

        const cleanedTitle = this.clean(title);
        let bestEntry: BibTeXEntry | null = null;
        let bestScore = Infinity;

        for (const entry of entries) {
            const entryTitle = this.clean(entry.title);
            const distance = levenshtein.get(cleanedTitle, entryTitle);
            if (distance < bestScore) {
                bestScore = distance;
                bestEntry = entry;
            }
        }

        return bestEntry;
    }

    mergeEntries(primary: BibTeXEntry, secondary: BibTeXEntry | null): BibTeXEntry {
        if (!secondary) {
            return primary;
        }
        if (!primary) {
            return secondary;
        }

        const merged: BibTeXEntry = { ...primary };

        for (const key in secondary) {
            if (
                (merged as any)[key] === undefined ||
                (Array.isArray((merged as any)[key]) && (merged as any)[key].length === 0) ||
                ((merged as any)[key] === "" && (secondary as any)[key] !== "")
            ) {
                (merged as any)[key] = (secondary as any)[key];
            } else if (Array.isArray((merged as any)[key]) && Array.isArray((secondary as any)[key])) {
                const combined = new Set([...(merged as any)[key], ...(secondary as any)[key]]);
                (merged as any)[key] = Array.from(combined);
            }
        }

        return merged;
    }

    // ----------------------------- Text Processing Helpers -----------------------------
    private getAuthor(authors: string[] | undefined): string {
        return authors && authors.length > 0 ? authors[0] : "";
    }

    private getLastName(author: string): string {
        const parts = author.split(',');
        return parts[0].trim();
    }

    private formatEntry(text: string, maxLength: number): string {
        text = text.toLowerCase();
        if (text.length > maxLength) {
            return text.substring(0, maxLength);
        }
        return text.padEnd(maxLength, '.');
    }

    private clean(text: string): string {
        return text
            .replace(/[^\w\s]/g, ' ')
            .replace(/\s+/g, ' ')
            .trim()
            .toLowerCase();
    }

    private isDigit(str: string): boolean {
        return /^\d+$/.test(str);
    }
}