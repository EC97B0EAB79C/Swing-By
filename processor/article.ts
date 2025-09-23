import { BibTeXEntry, References } from "./bibtex";
import { Helper } from "./helper";
import { ArxivProcessor } from "./api/arxiv";
import { CrossRefProcessor } from "./api/crossref";
import { AdsProcessor } from "./api/ads";

export class ArticleProcessor {
    private helper = new Helper();

    private arxivProcessor = new ArxivProcessor();
    private crossRefProcessor = new CrossRefProcessor();
    private adsProcessor = new AdsProcessor();

    async getReferences(entry: BibTeXEntry): Promise<BibTeXEntry[]> {
        // TODO remove test code
        const crossRefResult = this.crossRefProcessor.sendRequest(entry, true);
        const arxivResult = this.arxivProcessor.sendRequest(entry);
        const adsResult = this.adsProcessor.sendRequest(entry, true);

        const adsReferences = this.generateSBKeys((await adsResult)?.references || []);
        const crossRefReferences = this.generateSBKeys((await crossRefResult)?.references || []);

        console.log('ADS Result:', await adsResult);
        console.log('ADS References SBKeys:', await adsReferences);
        console.log('CrossRef Result:', await crossRefResult);
        console.log('CrossRef References SBKeys:', await crossRefReferences);

        return [];
    }

    private async generateSBKeys(references: References[]): Promise<string[]> {
        const sbkeys: string[] = [];
        for (const ref of references) {
            const sbkey = await this.convertRefrenceToSBKey(ref);
            if (sbkey) sbkeys.push(sbkey);
        }
        return sbkeys;
    }

    private async convertRefrenceToSBKey(reference: References): Promise<string | null> {
        if (reference.sbkey) {
            return reference.sbkey;
        }
        if (reference.bibcode) {
            const entry = await this.adsProcessor.sendRequest({ bibcode: reference.bibcode } as References);
            if (entry && entry.sbkey) {
                return entry.sbkey;
            }
        }
        return null;
    }
}