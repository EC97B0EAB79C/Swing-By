import { BibTeXEntry, References } from "./bibtex";
import { ArticleSettings } from "../settings";
import { Helper } from "./helper";
import { ArxivProcessor } from "./api/arxiv";
import { CrossRefProcessor } from "./api/crossref";
import { AdsProcessor } from "./api/ads";

export class ArticleProcessor {
    private helper = new Helper();

    private arxivProcessor = new ArxivProcessor();
    private crossRefProcessor = new CrossRefProcessor();
    private adsProcessor = new AdsProcessor();

    private settings: ArticleSettings;

    constructor(settings: ArticleSettings) {
        this.settings = settings;
        this.adsProcessor.setApiKey(this.settings.apiKeyADS);
    }

    async getReferences(entry: BibTeXEntry): Promise<[string[], { [key: string]: string[] }]> {
        console.info(`Fetching references for: ${entry.title}`);
        const crossRefResult = this.crossRefProcessor.sendRequest(entry, true);
        const adsResult = this.adsProcessor.sendRequest(entry, true);

        const adsReferences = this.generateSBKeys((await adsResult)?.references || []);
        const crossRefReferences = this.generateSBKeys((await crossRefResult)?.references || []);

        let mergedReferences: string[] = [];
        let mismatchReferences: { [key: string]: string[] } = {};
        if (!this.helper.sameStrings(entry?.title, (await adsResult)?.title)) {
            console.warn(`Title mismatch with ADS: ${entry.title}`);
            mismatchReferences.ads = await adsReferences;
        }
        else {
            mergedReferences = [...new Set([...mergedReferences, ...await adsReferences])];
        }

        if (!this.helper.sameStrings(entry?.title, (await crossRefResult)?.title)) {
            console.warn(`Title mismatch with CrossRef: ${entry.title}`);
            mismatchReferences.crossref = await crossRefReferences;
        }
        else {
            mergedReferences = [...new Set([...mergedReferences, ...await crossRefReferences])];
        }

        return [mergedReferences, mismatchReferences];
    }

    private async generateSBKeys(references: References[]): Promise<string[]> {
        const sbkeys: string[] = [];
        for (const ref of references) {
            const sbkey = await this.convertReferenceToSBKey(ref);
            if (sbkey) sbkeys.push(sbkey);
        }
        return sbkeys;
    }

    private async convertReferenceToSBKey(reference: References): Promise<string | null> {
        if (reference.sbkey) {
            return reference.sbkey;
        }
        if (reference.bibcode) {
            const entry = await this.adsProcessor.sendRequest({ bibcode: reference.bibcode } as References);
            if (entry && entry.sbkey) return entry.sbkey;
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