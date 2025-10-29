export interface MarkdownFile {
    id: string;        // file_id (without extension)
    filename: string;  // actual file name like "Company1.json"
    size: number;
    created: number;
    modified: number;
  }
  
  export interface IngestResponse {
    // Tailor to your backend response
    // Minimal assumption: it returns the new markdown id/name that was created
    id: string;       // e.g., "company-4.md"
    name: string;     // e.g., "Company 4 Markdown"
    message?: string; // optional status message
  }