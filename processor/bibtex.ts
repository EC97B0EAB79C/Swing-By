import SwingBy from '../main';
import { Helper } from './helper';
import { ArticleProcessor } from './article';

import { Notice, TFile } from 'obsidian';
import { parse } from '@retorquere/bibtex-parser';

export interface BibTeXEntry {
    // Article fields
    title: string;
    authors?: string[];
    year?: string;
    citationKey?: string;
    // Key fields
    sbkey?: string;
    arxivId?: string;
    doi?: string[];
    // Additional fields
    summary?: string;
}

export class BibTeXProcessor {
    private helper = new Helper();
    private articleProcessor = new ArticleProcessor();
    plugin: SwingBy;

    constructor(plugin: SwingBy) {
        this.plugin = plugin;
    }

    async processBibTeX(file: TFile): Promise<void> {
        const content = await this.plugin.app.vault.read(file);

        const entry = this.extractEntries(content, 'bibtex')
        if (!entry) {
            new Notice('No valid BibTeX entry found');
            return;
        }

        entry.sbkey = this.helper.generateSBKey(entry);
        console.log('Extracted BibTeX Entry:', entry);

        await this.populateFrontmatterWithEntry(file, entry);

        const references = await this.articleProcessor.getReferences(entry);
        console.log('Extracted References:', references);
    }

    extractEntries(markdownString: string, lang: string): BibTeXEntry | null {
        const regex = /```([a-zA-Z0-9-]+)?\n([\s\S]*?)\n```/g;
        let match;
        let blocks: string[] = [];

        while ((match = regex.exec(markdownString)) !== null) {
            if (match[1] && match[1].toLowerCase() === lang.toLowerCase()) {
                blocks.push(match[2].trim());
            }
        }

        if (blocks.length === 0) {
            return null;
        }

        const entries = parse(blocks.join('\n\n'));
        if (entries.errors.length > 0 || entries.entries.length === 0) {
            return null;
        }

        const entry = entries.entries[0].fields;
        const authors = entry["author"]?.map((author: any) =>
            `${author["lastName"]}, ${author["firstName"]}`
        ) || [];

        const entryMap: BibTeXEntry = {
            citationKey: entry.citationKey || "",
            title: entry.title || "",
            authors: authors,
            year: entry.year || "",
        };
        return entryMap;
    }

    async populateFrontmatterWithEntry(file: TFile, entry: any): Promise<void> {
        this.plugin.app.fileManager.processFrontMatter(file, (frontmatter) => {
            frontmatter["title"] = entry.title || frontmatter["title"];
            frontmatter["author"] = entry.authors || frontmatter["author"];
            frontmatter["year"] = entry.year || frontmatter["year"];

            frontmatter["key"] = entry.sbkey || frontmatter["key"];
        });
    }
}