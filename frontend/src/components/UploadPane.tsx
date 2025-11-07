import React, { useRef, useState } from "react";
import Loader from "./Loader";

type Props = {
  onSubmitFile: (file: File) => Promise<void>;
  isLoading: boolean;
};

export default function UploadPane({ onSubmitFile, isLoading }: Props) {
  const fileRef = useRef<HTMLInputElement | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const file = fileRef.current?.files?.[0];
    if (!file) {
      setError("Please select a PDF file.");
      return;
    }
    if (file.type !== "application/pdf") {
      setError("Only PDF files are supported.");
      return;
    }
    try {
      await onSubmitFile(file);
    } catch (err: any) {
      setError(err?.message ?? "Upload failed");
    }
  };

  return (
    <div className="upload-pane">
      <h2>Upload Pitch Deck (PDF)</h2>
      <p>Choose a PDF pitch deck to ingest into the system.</p>
      <form onSubmit={onUpload} className="upload-form">
        <input type="file" accept="application/pdf" ref={fileRef} />
        <button type="submit" disabled={isLoading}>
          Ingest
        </button>
      </form>
      {isLoading && <Loader label="Ingesting… This can take a few minutes." />}
      {error && <p className="error">{error}</p>}
    </div>
  );
}