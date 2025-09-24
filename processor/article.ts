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

    async getReferences(entry: BibTeXEntry): Promise<string[]> {
        const crossRefResult = this.crossRefProcessor.sendRequest(entry, true);
        const adsResult = this.adsProcessor.sendRequest(entry, true);

        const adsReferences = await this.generateSBKeys((await adsResult)?.references || []);
        const crossRefReferences = await this.generateSBKeys((await crossRefResult)?.references || []);

        const mergedReferences = [...new Set([...adsReferences, ...crossRefReferences])];
        return mergedReferences;
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
        if (reference.doi) {
            const entryByArxiv = await this.arxivProcessor.sendRequest(reference.doi);
            if (entryByArxiv && entryByArxiv.sbkey) return entryByArxiv.sbkey;

            const entryByAds = await this.adsProcessor.sendRequest({ doi: reference.doi } as References);
            if (entryByAds && entryByAds.sbkey) return entryByAds.sbkey;

            const entryByCrossRef = await this.crossRefProcessor.sendRequest(reference.doi);
            if (entryByCrossRef && entryByCrossRef.sbkey) return entryByCrossRef.sbkey;
        }

        return null;
    }
}