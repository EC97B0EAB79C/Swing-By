import { MarkdownFileInfo, MarkdownView, Notice, Plugin, Editor, Pos } from 'obsidian';

import { BibTeXProcessor } from './processor/bibtex';
import { ArticleProcessor } from './processor/article';
import { NoteContentProcessor } from './processor/content_processor';

export default class SwingBy extends Plugin {

    async onload() {

        const bibtexProcessor = new BibTeXProcessor(this);
        const articleProcessor = new ArticleProcessor();
        const noteContentProcessor = new NoteContentProcessor(this);

        // ---- Commands -----------------------------------------------------
        // this.addCommand({
        //     id: 'test',
        //     name: 'Test Command',
        //     hotkeys: [{ modifiers: ["Alt", "Shift"], key: 't' }],
        //     editorCallback: (editor: Editor, ctx: MarkdownView | MarkdownFileInfo) => {
        //         const view = ctx instanceof MarkdownView ? ctx : this.app.workspace.getActiveViewOfType(MarkdownView);
        //         if (!view) {
        //             new Notice('No active markdown view');
        //             return;
        //         }
        //         const file = this.app.workspace.getActiveFile();
        //         if (!file) {
        //             new Notice('No active file');
        //             return;
        //         }

        //         const metadata = this.app.metadataCache.getFileCache(file);
        //         console.log(metadata);

        //         let referenceSectionLocation: any | null = null;
        //         if (metadata && metadata.headings) {
        //             for (let i = metadata.headings.length - 1; i >= 0; i--) {
        //                 if (metadata.headings[i].heading.toLowerCase().includes("references")) {
        //                     referenceSectionLocation = metadata.headings[i].position
        //                     break;
        //                 }
        //             }
        //         }
        //     }
        // })

        this.addCommand({
            id: 'process-note',
            name: 'Process Note',
            hotkeys: [{ modifiers: ["Alt"], key: 's' }],
            editorCallback: async (editor: Editor, ctx: MarkdownView | MarkdownFileInfo) => {
                const view = ctx instanceof MarkdownView ? ctx : this.app.workspace.getActiveViewOfType(MarkdownView);
                if (!view) {
                    new Notice('No active markdown view');
                    return;
                }
                const file = this.app.workspace.getActiveFile();
                if (!file) {
                    new Notice('No active file');
                    return;
                }

                new Notice('Processing note...');
                const entry = await bibtexProcessor.parseBibTeX(file);
                if (!entry) {
                    new Notice('No valid BibTeX entry found');
                    return;
                }
                await noteContentProcessor.populateEntry(file, entry);
                new Notice('Extracted metadata from BibTeX entry');

                const references = await articleProcessor.getReferences(entry);
                await noteContentProcessor.appendReferences(file, references);
                new Notice('Appended references to the note');
            }
        });
    }
}