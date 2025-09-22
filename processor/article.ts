import { BibTeXEntry } from "./bibtex";
import { ArxivProcessor } from "./api/arxiv";
import { CrossRefProcessor } from "./api/crossref";

export class ArticleProcessor {
    private arxivProcessor = new ArxivProcessor();
    private crossRefProcessor = new CrossRefProcessor();

    async getReferences(entry: BibTeXEntry): Promise<BibTeXEntry[]> {
        // TODO remove test code 
        const arxivResult = await this.arxivProcessor.fillEntry(entry);
        console.log('Arxiv Result:', arxivResult);

        const crossRefResult = await this.crossRefProcessor.fillEntry(entry);
        console.log('CrossRef Result:', crossRefResult);
        return [];
    }
}