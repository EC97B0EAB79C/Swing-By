import { MarkdownFileInfo, MarkdownView, Notice, Plugin, Editor, Pos } from 'obsidian';

import { SwingBySettings, SwingBySettingsTab, DEFAULT_SETTINGS } from './settings';

import { MismatchModal } from './ui/mismatch_modal';

import { BibTeXProcessor } from './processor/bibtex';
import { ArticleProcessor } from './processor/article';
import { NoteContentProcessor } from './processor/content_processor';

export default class SwingBy extends Plugin {
    settings!: SwingBySettings;

    async onload() {
        await this.loadSettings();
        this.addSettingTab(new SwingBySettingsTab(this.app, this));

        const bibtexProcessor = new BibTeXProcessor(this);
        const articleProcessor = new ArticleProcessor(this.settings.article);
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
                await noteContentProcessor.appendReferences(file, references[0]);

                console.log(references)
                if (Object.keys(references[1]).length > 0) {
                    new MismatchModal(this.app).open();
                }

                new Notice('Appended references to the note');
            }
        });
    }

    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() {
        await this.saveData(this.settings);
    }
}