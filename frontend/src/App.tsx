import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import MarkdownViewer from "./components/MarkdownViewer";
import UploadPane from "./components/UploadPane";
import ChatInput from "./components/ChatInput";
import { getMarkdownList, getMarkdownById, ingestPitchDeck } from "./api/markdown";
import type { MarkdownFile } from "./types";
import "./styles.css";

type MainView = { kind: "markdown"; id: string } | { kind: "upload" } | { kind: "empty" };

export default function App() {
  const [markdowns, setMarkdowns] = useState<MarkdownFile[]>([]);
  const [mainView, setMainView] = useState<MainView>({ kind: "empty" });
  const [content, setContent] = useState<string>("# Welcome\nSelect a markdown from the left, or upload a pitch deck.");
  const [isIngesting, setIsIngesting] = useState(false);

  // initial load of list
  useEffect(() => {
    refreshList();
  }, []);

  async function refreshList(selectFirstIfNone = false) {
    const list = await getMarkdownList();
    setMarkdowns(list);
    if (selectFirstIfNone && list.length > 0) {
      selectMarkdown(list[0].id);
    }
  }

  async function selectMarkdown(id: string) {
    setMainView({ kind: "markdown", id });
    setContent("Loading markdown…");
    try {
      const response = await getMarkdownById(id);
      const data = typeof response === "string" ? JSON.parse(response) : response;
      const text = data.markdown;

      setContent(text);
    } catch (err: any) {
      setContent(`# Error\n\n${err?.message ?? "Failed to load markdown."}`);
    }
  }

  async function handleUpload(file: File) {
    setIsIngesting(true);
    try {
      const res = await ingestPitchDeck(file);
      // After success, refresh list so the new markdown shows up.
      await refreshList();
      // Optionally auto-open the new file
      if (res?.file_id && res?.markdown) {
        await selectMarkdown(res.final_md_id);
      }
      setMainView({ kind: "markdown", id: res?.file_id ?? "" });
    } catch (error) {
      console.error("Upload failed:", error);
    } finally {
      setIsIngesting(false);
    }
  }

  function handleShowUpload() {
    setMainView({ kind: "upload" });
    setContent(`# Upload a Pitch Deck\nUse the form to send a PDF to /ingest.`);
  }

  function handleSendChat(text: string) {
    // Hook up to your research assistant endpoint later
    console.log("Ask Research Assistant:", text);
  }

  return (
    <div className="app-container">
      <Sidebar
        markdownList={markdowns}
        selectedId={mainView.kind === "markdown" ? mainView.id : undefined}
        onSelectMarkdown={selectMarkdown}
        onShowUpload={handleShowUpload}
      />

      <div className="main-content">
        {mainView.kind === "upload" ? (
          <UploadPane onSubmitFile={handleUpload} isLoading={isIngesting} />
        ) : (
          <MarkdownViewer content={content} />
        )}
        <ChatInput onSend={handleSendChat} />
      </div>
    </div>
  );
}