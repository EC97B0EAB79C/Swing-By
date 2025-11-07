import { App, Modal, Setting } from 'obsidian';

export class MismatchModal extends Modal {
    constructor(app: App) {
        super(app);
        this.setTitle('Swing By Mismatch Handler');
        this.setContent("Mismatch detected.");

        new Setting(this.contentEl)
            .addButton((btn) =>
                btn
                    .setButtonText('OK')
                    .setCta()
                    .onClick(() => {
                        this.close();
                    })
            );
    }
}
