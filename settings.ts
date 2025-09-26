import SwingBy from './main';

import { App, PluginSettingTab, Setting } from 'obsidian';

export interface ArticleSettings {
    apiKeyADS: string;
}

export interface SwingBySettings {
    article: ArticleSettings;
}

export const DEFAULT_SETTINGS: SwingBySettings = {
    article: {
        apiKeyADS: '',
    },
};

export class SwingBySettingsTab extends PluginSettingTab {
    plugin: SwingBy;

    constructor(app: App, plugin: SwingBy) {
        super(app, plugin);
        this.plugin = plugin;
    }

    display(): void {
        let { containerEl } = this;
        containerEl.empty();


        // ---- API Settings -----------------------------------------------------
        new Setting(containerEl)
            .setHeading()
            .setName('API Settings');

        // ADS API Key
        new Setting(containerEl)
            .setName('NASA ADS API Key')
            .setDesc('Enter your NASA ADS API Key here')
            .addText((text) =>
                text
                    .setPlaceholder('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
                    .setValue(this.plugin.settings.article.apiKeyADS)
                    .onChange(async (value) => {
                        this.plugin.settings.article.apiKeyADS = value;
                        await this.plugin.saveSettings();
                    })
            );

    }

}