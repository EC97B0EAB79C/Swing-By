import { Notice, Plugin } from 'obsidian';

export default class MyPlugin extends Plugin {

    async onload() {
        this.addRibbonIcon('dice', 'Test', () => {
            new Notice('Hello, world!');
        });
    }
}