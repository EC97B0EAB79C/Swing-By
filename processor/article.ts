import { BibTeXEntry } from "./bibtex";
import { ArxivProcessor } from "./api/arxiv";
import { CrossRefProcessor } from "./api/crossref";

export class ArticleProcessor {
    private arxivProcessor = new ArxivProcessor();
    private crossRefProcessor = new CrossRefProcessor();

    async getReferences(entry: BibTeXEntry): Promise<BibTeXEntry[]> {
        // TODO remove test code
        const arxivResult = this.arxivProcessor.sendRequest(entry);

        const crossRefResult = this.crossRefProcessor.sendRequest(entry, true);

        console.log('Arxiv Result:', await arxivResult);
        console.log('CrossRef Result:', await crossRefResult);
        return [];
    }
}