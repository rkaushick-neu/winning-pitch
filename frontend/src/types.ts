export interface MarkdownFile {
    id: string;        // file_id (without extension)
    filename: string;  // actual file name like "Company1.json"
    size: number;
    created: number;
    modified: number;
  }
  
  export interface IngestResponse {
    file_id: string;
    message: string;
    markdown: string;
    ocr_path: string;
    captioned_path: string;
    final_md_id: string;
  }