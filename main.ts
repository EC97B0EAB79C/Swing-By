import { MarkdownFileInfo, MarkdownView, Notice, Plugin, Editor } from 'obsidian';

import { BibTeXProcessor } from './processor/bibtex';
import { NoteContentProcessor } from './processor/content_processor';

export default class SwingBy extends Plugin {

    async onload() {

        const bibtexProcessor = new BibTeXProcessor(this);
        const noteContentProcessor = new NoteContentProcessor(this);

        // ---- Commands -----------------------------------------------------
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

                const entry = await bibtexProcessor.parseBibTeX(file);
                if (!entry) {
                    new Notice('No valid BibTeX entry found');
                    return;
                }

                await noteContentProcessor.populateEntry(file, entry);

                // Test code
                const result = await noteContentProcessor.markdownToObject(editor.getValue());
                console.log(result);
                const markdown = await noteContentProcessor.objectToMarkdown(result);
                console.log(markdown);
            }
        });
    }
}