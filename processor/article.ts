import { BibTeXEntry } from "./bibtex";
import { ArxivProcessor } from "./api/arxiv";

export class ArticleProcessor {
    private arxivProcessor = new ArxivProcessor();
    async getReferences(entry: BibTeXEntry): Promise<BibTeXEntry[]> {
        // Test code 
        return [await this.arxivProcessor.fillEntry(entry)];
    }
}