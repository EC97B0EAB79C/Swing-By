import { Notice, Plugin } from 'obsidian';

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
            callback: async () => {
                new Notice('Processing note...');
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
            }
        });
    }
}