import type { ProcessLogger, SourceDocument } from "./types";

async function extractTextFromPdf(file: File) {
  const [{ GlobalWorkerOptions, getDocument }, { default: pdfWorker }] =
    await Promise.all([
      import("pdfjs-dist"),
      import("pdfjs-dist/build/pdf.worker.min.mjs?url"),
    ]);

  GlobalWorkerOptions.workerSrc = pdfWorker;

  const data = new Uint8Array(await file.arrayBuffer());
  const pdf = await getDocument({ data }).promise;
  const pages: string[] = [];

  for (let pageIndex = 1; pageIndex <= pdf.numPages; pageIndex += 1) {
    const page = await pdf.getPage(pageIndex);
    const content = await page.getTextContent();
    const text = content.items
      .map((item) => ("str" in item ? item.str : ""))
      .join(" ")
      .replace(/\s+/g, " ")
      .trim();

    if (text) {
      pages.push(text);
    }
  }

  return pages.join("\n");
}

export async function parseSourceFiles(
  files: File[],
  onStatus?: ProcessLogger,
): Promise<SourceDocument[]> {
  const documents: SourceDocument[] = [];

  for (const file of files) {
    const isPdf =
      file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
    const mode = isPdf ? "PDF" : "text";

    onStatus?.({
      stage: "ingest",
      message: `Reading ${file.name} as ${mode}.`,
    });

    let text = "";
    if (isPdf) {
      text = await extractTextFromPdf(file);
    } else {
      text = await file.text();
    }

    const normalizedLength = text.replace(/\s+/g, " ").trim().length;
    onStatus?.({
      stage: "ingest",
      tone: "success",
      message: `Loaded ${file.name} with ${normalizedLength.toLocaleString()} extracted characters.`,
    });

    documents.push({
      documentId: file.name,
      title: file.name,
      text,
      section: null,
    });
  }

  return documents;
}
