import SwingBy from './main';

import { App, PluginSettingTab, Setting } from 'obsidian';

const modelOptions = [
    { name: 'Gemini 2.5 Flash', value: 'gemini/gemini-2.5-flash' },
    { name: 'Gemini 2.5 Flash-Lite Preview', value: 'gemini/gemini-2.5-flash-lite-preview-06-17' },
    { name: 'Gemini 2.0 Flash', value: 'gemini/gemini-2.0-flash' },
    { name: 'Gemini 2.0 Flash-Lite', value: 'gemini/gemini-2.0-flash-lite' },
    { name: 'Gemini 1.5 Flash', value: 'gemini/gemini-1.5-flash' },
    { name: 'Gemini 1.5 Pro', value: 'gemini/gemini-1.5-pro' },
    { name: 'OpenAI GPT-4.1-nano', value: 'openai/gpt-4.1-nano' },
    { name: 'OpenAI GPT-4.1-mini', value: 'openai/gpt-4.1-mini' },
    { name: 'OpenAI GPT-4.1', value: 'openai/gpt-4.1' },
    { name: 'OpenAI GPT-4o', value: 'openai/gpt-4o' },
    { name: 'OpenAI GPT-4o mini', value: 'openai/gpt-4o-mini' },
    { name: 'OpenAi o4-mini', value: 'openai/o4-mini' },
    { name: 'OpenAi o3-mini', value: 'openai/o3-mini' },
    { name: 'OpenAi o3', value: 'openai/o3' },
    { name: 'OpenAI o1', value: 'openai/o1' },
    { name: 'Sonar Pro', value: 'pplx/sonar-pro' },
    { name: 'Sonar', value: 'pplx/sonar' },
];

// Article settings interface
export interface ArticleSettings {
    apiKeyADS: string;
}
// LLM settings interface
export interface LlmApiKeys {
    openai?: string;
    gemini?: string;
}
export interface Endpoint {
    openai: string;
}
export interface LlmSettings {
    selectedModel: string;
    apikeys: LlmApiKeys;
    endpoint: Endpoint;
}
// settings interface
export interface SwingBySettings {
    article: ArticleSettings;
    llm: LlmSettings;
}


export const DEFAULT_SETTINGS: SwingBySettings = {
    article: {
        apiKeyADS: '',
    },
    llm: {
        selectedModel: 'gemini/gemini-2.5-flash',
        apikeys: {
            openai: '',
            gemini: '',
        },
        endpoint: {
            openai: '',
        },
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