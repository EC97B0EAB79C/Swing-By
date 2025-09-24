import { Notice, TFile } from 'obsidian';

import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkStringify from 'remark-stringify';
import { Root } from 'mdast';


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

    markdownToObject(markdown: string): Root {
        const processor = unified().use(remarkParse);
        const ast = processor.parse(markdown);
        return ast;
    }

    objectToMarkdown(tree: Root): string {
        const processor = unified().use(remarkStringify);
        const markdownText = processor.stringify(tree);
        return markdownText;
    }



    // ---- Helpers -----------------------------------------------------
    private generateReferenceList(references: string[], level: number = 2): string {
        let list = references.map(ref => `- [[${ref}]]`).join('\n')
        list = `\n\n${"#".repeat(level)} References\n` + list + "\n";
        return list
    }
}