import type { MarkdownFile } from "../types";

type Props = {
  markdownList: MarkdownFile[];
  selectedId?: string;
  onSelectMarkdown: (id: string) => void;
  onShowUpload: () => void;
};

export default function Sidebar({
  markdownList,
  selectedId,
  onSelectMarkdown,
  onShowUpload
}: Props) {
  return (
    <aside className="sidebar">
      <h3>Upload Pitch Deck</h3>
      <button className="upload-btn" onClick={onShowUpload}>
        Upload PDF
      </button>

      <h3 style={{ marginTop: 24 }}>Markdown</h3>
      <ul className="md-list">
        {markdownList.map((m) => (
          <li
            key={m.id}
            className={m.id === selectedId ? "selected" : ""}
            onClick={() => onSelectMarkdown(m.id)}
            title={m.filename}
          >
            {m.filename}
          </li>
        ))}
      </ul>
    </aside>
  );
}