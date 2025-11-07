declare module '@retorquere/bibtex-parser' {
    export interface Author {
        firstName?: string;
        lastName?: string;
    }

    export interface BibTeXField {
        [key: string]: any;
        author?: Author[];
        title?: string;
        year?: string;
    }

    export interface BibTeXEntryData {
        key: string;
        type: string;
        fields: BibTeXField;
    }

    export interface ParseResult {
        entries: BibTeXEntryData[];
        errors: any[];
    }

    export function parse(bibtex: string): ParseResult;
}
