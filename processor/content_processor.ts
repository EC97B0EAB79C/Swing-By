import { Notice, TFile } from 'obsidian';

import SwingBy from '../main';
import { BibTeXEntry } from './bibtex';

export class NoteContentProcessor {
    plugin: SwingBy;

    constructor(plugin: SwingBy) {
        this.plugin = plugin;
    }

    // ---- Content Processing -----------------------------------------------------
    async populateEntry(file: TFile, entry: BibTeXEntry): Promise<void> {
        this.plugin.app.fileManager.processFrontMatter(file, (frontmatter) => {
            frontmatter["title"] = entry.title || frontmatter["title"];
            frontmatter["author"] = entry.authors || frontmatter["author"];
            frontmatter["year"] = entry.year || frontmatter["year"];

            frontmatter["key"] = entry.sbkey || frontmatter["key"];
        });
    }

    async appendReferences(file: TFile, references: string[]): Promise<void> {
        if (references.length === 0) {
            new Notice("No references to append.");
            return;
        }

        const links = references.map(ref => `[[${ref}]]`);

        this.plugin.app.fileManager.processFrontMatter(file, (frontmatter) => {
            const existingReferences = frontmatter["references"] || [];
            frontmatter["references"] = Array.from(new Set([...existingReferences, ...links]));
        });
    }
}