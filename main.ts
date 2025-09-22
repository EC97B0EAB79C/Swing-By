import { Notice, Plugin } from 'obsidian';

import { BibTeXProcessor } from './processor/bibtex';

export default class SwingBy extends Plugin {

    async onload() {

        const bibtexProcessor = new BibTeXProcessor(this);

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

                // TODO remove test code
                const test = await bibtexProcessor.processBibTeX(file);
                console.log(test);
            }
        });
    }
}