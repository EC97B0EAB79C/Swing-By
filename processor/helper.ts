import { BibTeXEntry } from "./bibtex";

export class Helper {
    generateSBKey(entry: BibTeXEntry): string {
        // Get author last name
        const author = this.getAuthor(entry.authors);
        let authorLastName = this.getLastName(author);
        authorLastName = this.formatEntry(authorLastName, 6);

        // Process year
        let year = entry.year;
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

    private getAuthor(authors: string[]): string {
        // Get the first author, or empty string if no authors
        return authors.length > 0 ? authors[0] : "";
    }

    private getLastName(author: string): string {
        // Assuming author format is "LastName, FirstName" or just "LastName"
        const parts = author.split(',');
        return parts[0].trim();
    }

    private formatEntry(text: string, maxLength: number): string {
        // Truncate or pad the text to the specified length
        if (text.length > maxLength) {
            return text.substring(0, maxLength);
        }
        return text.padEnd(maxLength, ' ');
    }

    private clean(text: string): string {
        // Clean the text by removing special characters and normalizing whitespace
        return text
            .replace(/[^\w\s]/g, ' ') // Replace non-word characters with spaces
            .replace(/\s+/g, ' ')     // Replace multiple spaces with single space
            .trim()
            .toLowerCase();
    }

    private isDigit(str: string): boolean {
        // Check if string contains only digits
        return /^\d+$/.test(str);
    }
}